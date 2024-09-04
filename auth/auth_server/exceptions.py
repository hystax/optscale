import enum


class Err(enum.Enum):
    OA0000 = [
        "Mock err code",
    ]
    OA0002 = [
        "Method not allowed",
    ]
    OA0003 = [
        "%s %s not found",
    ]
    OA0004 = [
        "User %s is not an owner of assignment %s",
    ]
    OA0005 = [
        "User %s does not exist",
    ]
    OA0006 = [
        "Bad secret",
    ]
    OA0007 = [
        "This resource requires authorization",
    ]
    OA0008 = [
        "Should provide user id and role id",
    ]
    OA0009 = [
        "Invalid action provided",
    ]
    OA0010 = [
        "Token not found",
    ]
    OA0011 = [
        "Invalid token",
    ]
    OA0012 = [
        "Forbidden!",
    ]
    OA0013 = [
        "Malformed payload",
    ]
    OA0014 = [
        "Actions should be non-empty list",
    ]
    OA0017 = [
        "Role with id %s not assignable to user %s",
    ]
    OA0018 = [
        "Scope of assignment should be not greater than user scope",
    ]
    OA0019 = [
        "Assignment with id %s not found",
    ]
    OA0020 = [
        "Invalid type %s",
    ]
    OA0021 = [
        "Parameter \"%s\" is immutable",
    ]
    OA0022 = [
        "Unexpected parameters: %s",
    ]
    OA0023 = [
        "Unauthorized",
    ]
    OA0024 = [
        "User %s was not found",
    ]
    OA0025 = [
        "Role %s was not found",
    ]
    OA0026 = [
        "Invalid type with id %s",
    ]
    OA0027 = [
        "Resource %s not found",
    ]
    # TODO replace item
    OA0028 = [
        "%s with id %s was not found",
    ]
    OA0029 = [
        "Non unique parameters in get request",
    ]
    OA0030 = [
        "Role %s was not found",
    ]
    OA0031 = [
        "%s is required",
    ]
    OA0032 = [
        "%s is not provided",
    ]
    OA0033 = [
        "%s should be a string",
    ]
    OA0034 = [
        "Cannot create role with given lvl for %s",
    ]
    OA0035 = [
        "Role %s already exists",
    ]
    OA0036 = [
        "Action %s cannot be assigned",
    ]
    OA0037 = [
        "Email or password is invalid",
    ]
    OA0038 = [
        "User is inactive",
    ]
    OA0039 = [
        "Email and/or password is not provided",
    ]
    OA0041 = [
        "Password should be at least 4 characters",
    ]
    OA0042 = [
        "User %s already exists",
    ]
    OA0043 = [
        "User with id %s not found",
    ]
    OA0044 = [
        "Email has invalid format",
    ]
    OA0045 = [
        "Invalid model type: %s",
    ]
    OA0046 = [
        "Payload is not a valid json",
    ]
    OA0047 = [
        "Payload is malformed",
    ]
    OA0048 = [
        "%s should contain %s-%s characters",
    ]
    OA0049 = [
        "%s should be integer",
    ]
    OA0050 = [
        "Incorrect request body received",
    ]
    OA0051 = [
        "Action group \"%s\" cannot be assigned",
    ]
    OA0052 = [
        "%s method not allowed",
    ]
    OA0053 = [
        "Not found",
    ]
    OA0054 = [
        "Invalid scope_id",
    ]
    OA0055 = [
        "%s should be list",
    ]
    OA0056 = [
        "Type with id %s not found",
    ]
    OA0057 = [
        "Role with purpose %s not found",
    ]
    OA0058 = [
        "%s is not a valid purpose",
    ]
    OA0060 = [
        "Invalid %s",
    ]
    OA0061 = [
        "Database error: %s",
    ]
    OA0062 = [
        "This resource requires an authorization token",
    ]
    OA0063 = [
        "%s should be true or false",
    ]
    OA0064 = [
        "No one root type is found",
    ]
    OA0065 = [
        "%s should not contain only whitespaces",
    ]
    OA0066 = [
        "%s %s has a removed associated %s %s"
    ]
    OA0067 = [
        "Invalid provider %s",
    ]
    OA0070 = [
        "Registration with domain %s is prohibited. "
        "Please use your business email for registration",
    ]
    OA0071 = [
        "Email or verification_code is invalid",
    ]
    OA0072 = [
        "The verification code can be generated once in a minute"
    ]
