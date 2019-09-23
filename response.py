from headersResponse import headers
from statusLine import statusLine

__all__ = (
    'Response',
)


class Response:
    DEFAULT_READ_CHUNK_SIZE = 1024

    def __init__(self, statusCode, headerPairs):
        self.statusLine = statusLine(statusCode)
        self.headers = headers(headerPairs)

    def __str__(self):
        return '{}\r\n{}\r\n'.format(str(self.statusLine), str(self.headers))