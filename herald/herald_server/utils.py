import json
import re
import os
import enum
import uuid
import netaddr
from sqlalchemy import inspect
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from herald.herald_server.exceptions import Err

from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import WrongArgumentsException

from optscale_client.config_client.client import Client as ConfigClient


tp_executor = ThreadPoolExecutor(15)

MAX_32_INT = 2 ** 31 - 1
MAX_64_INT = 2 ** 63 - 1


def gen_id():
    return str(uuid.uuid4())


def is_valid_hostname(hostname):
    """http://stackoverflow.com/a/20204811"""
    regex = '(?=^.{1,253}$)(^(((?!-)[a-zA-Z0-9-]{1,63}(?<!-))|((?!-)' \
            '[a-zA-Z0-9-]{1,63}(?<!-)\\.)+[a-zA-Z]{2,63})$)'
    match = re.match(regex, str(hostname).lower())
    return bool(match)


def check_ipv4_addr(address):
    if not address or not netaddr.valid_ipv4(str(address),
                                             netaddr.core.INET_PTON):
        raise ValueError("%s is not an IPv4 address" % address)


def is_uuid(check_str):
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\\Z'
    return bool(re.match(pattern, str(check_str).lower()))


def raise_not_provided_exception(argument):
    raise WrongArgumentsException(Err.OE0216, [argument])


def is_valid_meta(metadata):
    try:
        meta = json.loads(metadata)
        if not isinstance(meta, dict):
            return False
    except Exception:
        return False
    return True


def check_string_attribute(name, value, min_length=1, max_length=255):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OE0214, [name])
    if not min_length <= len(value) <= max_length:
        count = ('max %s' % max_length if min_length == 0
                 else '%s-%s' % (min_length, max_length))
        raise WrongArgumentsException(Err.OE0215, [name, count])


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Config(object):

    def __init__(self):
        etcd_host = os.environ.get('HX_ETCD_HOST')
        etcd_port = int(os.environ.get('HX_ETCD_PORT'))
        self.client = ConfigClient(host=etcd_host, port=etcd_port)

    @property
    def auth_url(self):
        return self.client.auth_url()

    @property
    def keeper_url(self):
        return self.client.keeper_url()

    @property
    def cluster_secret(self):
        return self.client.cluster_secret()

    @property
    def smtp_params(self):
        try:
            return self.client.smtp_params()
        except Exception:
            return None


def as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def is_valid_port(value):
    try:
        port = int(value)
    except (ValueError, TypeError):
        return False
    if 1 <= port <= 65535:
        return True
    return False


def is_email_format(check_str):
    regex = '^[a-z0-9!#$%&\'*+/=?`{|}~\\^\\-\\+_()]+(\\.[a-z0-9!#$%&\'*+/=?`{' \
            '|}~\\^\\-\\+_()]+)*@[a-z0-9-]+(\\.[a-z0-9-]+)*(\\.[a-z]{2,18})$'
    match = re.match(regex, str(check_str).lower())
    return bool(match)


def is_hystax_email(email):
    regex = '^.+@hystax.com$'
    match = re.match(regex, str(email).lower())
    return bool(match)


def raise_not_provided_error(argument):
    raise OptHTTPError(400, Err.G0025, [argument])


def raise_invalid_argument_exception(argument):
    raise OptHTTPError(400, Err.G0026, [argument])


class ModelEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return json.JSONEncoder.default(self, obj)
