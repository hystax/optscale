import logging

LOG = logging.getLogger(__name__)


class ObjectInfo:
    def __init__(self, tag: str, bucket: str, key: str, size: int):
        self._tag = tag
        self._bucket = bucket
        self._key = key
        self._size = size

    @staticmethod
    def from_db_object(db_object: tuple[str, str, str, int]):
        return ObjectInfo(
            tag=db_object[0],
            bucket=db_object[1],
            key=db_object[2],
            size=db_object[3])

    @staticmethod
    def from_aws_object_info(bucket: str, obj: dict):
        try:
            return ObjectInfo(
                # ETag field is surrounded by double quotes ("etag")
                # Getting rid of them
                tag=obj["ETag"].strip('"'),
                bucket=bucket,
                key=obj["Key"],
                size=obj["Size"],
            )
        except KeyError as exc:
            LOG.error(f"Wrong object {obj}: {ex}")
            raise
        except Exception as exc:
            LOG.error(f"Unexpected exception {ex}")
            raise

    @property
    def tag(self):
        return self._tag

    @property
    def bucket(self):
        return self._bucket

    @property
    def key(self):
        return self._key

    @property
    def size(self):
        return self._size

    def __hash__(self):
        return hash((self._tag, self._bucket, self._key, self._size))

    def __eq__(self, other):
        return (
            (self._tag == other.tag) and
            (self._bucket == other.bucket) and
            (self._key == other.key) and
            (self._size == other.size)
        )

    def to_tuple(self):
        return self._tag, self._bucket, self._key, self._size

    def __str__(self):
        return f"|{self._tag: <38}| {self._bucket : <32}| {self._key: <32}| {self._size: >16} bytes|"
