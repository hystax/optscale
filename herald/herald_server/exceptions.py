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

    G0019 = [
        "must provide email address in payload for reaction 'email'"
    ]

    G0022 = [
        "must provide phone number in payload for reaction 'sms'",
    ]

    G0023 = [
        "invalid value for reaction type - %s",
    ]

    G0024 = [
        "Invalid model type: %s",
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

    OE0004 = [
        "Type error: %s",
        ["Traceback when try to set wrong value for enum type"],
        ["'unexpected' is not a valid ConditionTypes"]
    ]

    OE0214 = [
        "%s should be a string",
        ["Field name"],
        ["name"]
    ]
    OE0215 = [
        "%s should contain %s characters",
        ["Filed name", "max count of chars or range"],
        ["name", "max 255"]
    ]

    OE0216 = [
        "%s is not provided",
        ["Field name"],
        ["business_unit_id"]
    ]

    OE0217 = [
        "Invalid %s",
        ["Field name"],
        ['filter_by']
    ]

    OE0218 = [
        "%s \"%s\" has incorrect format",
        ["Field name", "provided field value"],
        ["email", "wrong_email@com"]
    ]

    OE0219 = [
        "%s should be a string with valid JSON",
        ["Field name"],
        ["meta_info"]
    ]

    OE0223 = [
        "%s should be integer",
        ["Filed name"],
        ["limit"]
    ]
    OE0224 = [
        "Value of \"%s\" should be between %s and %s",
        ["Filed name", "min value", "max value"],
        ["limit", 0, 2147483647]
    ]

    OE0225 = [
        "%s is not valid fqdn or ip",
        ["Field name"],
        ["Address"]
    ]

    OE0226 = [
        "%s should be True or False",
        ["Field name"],
        ["Active"]
    ]
