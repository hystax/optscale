import pytz
from datetime import datetime


def _fix_time(timestamp, l_timezone: pytz.tzfile):
    result = None
    if timestamp:
        # convert UTC timestamp to datetime and replace timezone from UTC to
        # schedule timezone
        date_utc = datetime.fromtimestamp(timestamp, tz=pytz.utc)
        result = l_timezone.localize(date_utc.replace(tzinfo=None))
    return result


def is_schedule_outdated(schedule):
    now = datetime.now(pytz.utc)
    l_timezone = pytz.timezone(schedule['timezone'])
    start_date_local = _fix_time(schedule['start_date'], l_timezone)
    end_date_local = _fix_time(schedule['end_date'], l_timezone)
    if ((not start_date_local or start_date_local < now) and (
            not end_date_local or end_date_local > now)):
        return False
    return True
