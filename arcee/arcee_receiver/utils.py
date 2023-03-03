from bson.json_util import Any, JSONOptions, DEFAULT_JSON_OPTIONS
from bson.objectid import ObjectId


def serializer(obj: Any, json_options: JSONOptions = DEFAULT_JSON_OPTIONS) -> Any:
    if isinstance(obj, ObjectId):
        return str(obj)
