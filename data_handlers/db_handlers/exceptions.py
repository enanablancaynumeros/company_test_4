class BaseException(Exception):
    pass


class ValidationException(BaseException):
    pass


class UnExistingDBEntityException(BaseException):
    pass
