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
            now = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

            print('{} - {} request'.format(addr, now))

            self.loop.create_task(self.request(client, addr))
    
    async def request(self, client, addr):
        request = await self.asyncRead(client)

        now = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

        if not self.reqParser(request):
            print('request: "{}"'.format(request))
            print('{} - {} parse error'.format(addr, now))
            response = Response(400, setHeaders())
            await self.asyncWrite(client, response)
            client.close()
            return

        if self.reqParser.requestLine.method not in self.ALLOWED_METHODS:
            print('{} - {} depricated method'.format(addr, now))
            response = Response(405, setHeaders())
            await self.asyncWrite(client, response)
            client.close()
            return

        pathToFile = os.path.abspath(os.path.join(self.document_root, self.reqParser.requestLine.path))
        pathToFile = unquote(pathToFile)

        incorrectFile = (not pathToFile.endswith('/')) and self.reqParser.requestLine.path.endswith('/')

        if self.document_root not in pathToFile:
            print('{} - {} incorrect path'.format(addr, now))
            response = Response(403, setHeaders())
            await self.asyncWrite(client, response)
            client.close()
            return

        isAdded = False

        if os.path.isdir(pathToFile):
            isAdded = True
            pathToFile = os.path.join(pathToFile, self.reqParser.requestLine.INDEX_FILE_NAME)

        if not os.path.exists(pathToFile):
            print('{} - {} FILE PATH DOES NOT EXIST {}'.format(addr, now, pathToFile))

            if isAdded:
                response = Response(403, setHeaders())
            else:
                response = Response(404, setHeaders())

            await self.asyncWrite(client, response)
        else:
            if incorrectFile and not isAdded:
                print('{} - {} FILE PATH WITH TERMINATING SLASH {}'.format(addr, now, pathToFile))
                response = Response(404, setHeaders())
                await self.asyncWrite(client, response)
            else:
                print('{} - {} OK'.format(addr, now))

                headers = setHeaders()
                headers.append(('Content-Length', str(os.path.getsize(pathToFile))))
                mimeType, _ = mimetypes.guess_type(pathToFile)
                headers.append(('Content-Type', mimeType))

                response = Response(200, headers)

                if self.reqParser.requestLine.method == 'HEAD':
                    await self.asyncWrite(client, response)
                else:
                    with open(pathToFile, 'rb') as fp:
                        await self.asyncWrite(client, response, fp)

        client.close()
    
    async def asyncRead(self, client):
        return (await self.loop.sock_recv(client, self.SOCKET_BUFFER_SIZE)).decode('utf-8')

    async def asyncWrite(self, client, response, fp=None):
        await self.loop.sock_sendall(client, str(response).encode('utf-8'))

        if fp is not None:
            while True:
                line = fp.read(self.SOCKET_BUFFER_SIZE)

                if not line:
                    return

                await self.loop.sock_sendall(client, line)


if __name__ == '__main__':
    sock = createConnetion('localhost', 8001)
    worker = createWorker(sock, '/tmp')

    try:
        worker.pause()
    except KeyboardInterrupt:
        sock.close()