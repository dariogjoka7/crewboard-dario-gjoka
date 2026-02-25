class AppException(Exception):
    pass


class BadRequestException(AppException):
    def __init__(self, message: str):
        self.message = message


class NotFoundException(AppException):
    def __init__(self, message: str):
        self.message = message


class UnauthorizedException(AppException):
    def __init__(self, message: str):
        self.message = message


class InternalServerException(AppException):
    def __init__(self, message: str, error_id: str):
        self.message = message
        self.error_id = error_id


class DataValidationException(AppException):
    def __init__(self, message: str):
        self.message = message
