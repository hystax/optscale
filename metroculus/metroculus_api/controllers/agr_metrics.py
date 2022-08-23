import logging
from datetime import datetime
from collections import defaultdict
from optscale_exceptions.common_exc import WrongArgumentsException
from metroculus_api.exceptions import Err
from metroculus_api.utils import (
    check_string, check_list, check_positive_integer, check_non_negative_integer,
    SUPPORTED_METRICS)
from metroculus_api.controllers.base import (BaseController,
                                             BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)


class AgrMetricsController(BaseController):
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
        check_list('meter_name', meter_names, False)
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
        metrics = self._get_agr_metrics(
            cloud_account_id, resource_ids, start_date, end_date)
        result = defaultdict(dict)
        for resource_id, meter_name, avg, peak, quantiles in metrics:
            if meter_names and meter_name not in meter_names:
                continue
            result[resource_id][meter_name] = {
                'avg': avg,
                'max': peak,
                'qtl50': quantiles[0],
                'qtl99': quantiles[1],
            }
        return result

    def _get_agr_metrics(
            self, cloud_account_id, resource_ids, start_date, end_date):
        """
        return resource_id, metric, avg, max, [quantiles(0.5), quantiles(0.99)]
        """
        return self.clickhouse_client.execute(
            f'''
            SELECT resource_id, metric, AVG(value), MAX(value), quantiles(0.5, 0.99)(value)
            FROM average_metrics
            WHERE cloud_account_id = '{cloud_account_id}'
                AND resource_id IN {resource_ids}
                AND date >= '{start_date}'
                AND date <= '{end_date}'
            GROUP BY resource_id, metric
            '''
        )


class AgrMetricsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return AgrMetricsController
