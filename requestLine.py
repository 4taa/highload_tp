import re

__all__ = (
    'requestLineParser',
)

class requestLineParser:
    ALLOWED_SCHEMAS = (None, 'http', 'https')
    INDEX_FILE_NAME = 'index.html'
    REQUEST_LINE_REGEX_PATTERN = r'^(?P<method>[A-Z]+) ((?P<scheme>\w+)://)?(?(3)[^/]*)/?(?P<path>[^\?#]*/?)?(\?[^#]*)?(\#.*)? HTTP/1.[0|1]$'

    def __init__(self):
        self.re = re.compile(self.REQUEST_LINE_REGEX_PATTERN)
        self.method = None
        self.path = None

    def __call__(self, requestLine):
        if not str or not isinstance(requestLine, str):
            return False

        match = self.re.match(requestLine)

        if not match or match.group('scheme') not in self.ALLOWED_SCHEMAS:
            return False

        self.method = match.group('method')

        if match.group('path') == '/':
            self.path = self.INDEX_FILE_NAME
        else:
            self.path = match.group('path') or self.INDEX_FILE_NAME

        return True