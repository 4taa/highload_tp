import logging

from multiprocessing import Process

from config import createParser
from configFile import configFile

from connections import createConnetion
from connections import createWorker

def workerWrap(sock, document_root):
    worker = createWorker(sock, document_root)
    worker.pause()

def main():
    processes = []

    logging.basicConfig(level=logging.ERROR)

    configParser = createParser()
    localConfig = configParser.parse_args()

    if localConfig.config_file:
        num_workers = configFile(localConfig.config_file).num_workers
        port = configFile(localConfig.config_file).port
        host = configFile(localConfig.config_file).host
        document_root = configFile(localConfig.config_file).document_root
    else: 
        num_workers = localConfig.num_workers
        port = localConfig.port
        host = localConfig.host
        document_root = localConfig.document_root

    socket = createConnetion(host, port)

    try:
        for numProcess in range(num_workers):
            currentProcess = Process(target=workerWrap, args=(socket, document_root))
            processes.append(currentProcess)
            currentProcess.start()

        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for numProcess, process in enumerate(processes):
            process.terminate()
        socket.close()

if __name__ == '__main__':
    main()