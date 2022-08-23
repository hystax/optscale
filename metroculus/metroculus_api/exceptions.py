import enum


class Err(enum.Enum):
    OM0002 = [
        "Not found",
        [],
        []
    ]
    OM0003 = [
        "%s method not allowed",
        ["Method name"],
        ["POST"]
    ]
    OM0004 = [
        "Incorrect request body received",
        [],
        []
    ]
    OM0005 = [
        "Bad secret",
        [],
        []
    ]
    OM0006 = [
        "Invalid %s",
        [],
        []
    ]
    OM0007 = [
        "This resource requires authorization",
        [],
        []
    ]
    OM0008 = [
        "%s is not provided",
    ]
