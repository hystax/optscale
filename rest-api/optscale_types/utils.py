import re
import netaddr
import json
import uuid

from optscale_types.errors import Err

from optscale_exceptions.common_exc import WrongArgumentsException

MAX_32_INT = 2 ** 31 - 1
MAX_64_INT = 2 ** 63 - 1


def raise_invalid_argument_exception(argument):
    raise WrongArgumentsException(Err.OE0217, [argument])


def raise_not_provided_exception(argument):
    raise WrongArgumentsException(Err.OE0216, [argument])


def is_uuid(check_str):
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z'
    return bool(re.match(pattern, str(check_str).lower()))


def is_email_format(check_str):
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+''(\.[a-z0-9-]+)' \
            '*(\.[a-z]{2,18})$'
    match = re.match(regex, str(check_str).lower())
    return bool(match)


def is_valid_hostname(hostname):
    """http://stackoverflow.com/a/20204811"""
    regex = '(?=^.{1,253}$)(^(((?!-)[a-zA-Z0-9-]{1,63}(?<!-))|((?!-)' \
            '[a-zA-Z0-9-]{1,63}(?<!-)\.)+[a-zA-Z]{2,63})$)'
    match = re.match(regex, str(hostname).lower())
    return bool(match)


def check_ipv4_addr(address):
    if not address or not netaddr.valid_ipv4(str(address),
                                             netaddr.core.INET_PTON):
        raise ValueError("%s is not an IPv4 address" % address)


def is_valid_meta(metadata):
    try:
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            return False
    except:
        return False
    return True


def gen_id():
    return str(uuid.uuid4())


def check_string_attribute(name, value, min_length=1, max_length=255):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OE0214, [name])
    if not min_length <= len(value) <= max_length:
        count = ('max %s' % max_length if min_length == 0
                 else '%s-%s' % (min_length, max_length))
        raise WrongArgumentsException(Err.OE0215, [name, count])


def check_int_attribute(name, value, max_length=MAX_32_INT):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, int):
        raise WrongArgumentsException(Err.OE0223, [name])
    if not 0 <= value <= max_length:
        raise WrongArgumentsException(Err.OE0224, [name, 0, max_length])
