import re
from datetime import datetime
import enum
import json
from decimal import Decimal

from bson import ObjectId
from optscale_exceptions.common_exc import WrongArgumentsException

from metroculus_api.exceptions import Err

SUPPORTED_METRICS = ['cpu', 'ram', 'disk_read_io', 'disk_write_io',
                     'network_in_io', 'network_out_io']
SECONDS_IN_HOUR = 60 * 60


class ModelEncoder(json.JSONEncoder):
    # pylint: disable=E0202
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except Exception:
                pass
        return json.JSONEncoder.default(self, obj)


def check_string(name, value, required=True):
    if not value and required:
        raise_not_provided_exception(name)
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OM0006, [name])


def check_integer(name, value, required=True):
    if value is None and required:
        raise_not_provided_exception(name)
    if not isinstance(value, int):
        raise WrongArgumentsException(Err.OM0006, [name])


def check_non_negative_integer(name, value):
    check_integer(name, value)
    if value < 0:
        raise WrongArgumentsException(Err.OM0006, [name])


def check_positive_integer(name, value):
    check_integer(name, value)
    if value <= 0:
        raise WrongArgumentsException(Err.OM0006, [name])


def check_list(name, value, required=True):
    if not value and required:
        raise_not_provided_exception(name)
    if not isinstance(value, list):
        raise WrongArgumentsException(Err.OM0006, [name])


def raise_not_provided_exception(argument):
    raise WrongArgumentsException(Err.OM0008, [argument])


def seconds_to_hour(num_seconds):
    return num_seconds / SECONDS_IN_HOUR
