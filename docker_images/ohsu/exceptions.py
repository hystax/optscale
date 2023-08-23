import enum


class Err(enum.Enum):
    OHE0001 = [
        "Not found",
        [],
        []
    ]
    OHE0002 = [
        "%s method not allowed",
        ["Method name"],
        ["POST"]
    ]
    OHE0003 = [
        "Incorrect request body received",
        [],
        []
    ]
    OHE0004 = [
        "Invalid %s",
        ["parameter"],
        ["organization_id"]
    ]
    OHE0005 = [
        "%s is not provided",
        ["parameter"],
        ["app_id"]
    ]
