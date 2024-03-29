import asyncio
import mimetypes
import os
import socket
from datetime import datetime
from urllib.parse import unquote

import uvloop

from response import Response
from request import requestParser

__all__ = (
    'createConnetion',
    'createWorker',
)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def createConnetion(host, port, backlog=8):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.bind((host, port))
    conn.listen(backlog)
    conn.setblocking(False)
    return conn


def setHeaders():
    today = datetime.utcnow()
    return [
        ('Date', today.strftime('%a, %d %b %Y %H:%M:%S GMT')),
        ('Server', 'Highload'),
        ('Connection', 'close'),
    ]


class createWorker:
    ALLOWED_METHODS = ('GET', 'HEAD')
    INDEX_FILE_NAME = 'index.html'
    SOCKET_BUFFER_SIZE = 1024

    def __init__(self, sock, document_root):
        self.document_root = os.path.abspath(document_root)
        self.reqParser = requestParser()

        self.socket = sock

        self.loop = None

    def pause(self):
        self.loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.asyncPause())
    
    async def asyncPause(self):
        while True:
            client, addr = await self.loop.sock_accept(self.socket)

            addr = ':'.join([str(part) for part in addr])

            self.loop.create_task(self.request(client, addr))
    
    async def request(self, client, addr):
        request = (await self.loop.sock_recv(client, self.SOCKET_BUFFER_SIZE)).decode('utf-8')

        if not self.reqParser(request):
            response = Response(400, setHeaders())
            await self.loop.sock_sendall(client, str(response).encode('utf-8'))
            await self.loop.sock_sendall(client, None)
            client.close()
            return

        if self.reqParser.requestLine.method not in self.ALLOWED_METHODS:
            response = Response(405, setHeaders())
            await self.loop.sock_sendall(client, str(response).encode('utf-8'))
            await self.loop.sock_sendall(client, None)
            client.close()
            return

        pathToFile = os.path.abspath(os.path.join(self.document_root, self.reqParser.requestLine.path))
        pathToFile = unquote(pathToFile)

        incorrectFile = (not pathToFile.endswith('/')) and self.reqParser.requestLine.path.endswith('/')

        if self.document_root not in pathToFile:
            response = Response(403, setHeaders())
            await self.loop.sock_sendall(client, str(response).encode('utf-8'))
            await self.loop.sock_sendall(client, None)
            client.close()
            return

        isAdded = False

        if os.path.isdir(pathToFile):
            isAdded = True
            pathToFile = os.path.join(pathToFile, self.reqParser.requestLine.INDEX_FILE_NAME)

        if not os.path.exists(pathToFile):
            if isAdded:
                response = Response(403, setHeaders())
            else:
                response = Response(404, setHeaders())

            await self.loop.sock_sendall(client, str(response).encode('utf-8'))
            await self.loop.sock_sendall(client, None)
        else:
            if incorrectFile and not isAdded:
                response = Response(404, setHeaders())

                await self.loop.sock_sendall(client, str(response).encode('utf-8'))
                await self.loop.sock_sendall(client, None)
            else:

                headers = setHeaders()
                headers.append(('Content-Length', str(os.path.getsize(pathToFile))))
                mimeType, _ = mimetypes.guess_type(pathToFile)
                headers.append(('Content-Type', mimeType))

                response = Response(200, headers)

                if self.reqParser.requestLine.method == 'HEAD':
                    await self.loop.sock_sendall(client, str(response).encode('utf-8'))
                    await self.loop.sock_sendall(client, None)
                else:
                    with open(pathToFile, 'rb') as fp:
                        await self.loop.sock_sendall(client, str(response).encode('utf-8'))
                        await self.loop.sock_sendall(client, fp.read(self.SOCKET_BUFFER_SIZE))

        client.close()

if __name__ == '__main__':
    sock = createConnetion('localhost', 8001)
    worker = createWorker(sock, '/tmp')

    try:
        worker.pause()
    except KeyboardInterrupt:
        sock.close()