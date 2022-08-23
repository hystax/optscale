from datetime import datetime
from decimal import Decimal
import enum
import json
import logging
import uuid

from optscale_exceptions.common_exc import WrongArgumentsException

from katara_service.exceptions import Err

LOG = logging.getLogger(__name__)


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
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except Exception:
                pass
        return json.JSONEncoder.default(self, obj)


def gen_id():
    return str(uuid.uuid4())


def strtobool(val):
    val = val.lower()
    if val not in ['true', 'false']:
        raise ValueError('Should be false or true')
    return val == 'true'


def raise_not_provided_error(name):
    raise WrongArgumentsException(Err.OKA0021, [name])


def check_kwargs_empty(**kwargs):
    if kwargs:
        unexpected_string = ', '.join(kwargs.keys())
        raise WrongArgumentsException(Err.OKA0012, [unexpected_string])


def check_list_attribute(name, value, required=True):
    if value is None:
        if not required:
            return
        raise_not_provided_error(name)
    if not isinstance(value, list):
        raise WrongArgumentsException(Err.OKA0020, [name])
