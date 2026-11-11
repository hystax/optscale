from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


def utcnow_timestamp() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp())


def utcfromtimestamp(timestamp) -> datetime:
    return datetime.fromtimestamp(
        timestamp, timezone.utc).replace(tzinfo=None)


def utctimestamp(date) -> int:
    return int(date.replace(tzinfo=timezone.utc).timestamp())


def startday(date) -> datetime:
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def startmonth(date) -> datetime:
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
