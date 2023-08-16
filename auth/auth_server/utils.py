import enum
import hashlib
import json
import os
import re

from auth.auth_server.exceptions import Err
from concurrent.futures import ThreadPoolExecutor
from optscale_client.config_client.client import Client as ConfigClient
from datetime import datetime
from tools.optscale_exceptions.http_exc import OptHTTPError
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, UnauthorizedException, ForbiddenException,
    NotFoundException, ConflictException, FailedDependency)
from sqlalchemy import inspect


tp_executor = ThreadPoolExecutor(15)
MAX_32_INT = 2 ** 31 - 1


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
    def restapi_url(self):
        return self.client.restapi_url()

    @property
    def cluster_secret(self):
        return self.client.cluster_secret()


def as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def check_action(action_resources, action, resource_type, resource_id):
    try:
        resources = action_resources[action]
        if resource_type != 'root':
            check = any(filter(lambda x: x == (resource_type, resource_id),
                               resources))
        else:
            # TODO: check usage: Usually the root action doesn't require res_id
            check = any(filter(lambda x: x[0] == resource_type, resources))
        return check
    except KeyError:
        return False


def check_kwargs_is_empty(**kwargs):
    if kwargs:
        unexpected_string = ', '.join(kwargs.keys())
        raise WrongArgumentsException(Err.OA0022, [unexpected_string])


def pop_or_raise(object, key):
    if key not in object:
        raise WrongArgumentsException(Err.OA0031, [key])
    return object.pop(key)


def get_encryption_salt():
    return Config().client.encryption_salt_auth()


def hash_password(password, salt):
    return hashlib.sha256(
        password.encode('utf-8') + salt.encode('utf-8') +
        get_encryption_salt().encode('utf-8')).hexdigest()


def get_digest(val):
    return hashlib.md5(val.encode('utf-8')).hexdigest()


def get_input(keys, **input):
    return dict(filter(lambda x: x[1] is not None,
                       {key: input.get(key) for key in keys}.items()))


def is_email_format(check_str):
    regex = '^[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+(\.[a-z0-9!#$%&\'*+/=?`{|}~\^\-\+_()]+)*' \
            '@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,18})$'
    match = re.match(regex, str(check_str).lower())
    return bool(match)


def raise_not_provided_error(name):
    raise WrongArgumentsException(Err.OA0032, [name])


def check_string_attribute(name, value, min_length=1, max_length=255):
    if value is None:
        raise_not_provided_error(name)
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OA0033, [name])
    if not min_length <= len(value) <= max_length:
        raise WrongArgumentsException(
            Err.OA0048, [name, min_length, max_length])
    if value.isspace():
        raise WrongArgumentsException(Err.OA0065, [name])


def check_bool_attribute(name, value):
    if not isinstance(value, bool):
        raise WrongArgumentsException(Err.OA0063, [name])


def is_uuid(check_str):
    pattern = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    return bool(re.match(pattern, str(check_str).lower()))


def is_hystax_email(email):
    regex = '^.+@hystax.com$'
    match = re.match(regex, str(email).lower())
    return bool(match)


def is_demo_email(email):
    regex = '^.+@sunflower.demo$'
    match = re.match(regex, str(email).lower())
    return bool(match)


def check_list_attribute(name, value, required=True):
    if value is None:
        if not required:
            return
        raise_not_provided_error(name)
    if not isinstance(value, list):
        raise WrongArgumentsException(Err.OA0055, [name])


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


class PasswordValidator(object):
    # TODO: this is a placeholder, will implement in scope of ACR-1151

    def __init__(self, criteria):
        """
        Set the criteria of password validation
        :param criteria:
        """
        self.criteria = criteria

    def validate(self, password):
        """
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more
        """
        criteria = self.criteria

        length_error = len(password) < 8
        digit_error = re.search(r"\d", password) is None
        uppercase_error = re.search(r"[A-Z]", password) is None
        lowercase_error = re.search(r"[a-z]", password) is None
        symbol_error = re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]',
                                 password) is None

        # result should depend on criteria
        return not (length_error or digit_error or uppercase_error or
                    lowercase_error or symbol_error)


def unique_list(list_to_filter):
    return list(set(list_to_filter))


def load_payload(payload):
    try:
        payload_dict = json.loads(payload)
        if not isinstance(payload_dict, dict):
            raise WrongArgumentsException(Err.OA0047, [])
    except ValueError:
        raise WrongArgumentsException(Err.OA0046, [])
    return payload_dict


def popkey(obj, key):
    if key in obj:
        obj.pop(key)
    for k, v in obj.items():
        if isinstance(v, dict):
            return popkey(v, key)


def get_context_values(context):
    values = list()
    for value in context.values():
        if isinstance(value, list):
            values.extend(value)
        else:
            values.append(value)
    return values


async def run_task(func, *args, **kwargs):
    try:
        res = await func(*args, **kwargs)
    except WrongArgumentsException as ex:
        raise OptHTTPError.from_opt_exception(400, ex)
    except UnauthorizedException as ex:
        raise OptHTTPError.from_opt_exception(401, ex)
    except ForbiddenException as ex:
        raise OptHTTPError.from_opt_exception(403, ex)
    except NotFoundException as ex:
        raise OptHTTPError.from_opt_exception(404, ex)
    except NotImplementedError:
        raise OptHTTPError(405, Err.OA0002, [])
    except ConflictException as ex:
        raise OptHTTPError.from_opt_exception(409, ex)
    except FailedDependency as ex:
        raise OptHTTPError.from_opt_exception(424, ex)
    return res
