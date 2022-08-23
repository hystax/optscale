import logging
from datetime import datetime
from collections import defaultdict
from optscale_exceptions.common_exc import WrongArgumentsException
from metroculus_api.exceptions import Err
from metroculus_api.utils import (
    check_string, check_list,
    check_positive_integer, check_non_negative_integer,
    SUPPORTED_METRICS)
from metroculus_api.controllers.base import (BaseController,
                                             BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)
DAYS_IN_WEEK = 7
HOURS_IN_DAY = 24
METRIC_INTERVAL = 900


class ActivityBreakdownController(BaseController):
    @staticmethod
    def validate_parameters(**kwargs):
        cloud_account_id = kwargs.get('cloud_account_id')
        check_string('cloud_account_id', cloud_account_id)
        resource_ids = kwargs.get('resource_ids', [])
        check_list('resource_id', resource_ids)
        for r_id in resource_ids:
            check_string('resource_id', r_id)
        check_non_negative_integer('start_date', kwargs.get('start_date'))
        check_positive_integer('end_date', kwargs.get('end_date'))
        meter_names = kwargs.get('meter_names', [])
        check_list('meter_name', meter_names)
        for meter_name in meter_names:
            check_string('meter_name', meter_name)
            if meter_name not in SUPPORTED_METRICS:
                raise WrongArgumentsException(Err.OM0006, ['meter_name'])

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_account_id = kwargs.get('cloud_account_id')
        resource_ids = kwargs.get('resource_ids', [])
        start_date_timestamp = kwargs.get('start_date')
        end_date_timestamp = kwargs.get('end_date')
        meter_names = kwargs.get('meter_names', [])
        start_date = datetime.fromtimestamp(start_date_timestamp)
        end_date = datetime.fromtimestamp(end_date_timestamp)
        activity_breakdown = self._get_activity_breakdown(
            cloud_account_id, resource_ids, start_date, end_date, meter_names)
        empty_matrix = [None] * DAYS_IN_WEEK * HOURS_IN_DAY
        result = defaultdict(lambda: defaultdict(lambda: empty_matrix.copy()))
        for resource_id, metric, value, day, hour in activity_breakdown:
            interval_number = (day-1) * 24 + hour
            result[resource_id][metric][interval_number] = value
        return result

    def _get_activity_breakdown(
            self, cloud_account_id, resource_ids, start_date, end_date, meter_names):
        """
        return resource_id, metric, average value, day of week, hour
        """
        # We need to account for the fact that dates in the table
        # actually represent the end of a 900 second time interval.
        # E.g. if we have a record saying that at 15:00:00 the metric value was X
        # it means that the metric value was X in a range 14:45:00-15:00:00.
        # In order to get correct DayOfWeek and Hour values we need
        # to shift date values by a half of the range length - 450 seconds.
        half_interval = METRIC_INTERVAL / 2
        return self.clickhouse_client.execute(
            query='''
            SELECT resource_id, metric, avg(value) as value,
                   toDayOfWeek(date-%(half_interval)s) as day, toHour(date-%(half_interval)s) as hour
            FROM average_metrics
            WHERE cloud_account_id = %(cloud_account_id)s
                AND resource_id IN %(resource_ids)s
                AND metric in %(meter_names)s
                AND date-%(half_interval)s BETWEEN %(start_date)s AND %(end_date)s
            GROUP BY resource_id, metric, toDayOfWeek(date-%(half_interval)s), toHour(date-%(half_interval)s)
            ''',
            params={
                'start_date': start_date,
                'end_date': end_date,
                'cloud_account_id': cloud_account_id,
                'resource_ids': resource_ids,
                'meter_names': meter_names,
                'half_interval': half_interval,
            }
        )


class ActivityBreakdownAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ActivityBreakdownController
