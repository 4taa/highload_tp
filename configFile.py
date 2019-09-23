import os
import re

__all__ = (
    'configFile',
)


def errorMessage(message):
    return 'Incorrect httpd.conf: {}.'.format(message)


class configFile:
    NUM_WORKERS = r'cpu_limit (?P<num_workers>\d+)'
    DOCUMENT_ROOT = r'document_root (?P<document_root>[^\s]+)'
    HOST = r'host (?P<host>[^\s]+)'
    PORT = r'port (?P<port>\d+)'

    def __init__(self, configFilePath):
        self.configFilePath = configFilePath
        self.numWorkersRegEx = re.compile(self.NUM_WORKERS)
        self.documentRootRegEx = re.compile(self.DOCUMENT_ROOT)
        self.hostRegEx = re.compile(self.HOST)
        self.portRegEx = re.compile(self.PORT)

        self.num_workers = None
        self.document_root = None
        self.host = None
        self.port = None

        self.parse()

    def parse(self):
        with open(self.configFilePath, 'r') as fp:
            data = fp.read()

            if not data:
                raise ValueError(errorMessage('Config file is empty'))

            match = self.numWorkersRegEx.search(data)

            if match:
                self.num_workers = int(match.group('num_workers'))
            else:
                raise ValueError(errorMessage('Number of workers param (cpu_limit) missing'))

            match = self.documentRootRegEx.search(data)

            if match:
                document_root = match.group('document_root')

                if not os.path.exists(document_root):
                    raise ValueError(errorMessage('Document root {} does not exist.'.format(document_root)))

                self.document_root = document_root
            else:
                raise ValueError(errorMessage('Document root param (document_root) missing'))

            match = self.hostRegEx.search(data)

            if match:
                self.host = match.group('host')
            else:
                self.host = '0.0.0.0'

            match = self.portRegEx.search(data)

            if match:
                print('kek')
                self.port = int(match.group('port'))
            else:
                self.port = 80