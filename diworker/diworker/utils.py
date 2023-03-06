import time
from functools import wraps
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


def retry_backoff(exc_class, tries=8, delay=2, backoff=2, raise_errors=None):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return f(*args, **kwargs)
                except exc_class as e:
                    if raise_errors and type(e) in raise_errors:
                        raise
                    time.sleep(m_delay)
                    m_tries -= 1
                    m_delay *= backoff
            return f(*args, **kwargs)
        return f_retry
    return deco_retry
