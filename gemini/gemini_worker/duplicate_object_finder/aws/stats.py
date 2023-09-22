import datetime


class Stats:
    total_objects = 0
    filtered_objects = 0
    total_size = 0
    duplicates_size = 0
    duplicated_objects = 0
    buckets = None
    timedelta_requests = datetime.timedelta(0)
    timedelta_db = datetime.timedelta(0)
