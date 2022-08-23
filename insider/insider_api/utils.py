import re
from datetime import datetime
import enum
import json
from decimal import Decimal

from bson import ObjectId
from optscale_exceptions.common_exc import WrongArgumentsException

from insider_api.exceptions import Err


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


def check_string(name, value):
    if not isinstance(value, str):
        raise WrongArgumentsException(Err.OI0008, [name])


def is_public_region(region, cloud_type):
    return {'azure_cnr': _is_public_azure_region}.get(cloud_type)(region)


def _is_public_azure_region(region):
    regex = '^[a-z0-9]{1,}$'
    pattern = re.compile(regex)
    if not pattern.match(region):
        return False
    if region in ['uknorth', 'uksouth2']:
        return False
    if 'gov' in region:
        return False
    return True
