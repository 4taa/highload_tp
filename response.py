from headersResponse import headers
from statusLine import statusLine

__all__ = (
    'response',
)


class response:
    DEFAULT_READ_CHUNK_SIZE = 1024

    def __init__(self, status_code, header_pairs):
        self.statusLine = statusLine(statusCode)
        self.headers = headers(headerPairs)

    def __str__(self):
        return '{}\r\n{}\r\n'.format(str(self.statusLine), str(self.headers))