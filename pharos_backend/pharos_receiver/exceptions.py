import enum


class Err(enum.Enum):
    ODE0001 = [
        "Not found",
        [],
        []
    ]
    ODE0002 = [
        "%s method not allowed",
        ["Method name"],
        ["POST"]
    ]
    ODE0003 = [
        "Incorrect request body received",
        [],
        []
    ]
    ODE0004 = [
        "Invalid %s",
        [],
        []
    ]
    ODE0005 = [
        "Forbidden",
        [],
        []
    ]
