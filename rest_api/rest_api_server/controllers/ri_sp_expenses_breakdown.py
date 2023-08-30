import logging
from collections import defaultdict
from datetime import datetime
from rest_api.rest_api_server.controllers.ri_sp_usage_breakdown import RiSpUsageController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper


LOG = logging.getLogger(__name__)
SEC_IN_HR = 3600
SUPPORTED_CLOUD_TYPES = ['aws_cnr']


class RiSpExpensesController(RiSpUsageController):

    def get_usage_breakdown(self, start_date, end_date, cloud_account_ids):
        return self.execute_clickhouse(
            """SELECT
                 cloud_account_id, offer_type, date,
                 sum(offer_cost * sign), sum(on_demand_cost * sign)
               FROM ri_sp_usage
               WHERE cloud_account_id IN %(cloud_account_ids)s AND
                 date >= %(start_date)s AND date <= %(end_date)s
               GROUP BY cloud_account_id, offer_type, date
               HAVING sum(sign) > 0
               """,
            params={
                'cloud_account_ids': cloud_account_ids,
                'start_date': datetime.fromtimestamp(start_date),
                'end_date': datetime.fromtimestamp(end_date)
            })

    def get_total_usage(self, start_date, end_date, cloud_account_ids):
        pipeline = [
            {'$match': {
                'cloud_account_id': {'$in': cloud_account_ids},
                'start_date': {
                    '$gte': datetime.fromtimestamp(start_date),
                    '$lte': datetime.fromtimestamp(end_date)},
                'box_usage': True,
                'lineItem/LineItemType': {'$ne': 'Credit'}
            }},
            {
                '$project': {
                    'start_date': 1,
                    'cloud_account_id': 1,
                    'lineItem/LineItemType': 1,
                    'pricing/publicOnDemandCost': 1,
                    'reservation/EffectiveCost': 1,
                    'savingsPlan/SavingsPlanEffectiveCost': 1,
                    'lineItem/UnblendedCost': 1
                }
            },
            {'$group': {
                '_id': {
                    'start_date': '$start_date',
                    'cloud_account_id': '$cloud_account_id',
                },
                'total_cost_without_offer': {
                    '$push': '$pricing/publicOnDemandCost'},
                'unblended_cost': {'$push': '$lineItem/UnblendedCost'},
                'reservation_effective_cost': {
                    '$push': '$reservation/EffectiveCost'},
                'sp_effective_cost': {
                    '$push': '$savingsPlan/SavingsPlanEffectiveCost'},
            }}]
        return self.raw_expenses_collection.aggregate(pipeline)

    def get_total_cloud_account_stats(self, cloud_account_ids):
        cloud_account_total_usage = defaultdict(lambda: defaultdict(
            lambda: {'cost_without_offer': 0, 'cost_with_offer': 0}))
        accounts_total_usages = self.get_total_usage(
            self.start_date, self.end_date, cloud_account_ids)
        for mongo_usage in accounts_total_usages:
            cloud_account_id = mongo_usage['_id']['cloud_account_id']
            date = mongo_usage['_id']['start_date']
            unblended_cost = sum(
                float(x) for x in mongo_usage['unblended_cost'])
            reservation_eff_cost = sum(
                float(x) for x in mongo_usage['reservation_effective_cost'])
            sp_eff_cost = sum(
                float(x) for x in mongo_usage['sp_effective_cost'])
            total_cost_with_offer = (
                    unblended_cost + reservation_eff_cost + sp_eff_cost)
            total_cost_without_offer = sum(
                float(x) for x in mongo_usage['total_cost_without_offer'])
            cloud_account_total_usage[cloud_account_id][date][
                'cost_with_offer'] += total_cost_with_offer
            cloud_account_total_usage[cloud_account_id][date][
                'cost_without_offer'] += total_cost_without_offer
        return cloud_account_total_usage

    def get_cloud_account_ri_sp_stats(self, cloud_account_ids):
        cloud_account_usage = defaultdict(
            lambda: defaultdict(lambda: defaultdict(
                lambda: {'cost_without_offer': 0, 'cost_with_offer': 0})))
        usage_breakdown = self.get_usage_breakdown(
            self.start_date, self.end_date, cloud_account_ids)
        for ch_usage in usage_breakdown:
            cloud_account_id, offer_type, date, offer_cost, on_demand_cost = ch_usage
            cloud_account_usage[cloud_account_id][date][
                offer_type]['cost_without_offer'] += on_demand_cost
            cloud_account_usage[cloud_account_id][date][
                offer_type]['cost_with_offer'] += offer_cost
        return cloud_account_usage

    def format_result(self, result, cloud_account_id, date_ts, total_stats,
                      ri_sp_stats, cloud_accs_map):
        ri_stats = ri_sp_stats.get('ri', {})
        sp_stats = ri_sp_stats.get('sp', {})
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total': {
                'cost_without_offer': total_stats.get('cost_without_offer', 0),
                'cost_with_offer': total_stats.get('cost_with_offer', 0),
            },
            'ri': {
                'cost_without_offer': ri_stats.get('cost_without_offer', 0),
                'cost_with_offer': ri_stats.get('cost_with_offer', 0),
            },
            'sp': {
                'cost_without_offer': sp_stats.get('cost_without_offer', 0),
                'cost_with_offer': sp_stats.get('cost_with_offer', 0),
            }
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        result[date_ts].append(result_dict)
        return result

    def _empty_stats(self, cloud_account_id, cloud_accs_map):
        result_dict = {
            'cloud_account_id': cloud_account_id,
            'total': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            },
            'ri': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            },
            'sp': {
                'cost_without_offer': 0,
                'cost_with_offer': 0,
            }
        }
        result_dict.update(self.format_cloud_account(
            cloud_account_id, cloud_accs_map))
        return result_dict


class RiSpExpensesAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RiSpExpensesController
