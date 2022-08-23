import enum


class Err(enum.Enum):
    OKA0001 = [
        "Invalid db type: %s",
    ]
    OKA0002 = [
        "Recipient %s in scope %s already exists",
    ]
    OKA0003 = [
        "Report %s(%s) exists",
    ]
    OKA0004 = [
        "%s %s does not exist",
    ]
    OKA0005 = [
        "Report %s is already scheduled for recipient %s with rule %s",
    ]
    OKA0006 = [
        "Incorrect crontab %s",
    ]
    OKA0007 = [
        "Not found",
    ]
    OKA0008 = [
        "%s method not allowed",
    ]
    OKA0009 = [
        "Incorrect request body received",
    ]
    OKA0010 = [
        "Bad secret",
    ]
    OKA0011 = [
        "This resource requires authorization",
    ]
    OKA0012 = [
        "Unexpected parameters: %s",
    ]
    OKA0013 = [
        "%s %s not found",
    ]
    OKA0014 = [
        "Method not allowed",
    ]
    OKA0016 = [
        "Incorrect meta format",
    ]
    OKA0017 = [
        "Database error: %s",
    ]
    OKA0018 = [
        "Incorrect result format",
    ]
    OKA0019 = [
        "Parameter \"%s\" is immutable",
    ]
    OKA0020 = [
        "%s should be a list",
    ]
    OKA0021 = [
        "%s is not provided",
    ]
    OKA0022 = [
        "Incorrect task state %s",
    ]
    OKA0023 = [
        "role_purpose or user_id not provided",
    ]
    OKA0024 = [
        "role_purpose or user_id required",
    ]
    OKA0025 = [
        "Invalid %s",
    ]
    OKA0026 = [
        "%s should be true or false",
    ]
