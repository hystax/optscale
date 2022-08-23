import json
import re
import os
from sqlalchemy import inspect
import enum
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from herald_server.exceptions import Err

from optscale_exceptions.http_exc import OptHTTPError
from config_client.client import Client as ConfigClient


tp_executor = ThreadPoolExecutor(15)


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


def get_encryption_key():
    return Config().client.read('/encryption_key').value.encode()


def is_valid_port(value):
    try:
        port = int(value)
    except (ValueError, TypeError):
        return False
    if 1 <= port <= 65535:
        return True
    return False


def is_email_format(check_str):
    regex = '^[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+(\.[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+)*' \
            '@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,18})$'
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
