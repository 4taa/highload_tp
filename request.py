from headers import headersParser
from requestLine import requestLineParser

__all__ = (
    'requestParser',
)


class requestParser:
    DELIMITER = '\r\n'

    def __init__(self):
        self.requestLine = requestLineParser()
        self.headers = headersParser()

    def __call__(self, http_request):
        if not http_request or not isinstance(http_request, str):
            return False

        split = http_request.split(self.DELIMITER * 2)

        if len(split) == 2:
            head, body = split
            return self.parseHead(head)
        else:
            return False

    def parseHead(self, rawHead):
        head = rawHead.split(self.DELIMITER)

        if len(head) > 1:
            request_line, *headers = head
            return self.requestLine(request_line) and self.headers(headers)
        elif len(head) == 1:
            return self.requestLine (*head)
        else:
            return False