import logging
import json
from clickhouse_driver import Client as ClickHouseClient
from collections import defaultdict
from datetime import datetime, timedelta
from rest_api.rest_api_server.controllers.ri_breakdown import (
    RiBreakdownController)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)

CH_DB_NAME = 'risp'
LOG = logging.getLogger(__name__)
SUPPORTED_CLOUD_TYPES = ['aws_cnr']


class OfferBreakdownController(RiBreakdownController):

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, _ = self._config.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=CH_DB_NAME, user=user)
        return self._clickhouse_client

    def get_ri_sp_usage(self, cloud_account_ids, start_date, end_date):
        return self.execute_clickhouse(
            """SELECT offer_id, date, any(offer_type),
                 any(cloud_account_id) as cloud_account_id,
                 sum(offer_cost * sign) AS offer_cost,
                 any(n_expected_cost * sign) AS expected_cost
               FROM (
                 SELECT offer_id, date, offer_cost, offer_type, sign,
                   if(expected_cost=0, null, cloud_account_id) as cloud_account_id,
                   if(expected_cost=0, null, expected_cost) as n_expected_cost
                 FROM ri_sp_usage
                 WHERE cloud_account_id IN cloud_account_ids AND
                   date >= %(start_date)s AND date <= %(end_date)s)
               GROUP BY offer_id, date
               HAVING sum(sign) > 0""",
            params={'start_date': start_date, 'end_date': end_date},
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])

    def get(self, organization_id, **params):
        result = defaultdict(list)
        filters = params.copy()
        _, cloud_accounts = self.get_organization_and_cloud_accs(
            organization_id)
        self.handle_filters(params, filters, organization_id)
        aws_cloud_accs_map = {
            x.id: {
                'type': x.type.value,
                'name': x.name
            }
            for x in cloud_accounts if x.type.value in SUPPORTED_CLOUD_TYPES
        }
        cloud_account_ids = params.get('cloud_account_id')
        if not cloud_account_ids:
            cloud_account_ids = list(aws_cloud_accs_map.keys())
        else:
            for cloud_account_id in cloud_account_ids:
                if cloud_account_id not in aws_cloud_accs_map.keys():
                    cloud_account_ids.remove(cloud_account_id)
        offer_usage = defaultdict(lambda: defaultdict(dict))
        cloud_account_offers = defaultdict(set)
        expenses = self.get_ri_sp_usage(cloud_account_ids, self.start_date,
                                        self.end_date)
        for expense in expenses:
            (offer_id, date, offer_type, cloud_account_id, offer_cost,
             expected_cost) = expense
            cloud_account_offers[cloud_account_id].add(offer_id)
            offer_usage[offer_id][date]['cost'] = offer_cost
            offer_usage[offer_id][date]['expected_cost'] = expected_cost
            offer_usage[offer_id][date]['offer_type'] = offer_type

        for cloud_account_id, offers in cloud_account_offers.items():
            resources = self.resources_collection.find(
                {'cloud_account_id': cloud_account_id,
                 'cloud_resource_id': {'$in': list(offers)},
                 'resource_type': {'$in': ['Savings Plan',
                                           'Reserved Instances']}},
                {'_id': 1, 'cloud_resource_id': 1, 'meta': 1})
            resources_dict = {x['cloud_resource_id']: x for x in resources}
            for offer_id in offers:
                offer_data = offer_usage.get(offer_id, {})
                for date, data in offer_data.items():
                    date_ts = int(date.timestamp())
                    offer = resources_dict.get(offer_id, {})
                    res_dict = {
                        'offer_type': data['offer_type'],
                        'cloud_resource_id': offer_id,
                        'id': offer.get('_id'),
                        'cost': data['cost'],
                        'expected_cost': data['expected_cost'],
                        'cloud_account_id': cloud_account_id
                    }
                    meta = offer.get('meta', {})
                    for field in ['payment_option', 'offering_type',
                                  'purchase_term', 'applied_region']:
                        if field in meta:
                            res_dict[field] = meta.get(field)
                    res_dict.update(self.format_cloud_account(
                        cloud_account_id, aws_cloud_accs_map))
                    result[date_ts].append(res_dict)
        if cloud_account_ids:
            breakdown_dates = self.breakdown_dates(self.start_date,
                                                   self.end_date)
            for date in breakdown_dates:
                if date not in result:
                    result[date] = []
        return result


class OfferBreakdownAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OfferBreakdownController
