import enum


class Err(enum.Enum):

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
