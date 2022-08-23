class OptException(Exception):

    def __init__(self, error_code, params):
        """
        Creates a new OptScale exception

        :type error_code: Enum
        :type params: list
        """
        reason = error_code.value[0]
        reason = reason % tuple(params)
        super().__init__(reason)
        self.reason = reason
        self.err_code = error_code
        self.error_code = error_code.name
        self.params = params


class InvalidModelTypeException(OptException):
    pass


class HeraldException(OptException):
    pass


class WrongArgumentsException(OptException):
    pass


class NotFoundException(OptException):
    pass


class ConflictException(OptException):
    pass


class UnauthorizedException(OptException):
    pass


class ForbiddenException(OptException):
    pass


class FailedDependency(OptException):
    pass


class TimeoutException(OptException):
    pass


class InternalServerError(OptException):
    pass