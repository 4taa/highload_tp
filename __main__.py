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

    configParser = createParser()
    localConfig = configParser.parse_args()

    print(localConfig)

    if localConfig.config_file:
        print('Setting parsed config')
        num_workers = ConfigFileParser(args.config_file).num_workers
        port = ConfigFileParser(args.config_file).port
        host = ConfigFileParser(args.config_file).host
        document_root = ConfigFileParser(args.config_file).document_root
    else: 
        print('Setting default config')
        num_workers = localConfig.num_workers
        port = localConfig.port
        host = localConfig.host
        document_root = localConfig.document_root

    print('type = ', type(port));
    socket = createConnetion(host, port)

    try:
        for numProcess in range(num_workers):
            print('{} started'.format(numProcess))
            currentProcess = Process(target=workerWrap, args=(socket, document_root))
            processes.append(currentProcess)
            currentProcess.start()

        for process in processes:
            process.join()
    except KeyboardInterrupt:
        for numProcess, process in enumerate(processes):
            print('{} stopped'.format(numProcess))
            process.terminate()
        socket.close()

if __name__ == '__main__':
    main()