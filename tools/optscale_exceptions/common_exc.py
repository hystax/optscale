import os


class OptException(Exception):

    def __init__(self, error_code, params):
        """
        Creates a new OptScale exception

        :type error_code: Enum
        :type params: list
        """
        params_ = []
        for param in params:
            if isinstance(param, str):
                params_.append(param.replace(os.linesep, ' '))
            else:
                params_.append(param)
        reason = error_code.value[0]
        reason = reason % tuple(params_)
        super().__init__(reason)
        self.reason = reason
        self.err_code = error_code
        self.error_code = error_code.name
        self.params = params_


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
