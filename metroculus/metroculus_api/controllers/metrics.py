import logging
import math
from datetime import datetime, timedelta
from collections import defaultdict
from metroculus_api.exceptions import Err
from optscale_exceptions.common_exc import WrongArgumentsException
from metroculus_api.utils import (
    check_string, check_positive_integer, check_non_negative_integer)
from metroculus_api.controllers.base import (BaseController,
                                             BaseAsyncControllerWrapper)

METRIC_INTERVAL = 900
INTERVALS = [
    900,    # 15 minutes
    1800,   # 30 minutes
    3600,   # 1 hour
    10800,  # 3 hours
    21600,  # 6 hours
    43200,  # 12 hours
    86400   # 1 day
]
LOG = logging.getLogger(__name__)


class MetricsController(BaseController):
    @staticmethod
    def validate_parameters(**kwargs):
        for k in ['cloud_account_id', 'resource_id']:
            check_string(k, kwargs.get(k))
        check_non_negative_integer('start_date', kwargs.get('start_date'))
        check_positive_integer('end_date', kwargs.get('end_date'))
        check_positive_integer('interval', kwargs.get('interval'))
        interval = kwargs.get('interval')
        if interval % METRIC_INTERVAL != 0:
            raise WrongArgumentsException(Err.OM0006, ['interval'])

    @staticmethod
    def validate_interval_points_cnt(start_date, end_date, value):
        return (end_date - start_date).total_seconds() / value < 100

    @staticmethod
    def scale_interval(start_date, end_date, value):
        last_interval = value
        max_interval = INTERVALS[-1]
        for i, new_interval in enumerate(INTERVALS):
            if last_interval < new_interval or new_interval == max_interval:
                continue
            if MetricsController.validate_interval_points_cnt(
                    start_date, end_date, new_interval):
                return new_interval
            last_interval = INTERVALS[i + 1]
        return max_interval

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_account_id = kwargs.get('cloud_account_id')
        resource_id = kwargs.get('resource_id', [])
        start_dt_timestamp = kwargs.get('start_date')
        end_dt_timestamp = kwargs.get('end_date')
        interval = kwargs.get('interval', 900)
        start_date = datetime.fromtimestamp(math.floor(
            start_dt_timestamp / METRIC_INTERVAL) * METRIC_INTERVAL)
        end_date = datetime.fromtimestamp(math.floor(
            end_dt_timestamp / METRIC_INTERVAL) * METRIC_INTERVAL)
        if not self.validate_interval_points_cnt(
                start_date, end_date, interval):
            interval = self.scale_interval(start_date, end_date, interval)
        resource_metrics = self._get_metrics(cloud_account_id, resource_id,
                                             start_date, end_date)
        metric_values = defaultdict(list)
        for metric, value, date in resource_metrics:
            # if date == start_date this point contains statistics for 15
            # minutes before start_date
            if date != start_date:
                metric_values[metric].append((value, date))

        result = defaultdict(list)
        for metric, values in metric_values.items():
            next_date = start_date + timedelta(seconds=interval)
            grp_values = defaultdict(list)
            for value, date in values:
                while date > next_date:
                    next_date = next_date + timedelta(seconds=interval)
                grp_values[next_date].append(value)
            for dt, v in grp_values.items():
                avg_value = sum(v) / len(v)
                result[metric].append({
                    'date': int(dt.timestamp()),
                    'value': avg_value
                })
        return result

    def _get_metrics(
            self, cloud_account_id, resource_id, start_date, end_date):
        return self.clickhouse_client.execute(
            f'''
            SELECT metric, value, date
            FROM average_metrics
            WHERE cloud_account_id = '{cloud_account_id}'
                AND resource_id = '{resource_id}'
                AND date >= '{start_date}'
                AND date <= '{end_date}'
            ORDER BY date ASC
            '''
        )


class MetricsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return MetricsController
