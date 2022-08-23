import enum


class Err(enum.Enum):
    OJ0001 = [
        "Invalid db type: %s",
    ]
    OJ0002 = [
        "Not found",
    ]
    OJ0003 = [
        "%s method not allowed",
    ]
    OJ0004 = [
        "Incorrect request body received",
    ]
    OJ0005 = [
        "Bad secret",
    ]
    OJ0006 = [
        "This resource requires authorization",
    ]
    OJ0007 = [
        "Unexpected parameters: %s",
    ]
    OJ0008 = [
        "%s %s not found",
    ]
    OJ0009 = [
        "Database error: %s",
    ]
    OJ0010 = [
        "%s is not provided",
    ]
    OJ0011 = [
        "Invalid %s value",
    ]
    OJ0012 = [
        "Unauthorized",
    ]
    OJ0013 = [
        "Invalid payload"
    ]
    OJ0014 = [
        "App is not installed for tenant %s"
    ]
    OJ0015 = [
        "Failed to contact Atlassian public key server: %s"
    ]
    OJ0016 = [
        "This API must be called in user context"
    ]
    OJ0017 = [
        "%s not found",
    ],
    OJ0018 = [
        "Forbidden",
    ]
    OJ0019 = [
        "Organization is not assigned for tenant %s",
    ]
    OJ0020 = [
        "Service call error: %s"
    ]
    OJ0021 = [
        "OptScale user is not assigned for account ID %s",
    ]
    OJ0022 = [
        "This API must be called in Jira issue context"
    ]
    OJ0023 = [
        "Atlassian API server query failure: %s"
    ]
    OJ0024 = [
        "Invalid hook payload: %s"
    ]
    OJ0025 = [
        "Suitable existing booking was not found"
    ]
