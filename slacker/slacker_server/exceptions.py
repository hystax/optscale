import enum


class Err(enum.Enum):
    OS0001 = [
        "Invalid db type: %s",
    ]
    OS0002 = [
        "Not found",
    ]
    OS0003 = [
        "%s method not allowed",
    ]
    OS0004 = [
        "Incorrect request body received",
    ]
    OS0005 = [
        "Bad secret",
    ]
    OS0006 = [
        "This resource requires authorization",
    ]
    OS0007 = [
        "Unexpected parameters: %s",
    ]
    OS0008 = [
        "%s %s not found",
    ]
    OS0009 = [
        "Database error: %s",
    ]
    OS0010 = [
        "%s is not provided",
    ]
    OS0011 = [
        "Invalid %s value",
    ]
    OS0012 = [
        "Duplicate path parameters in the request body: %s",
        ["organization_id"],
        ["Duplicate path parameters in the request body: organization_id"]
    ]
    OS0013 = [
        'Slack user already connected'
    ]
    OS0014 = [
        "%s or %s should be provided",
        ["channel_id", "auth_user_id"],
        ["channel_id or auth_user_id should be provided"]
    ]
    OS0015 = [
        "%s and %s could not be provided at the same time",
        ["channel_id", "auth_user_id"],
        ["channel_id and auth_user_id could not be provided at the same time"]
    ]
    OS0016 = [
        "User with %s %s were not found",
        ["auth_user_id", "02430e6b-6975-4535-8bc6-7a7b52938014"],
        ["User with auth_user_id 02430e6b-6975-4535-8bc6-7a7b52938014 were not found"]
    ]
    OS0017 = [
        "%s should provide only with %s",
        ["channel_id", "team_id"],
        ["channel_id should provide only with team_id"]
    ]
    OS0018 = [
        "Unauthorized",
    ]
    OS0019 = [
        "Target slack channel %s is archived",
        ['channel_id'],
        ['Target slack channel FFFFFFFFF is archived']
    ]
