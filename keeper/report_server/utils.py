import os
import json
import re
from datetime import datetime
import enum
from concurrent.futures import ThreadPoolExecutor

from keeper.report_server.exceptions import Err


from tools.optscale_exceptions.common_exc import WrongArgumentsException
from optscale_client.config_client.client import Client as ConfigClient


MAX_32_INT = 2 ** 31 - 1
MAX_64_INT = 2 ** 63 - 1
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
    def block_size(self):
        return self.client.block_size()

    @property
    def max_cpu(self):
        return self.client.max_cpu()

    @property
    def max_ram(self):
        return self.client.max_ram()

    @property
    def external_network_cidr(self):
        return self.client.external_network_cidr()

    @property
    def auth_url(self):
        return self.client.auth_url()

    @property
    def receiver_url(self):
        return self.client.receiver_url()

    @property
    def cluster_secret(self):
        return self.client.cluster_secret()

    @property
    def agent_secret(self):
        return self.client.agent_secret()


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
        return json.JSONEncoder.default(self, obj)


def is_uuid(check_str):
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z'
    return bool(re.match(pattern, str(check_str).lower()))


def is_not_list_of_uuids(check_list):
    return (not check_list or not isinstance(check_list, list) or
            any(not isinstance(_id, str) or not is_uuid(_id)
                for _id in check_list))


def raise_not_provided_exception(argument):
    raise WrongArgumentsException(Err.OK0035, [argument])


def check_int_attribute(name, value, min_length=0, max_length=MAX_64_INT):
    if value is None:
        raise_not_provided_exception(name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise WrongArgumentsException(Err.OK0036, [name])
    if not min_length <= value <= max_length:
        raise WrongArgumentsException(
            Err.OK0037, [name, min_length, max_length])


def validate_key_in_collection(key, collection):
    if key in collection:
        value = collection.get(key)
        if value is None:
            raise_not_provided_exception(key)


def _check_filter_list(objects, type):
    if objects is not None and not isinstance(objects, list):
        raise WrongArgumentsException(
            Err.OK0027, [type])
