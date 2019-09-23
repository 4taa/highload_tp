__all__ = (
    'statusLine',
)


def getReasonPhraseByCode(statusCode):
    if statusCode == 200:
        return 'OK'
    elif statusCode == 400:
        return 'Bad_Request'
    elif statusCode == 403:
        return 'Forbidden'
    elif statusCode == 404:
        return 'Not Found'
    elif statusCode == 405:
        return 'Method Not Allowed'
    else:
        return ''


class statusLine:
    HTTP_VERSION = '1.1'

    def __init__(self, statusCode):
        self.statusCode = statusCode

    def __str__(self):
        reasonPhrase = getReasonPhraseByCode(self.statusCode)
        return 'HTTP/{} {} {}'.format(self.HTTP_VERSION, self.statusCode, reasonPhrase)

    def __repr__(self):
        reasonPhrase = getReasonPhraseByCode(self.statusCode)
        return 'Status line: HTTP/{} {} {}'.format(self.HTTP_VERSION, self.statusCode, reasonPhrase)