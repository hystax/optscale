class CloudAdapterBaseException(Exception):
    pass


class ResourceNotFound(CloudAdapterBaseException):
    pass


class RegionNotFoundException(ResourceNotFound):
    pass


class PricingNotFoundException(ResourceNotFound):
    pass


class AuthorizationException(CloudAdapterBaseException):
    pass


class InvalidParameterException(CloudAdapterBaseException):
    pass


class ReportConfigurationException(CloudAdapterBaseException):
    pass


class ReportFilesNotFoundException(CloudAdapterBaseException):
    pass


class CloudSettingNotSupported(CloudAdapterBaseException):
    pass


class BucketNotFoundException(CloudAdapterBaseException):
    pass


class BucketNameValidationError(CloudAdapterBaseException):
    pass


class ReportNameValidationError(CloudAdapterBaseException):
    pass


class BucketPrefixValidationError(CloudAdapterBaseException):
    pass


class CloudConnectionError(CloudAdapterBaseException):
    pass


class ConnectionTimeout(CloudAdapterBaseException):
    pass


class S3ConnectionError(CloudAdapterBaseException):
    pass


class InvalidResourceTypeException(CloudAdapterBaseException):
    pass


class MetricsNotFoundException(ResourceNotFound):
    pass


class MetricsServerTimeoutException(ResourceNotFound):
    pass


class InvalidResourceStateException(CloudAdapterBaseException):
    pass


class ForbiddenException(CloudAdapterBaseException):
    pass
