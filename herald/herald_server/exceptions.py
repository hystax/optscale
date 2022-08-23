import enum


class Err(enum.Enum):
    G0002 = [
        "item %s not found",
    ]

    G0003 = [
        "Forbidden",
    ]

    G0004 = [
        "Unauthorized",
    ]

    G0005 = [
        "This resource requires authorization",
    ]

    G0006 = [
        "Bad secret",
    ]

    G0007 = [
        "Incorrect request body received",
    ]

    G0008 = [
        "%s method not allowed",
    ]

    G0009 = [
        "parameter \"%s\" is immutable",
    ]

    G0010 = [
        "Unexpected parameters: %s",
    ]

    G0011 = [
        "Non unique parameters in get request",
    ]

    G0012 = [
        "reactions has invalid format",
    ]

    G0013 = [
        "criteria \"%s\" does not match format key:value",
    ]

    G0014 = [
        "invalid field name %s",
    ]

    G0015 = [
        "type is required for reaction",
    ]

    G0016 = [
        "\"payload\" should be a string with valid JSON",
    ]

    G0023 = [
        "invalid value for reaction type - %s",
    ]

    G0025 = [
        "%s is not provided",
    ]

    G0026 = [
        "invalid %s",
    ]

    G0027 = [
        "Database error: %s",
    ]

    G0028 = [
        "Bad request: %s",
    ]
