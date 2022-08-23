import enum


class Err(enum.Enum):
    OI0002 = [
        "Not found",
        [],
        []
    ]
    OI0003 = [
        "%s method not allowed",
        ["Method name"],
        ["POST"]
    ]
    OI0004 = [
        "Incorrect request body received",
        [],
        []
    ]
    OI0005 = [
        "Bad secret",
        [],
        []
    ]
    OI0006 = [
        "Unauthorized",
        [],
        []
    ]
    OI0007 = [
        "This resource requires authorization",
        [],
        []
    ]
    OI0008 = [
        "Invalid %s",
        [],
        []
    ]
    OI0009 = [
        "Discovery not found for cloud %s",
        [],
        []
    ]
    OI0010 = [
        "Cloud %s is not supported",
        [],
        []
    ]
    OI0011 = [
        "%s is not provided",
    ]
    OI0012 = [
        "Region %s is not available",
        ['Region name'],
        ['region-1']
    ]
    OI0013 = [
        "Resource type %s is not supported for cloud %s"
    ]
    OI0014 = [
        "Unexpected parameters: %s",
    ]
    OI0015 = [
        "Operating system %s is not available",
        ['Operating system'],
        ['ROSA Linux']
    ]
    OI0016 = [
        "Cloud %s does not support %s parameter"
    ]
    OI0017 = [
        "Unexpected response from cloud: %s"
    ]
    OI0018 = [
        "Invalid parameters error: %s"
    ]
