from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
import enum
import json
import logging
import uuid


LOG = logging.getLogger(__name__)
tp_executor = ThreadPoolExecutor(30)


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
