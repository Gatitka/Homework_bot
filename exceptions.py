class RequestExceptionError(Exception):
    """Класс исключения при request exception."""
    def __init__(self, message='Проблема с ответом сервера'):
        self.message = message

    def __str__(self):
        return f'{self.message}'
