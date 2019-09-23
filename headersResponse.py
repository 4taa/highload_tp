  
from collections import OrderedDict

__all__ = (
    'headers',
)


class headers(OrderedDict):
    KEY_VALUE_DELIMITER = ': '
    HEADER_DELIMITER = '\r\n'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.join()

    def __repr__(self):
        return 'Headers: {}'.format(self.join())

    def join(self):
        headers = ['{}{}{}'.format(k, self.KEY_VALUE_DELIMITER, v) for k, v in self.items()]
        return self.HEADER_DELIMITER.join(headers) + self.HEADER_DELIMITER