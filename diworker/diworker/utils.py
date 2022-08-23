from pymongo.errors import BulkWriteError
from retrying import retry


def _retry_on_mongo_error(exc):
    if isinstance(exc, BulkWriteError):
        # retry if we got error in mongo upsert
        return True
    return False


@retry(retry_on_exception=_retry_on_mongo_error, wait_fixed=2000,
       stop_max_attempt_number=10)
def retry_mongo_upsert(method, *args, **kwargs):
    return method(*args, **kwargs)


def get_month_start(date, timezone=None):
    date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if timezone:
        date = date.replace(tzinfo=timezone.utc)
    return date


def bytes_to_gb(value):
    return value / 2**30
