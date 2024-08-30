from enum import Enum
import logging

from collections import defaultdict
from datetime import datetime, timedelta
from math import ceil

import re
from requests import HTTPError

from optscale_client.insider_client.client import Client as InsiderClient
from optscale_client.metroculus_client.client import Client as MetroculusClient

from bumiworker.bumiworker.modules.base import (
    ModuleBase, ArchiveBase, ArchiveReason
)

LOG = logging.getLogger(__name__)
BULK_SIZE = 500
METRICS_BULK_SIZE = 50
HOURS_IN_DAY = 24
SECONDS_IN_HOUR = 3600
SECONDS_IN_DAY = HOURS_IN_DAY * SECONDS_IN_HOUR
DAYS_IN_MONTH = 30
BYTES_IN_GB = 2 ** 30


class LimitType(Enum):
    MAX = 'max'
    AVG = 'avg'
    Q50 = 'qtl50'
    Q99 = 'qtl99'


class RightsizingBase(ModuleBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._insider_cl = None
        self._metroculus_cl = None
        self.excluded_flavor_regex_key = 'excluded_flavor_regex'
        self.cloud_account_map = {}

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._insider_cl

    @property
    def metroculus_cl(self):
        if self._metroculus_cl is None:
            self._metroculus_cl = MetroculusClient(
                url=self.config_cl.metroculus_url(),
                secret=self.config_cl.cluster_secret(),
                verify=False)
        return self._metroculus_cl

    def get_organization_currency(self):
        _, organization = self.rest_client.organization_get(
            self.organization_id)
        return organization.get('currency', 'USD')

    def _get_supported_func_map(self):
        raise NotImplementedError

    def _get_raw_expense_resource_filter(self):
        raise NotImplementedError

    def get_insider_resource_type(self):
        raise NotImplementedError

    @staticmethod
    def _get_base_recommended_cpu(flavor_cpu, instance_metrics,
                                  optimization_metric):
        optimization_metric_type = optimization_metric.get('type')
        optimization_metric_limit = optimization_metric.get('limit')
        relevant_instance_metric = instance_metrics.get(
            optimization_metric_type)
        if relevant_instance_metric is None:
            LOG.warning("unknown CPU metric %s", optimization_metric_type)
            return None
        recommended = ceil(
            flavor_cpu / optimization_metric_limit * relevant_instance_metric)
        return recommended

    def get_recommended_cpu(self, flavor_cpu, instance_metrics,
                            optimization_metric, recommended_flavor_cpu_min):
        recommended_cpu_list = []
        min_recommended = self._get_base_recommended_cpu(
            flavor_cpu, instance_metrics, optimization_metric)
        if min_recommended:
            recommended_cpu_list = [
                x for x in range(int(min_recommended), flavor_cpu)
                if x >= recommended_flavor_cpu_min and bool(
                    x == 1 or x > 1 and x % 2 == 0)]
        return recommended_cpu_list

    @staticmethod
    def get_common_match_pipeline(resource_ids, cloud_account_ids):
        now = datetime.utcnow()
        return {
            '$match': {
                '$and': [
                    {'resource_id': {'$in': resource_ids}},
                    {'cloud_account_id': {'$in': cloud_account_ids}},
                    {'box_usage': True},
                    {'start_date': {
                        '$gte': now - timedelta(days=DAYS_IN_MONTH)
                    }},
                ]
            }
        }

    @staticmethod
    def get_common_group_pipeline():
        return {
            '$group': {
                '_id': {'resource_id': '$resource_id'},
                'cloud_account_id': {'$first': "$cloud_account_id"},
                "cost": {'$sum': '$cost'}
            }
        }

    def _create_or_increment(self, dictionary, key):
        dictionary[key] = dictionary.get(key, 0) + 1

    def _get_instances_info_func(self, cloud_type):
        supported_func_map = self._get_supported_func_map()
        return supported_func_map[cloud_type]['instances_info']

    def _get_family_specs_func(self, cloud_type):
        supported_func_map = self._get_supported_func_map()
        return supported_func_map[cloud_type]['family_specs']

    def _get_metric_func(self, cloud_type):
        supported_func_map = self._get_supported_func_map()
        return supported_func_map[cloud_type]['metric']

    def _get_metrics(self, resource_ids, cloud_account_id,
                     days_threshold, cloud_type):
        metrics_map = {}
        metric_func = self._get_metric_func(cloud_type)
        for i in range(0, len(resource_ids), METRICS_BULK_SIZE):
            metrics_map.update(metric_func(
                cloud_account_id=cloud_account_id,
                resource_ids=resource_ids[i:i + METRICS_BULK_SIZE],
                days_threshold=days_threshold
            ))
        return metrics_map

    def _get_instances_info(self, cloud_resources, cloud_account_id,
                            cloud_type):
        info_func = self._get_instances_info_func(cloud_type)
        return info_func(cloud_resources, [cloud_account_id])

    def _get_flavor_params(self, cloud_resource_id_info_map,
                           cloud_resource_id_instance_map, cloud_type):
        result = []
        specs_func = self._get_family_specs_func(cloud_type)
        for cloud_resource_id, info_list in cloud_resource_id_info_map.items():
            instance = cloud_resource_id_instance_map[cloud_resource_id]
            region = instance.get('region')
            family_specs = specs_func(instance)
            meta = instance['meta']
            for info in info_list:
                flavor_params = {
                    'os_type': info.get('os') or meta.get('os'),
                }
                preinstalled = meta.get('preinstalled')
                if preinstalled and cloud_type == 'aws_cnr':
                    flavor_params['preinstalled'] = preinstalled
                meter_id = info.get('meter_id')
                if cloud_type == 'azure_cnr':
                    flavor = meta.get('flavor')
                    properties = info.get('additional_properties')
                    if flavor and properties and flavor not in properties:
                        continue
                    if meter_id:
                        flavor_params['meter_id'] = meter_id
                if meter_id and cloud_type == 'azure_cnr':
                    flavor_params['meter_id'] = meter_id
                if cloud_type == 'nebius' and 'cpu_count' in meta:
                    flavor_params['cpu'] = meta['cpu_count']

                exists = [i for i, x in enumerate(result)
                          if (x.get('family_specs') == family_specs and
                              x.get('flavor_params') == flavor_params and
                              x.get('region') == region)]
                if exists:
                    result[exists[0]]['resource_ids'].append(cloud_resource_id)
                else:
                    result.append({
                        'resource_ids': [cloud_resource_id],
                        'family_specs': family_specs,
                        'flavor_params': flavor_params,
                        'region': region
                    })
        return result

    def _find_flavor(self, cloud_type, region, family_specs, mode, **params):
        try:
            currency = self.get_organization_currency()
            _, flavor = self.insider_cl.find_flavor(
                cloud_type, self.get_insider_resource_type(),
                region, family_specs, mode, currency=currency,
                **params)
            return flavor
        except HTTPError as ex:
            if ex.response.status_code == 403:
                raise
            LOG.warning('Unable to get %s flavor: %s', mode, str(ex))

    def _handle_instances(self, current_flavor_params, cloud_account,
                          write_stat_func, optimization_metric, metrics_map,
                          resource_info_map, r_info,
                          recommended_flavor_cpu_min, excluded_pools,
                          excluded_flavor_prog):
        result = []
        unable_to_get_current_flavor = set(
            x for params in current_flavor_params
            for x in params['resource_ids'])
        for params in current_flavor_params:
            res_ids = params['resource_ids']
            region = params['region']
            family_specs = params['family_specs']
            flavor_params = params['flavor_params']
            if cloud_account['type'] == 'nebius':
                flavor_params['cloud_account_id'] = cloud_account['id']
            current_flavor = self._find_flavor(
                cloud_account['type'], region, family_specs, 'current',
                **flavor_params)
            if not current_flavor:
                continue
            current_cpu = current_flavor.get('cpu', 0)
            if current_cpu <= recommended_flavor_cpu_min:
                for res_id in res_ids:
                    unable_to_get_current_flavor.remove(res_id)
                    write_stat_func('current_cpu_too_low')
                continue
            cpu_flavor_map = {}
            for res_id in res_ids:
                unable_to_get_current_flavor.remove(res_id)

                current_r_info = r_info[res_id][0]
                if (cloud_account['type'] == 'azure_cnr' and
                        len(r_info[res_id]) != 1):
                    meter_id = flavor_params['meter_id']
                    current_r_info = [x for x in r_info[res_id]
                                      if x['meter_id'] == meter_id][0]

                instance = resource_info_map[res_id]
                meta = instance['meta']
                instance_metrics = metrics_map.get(instance['_id'])
                if instance_metrics is None:
                    write_stat_func('no_metric')
                    continue
                recommended_cpu_list = self.get_recommended_cpu(
                    current_cpu, instance_metrics, optimization_metric,
                    recommended_flavor_cpu_min)
                flavor = meta.get('flavor')
                platform_name = meta.get('platform_name')
                if not recommended_cpu_list:
                    write_stat_func('no_recommended_cpu')
                    continue
                for i, recommended_cpu in enumerate(recommended_cpu_list):
                    if not cpu_flavor_map.get(recommended_cpu):
                        flavor_params['cpu'] = recommended_cpu
                        recommended_flavor = self._find_flavor(
                            cloud_account['type'], region, family_specs,
                            'search_relevant', **flavor_params)
                        if (not recommended_flavor and
                                i == len(recommended_cpu_list) - 1):
                            write_stat_func('unable_to_get_flavor')
                            break
                        cpu_flavor_map[recommended_cpu] = recommended_flavor
                    else:
                        recommended_flavor = cpu_flavor_map[recommended_cpu]
                    if not recommended_flavor:
                        continue
                    if (recommended_flavor['flavor'] == flavor or
                            platform_name and not flavor and
                            recommended_flavor['flavor'] != platform_name):
                        write_stat_func('no_recommended_flavor')
                        break
                    current_cost = current_r_info.get(
                        'day_cost', 0) * DAYS_IN_MONTH
                    discount_multiplier = current_r_info.get(
                        'discount_multiplier', 1)
                    multiplier = HOURS_IN_DAY * DAYS_IN_MONTH * discount_multiplier
                    recommended_cost = recommended_flavor.get(
                        'price') * multiplier
                    current_flavor_cost = current_flavor.get(
                        'price') * multiplier
                    if recommended_cost >= current_flavor_cost:
                        write_stat_func('current_cost_less_recommended')
                        break
                    saving = current_flavor_cost - recommended_cost
                    is_pool_excluded = instance.get('pool_id') in excluded_pools
                    is_flavor_excluded = bool(excluded_flavor_prog.pattern and
                                              excluded_flavor_prog.match(
                                                  flavor or platform_name))
                    write_stat_func('success')
                    cpu_peak = instance_metrics['max']
                    cpu_qtl_50 = instance_metrics['qtl50']
                    cpu_qtl_99 = instance_metrics['qtl99']
                    target_cpu = recommended_flavor['cpu']
                    project_cpu_avg = min([instance_metrics['avg'] * current_cpu / target_cpu, 100])  # max 100
                    project_cpu_peak = min([cpu_peak * current_cpu / target_cpu, 100])  # max 100
                    projected_cpu_qtl_50 = min([cpu_qtl_50 * current_cpu / target_cpu, 100])  # max 100
                    projected_cpu_qtl_99 = min([cpu_qtl_99 * current_cpu / target_cpu, 100])  # max 100

                    result.append({
                        'cloud_resource_id': instance['cloud_resource_id'],
                        'resource_name': instance.get('name'),
                        'resource_id': instance['_id'],
                        'cloud_account_id': instance['cloud_account_id'],
                        'cloud_type': cloud_account['type'],
                        'cloud_account_name': cloud_account['name'],
                        'region': region,
                        'flavor': flavor or platform_name,
                        'recommended_flavor': recommended_flavor['flavor'],
                        'saving': round(saving, 2),
                        'saving_percent': round(
                            saving / current_cost * 100, 2) if current_cost else 0,
                        'current_cost': round(current_cost, 2),
                        'recommended_flavor_cost': round(recommended_cost, 2),
                        'cpu': current_cpu,
                        'recommended_flavor_cpu': target_cpu,
                        'recommended_flavor_ram': recommended_flavor['ram'],
                        'cpu_usage': round(instance_metrics['avg'], 2),
                        'is_excluded': is_pool_excluded or is_flavor_excluded,
                        'cpu_peak': round(cpu_peak, 2),
                        'cpu_quantile_50': round(cpu_qtl_50, 2),
                        'cpu_quantile_99': round(cpu_qtl_99, 2),
                        'project_cpu_avg': round(project_cpu_avg, 2),
                        'project_cpu_peak': round(project_cpu_peak, 2),
                        'projected_cpu_qtl_50': round(projected_cpu_qtl_50, 2),
                        'projected_cpu_qtl_99': round(projected_cpu_qtl_99, 2),
                    })
                    break
        for _ in unable_to_get_current_flavor:
            write_stat_func('unable_to_get_current_flavor')
        return result

    def _get_instances(self, cloud_account_ids, start_date):
        if not cloud_account_ids:
            return []
        instances_filter = {
            'cloud_account_id': {
                '$in': cloud_account_ids
            },
            'active': True,
            'first_seen': {'$lt': start_date},
        }
        instances_filter.update(self._get_raw_expense_resource_filter())
        return self.mongo_client.restapi.resources.find(instances_filter)

    def _get(self):
        (days_threshold, optimization_metric,
         excluded_flavor_regex, excluded_pools, recommended_flavor_cpu_min,
         skip_cloud_accounts) = self.get_options_values()
        excluded_flavor_prog = re.compile(excluded_flavor_regex)

        supported_func_map = self._get_supported_func_map()
        supported_types = list(supported_func_map.keys())
        self.cloud_account_map = self.get_cloud_accounts(
            supported_types, skip_cloud_accounts)

        min_dt = datetime.utcnow() - timedelta(days=days_threshold)
        instances = self._get_instances(list(self.cloud_account_map.keys()),
                                        int(min_dt.timestamp()))

        resource_info_map = {}
        cloud_resource_resource_map = dict()
        ca_id_resource_map = defaultdict(list)
        for instance in instances:
            cloud_resource_id = instance['cloud_resource_id']
            resource_info_map[cloud_resource_id] = instance
            ca_id_resource_map[instance['cloud_account_id']].append(
                instance)
            cloud_resource_resource_map[cloud_resource_id] = instance['_id']
        result = []
        for ca_id, ca in self.cloud_account_map.items():
            stats_map = {}
            cloud_resources = ca_id_resource_map[ca_id]
            if not cloud_resources:
                self._create_or_increment(stats_map, 'no_instances')
                continue

            def write_stat(msg):
                self._create_or_increment(stats_map, msg)

            cloud_type = ca['type']
            info = self._get_instances_info(cloud_resources, ca_id, cloud_type)
            resource_ids = list(map(lambda x: cloud_resource_resource_map[x],
                                    info.keys()))
            if not resource_ids:
                continue
            metrics_map = self._get_metrics(
                resource_ids, ca_id, days_threshold, cloud_type)
            current_flavor_params = self._get_flavor_params(
                info, resource_info_map, cloud_type)

            ca_result = self._handle_instances(
                current_flavor_params, ca, write_stat, optimization_metric,
                metrics_map, resource_info_map, info,
                recommended_flavor_cpu_min, excluded_pools,
                excluded_flavor_prog)
            LOG.info('%s statistics for %s (%s): %s',
                     self.get_name().capitalize(), self.organization_id,
                     cloud_type, stats_map)
            if ca_result:
                result.extend(ca_result)
        return result

    def get_base_agr_cpu_metric(self, cloud_account_id, resource_ids,
                                days_threshold):
        now = datetime.utcnow()
        start = now - timedelta(days=days_threshold)
        _, metrics = self.metroculus_cl.get_aggregated_metrics(
            cloud_account_id, resource_ids, int(start.timestamp()),
            int(now.timestamp()), 'cpu')
        return {k: v['cpu'] for k, v in metrics.items()}

    def get_base_aws_instances_info(self, cloud_resources, cloud_account_ids):
        result = {}
        for i in range(0, len(cloud_resources), BULK_SIZE):
            bulk_resources = cloud_resources[i:i + BULK_SIZE]
            bulk_ids = [r["cloud_resource_id"] for r in bulk_resources]
            match_pipeline = self.get_common_match_pipeline(
                bulk_ids, cloud_account_ids)
            group_pipeline = self.get_common_group_pipeline()
            group_pipeline['$group'].update({
                'usages': {'$push': '$lineItem/UsageAmount'},
                'costs': {'$push': '$pricing/publicOnDemandCost'},
            })
            pipeline = [match_pipeline, group_pipeline]
            res = self.mongo_client.restapi.raw_expenses.aggregate(pipeline)
            for r in res:
                usages = sum([float(x) for x in r['usages']])
                costs = sum([float(x) for x in r['costs']])
                day_cost = costs / usages * HOURS_IN_DAY
                res_id = r['_id']['resource_id']
                result[res_id] = [{
                    'day_cost': day_cost,
                    'total_cost': r['cost'],
                    'cloud_account_id': r['cloud_account_id'],
                    'resource_id': res_id
                }]
        return result

    def get_base_azure_instances_info(self, cloud_resources,
                                      cloud_account_ids):
        result = defaultdict(list)
        for i in range(0, len(cloud_resources), BULK_SIZE):
            bulk_resources = cloud_resources[i:i + BULK_SIZE]
            bulk_ids = [r["cloud_resource_id"] for r in bulk_resources]
            match_pipeline = self.get_common_match_pipeline(
                bulk_ids, cloud_account_ids)
            sort_pipeline = {'$sort': {'end_date': 1}}
            group_pipeline = self.get_common_group_pipeline()
            group_pipeline['$group'].update({
                "_id": {"resource_id": "$resource_id", "meter_id": "$meter_id"},
                "usage_quantity": {"$sum": "$usage_quantity"},
                "additional_properties": {"$last": "$additional_properties"},
                "service_info": {"$last": "$service_info2"}
            })
            pipeline = [match_pipeline, sort_pipeline, group_pipeline]
            res = self.mongo_client.restapi.raw_expenses.aggregate(pipeline)
            for r in res:
                properties = r.get('additional_properties')
                if properties and 'Reservation' in properties:
                    continue
                res_id = r['_id']['resource_id']
                meter_id = r['_id']['meter_id']
                day_cost = r['cost'] * HOURS_IN_DAY / r['usage_quantity']
                data = {
                    'day_cost': day_cost,
                    'total_cost': r['cost'],
                    'cloud_account_id': r['cloud_account_id'],
                    'resource_id': r['_id'],
                    'meter_id': meter_id,
                    'additional_properties': properties
                }
                byol_str = properties or r.get('service_info') or ''
                if byol_str and 'Windows Client BYOL' in byol_str:
                    # Windows VM is charged using sku for Linux
                    data['os'] = 'Linux'
                result[res_id].append(data)
        return result

    def get_base_alibaba_instances_info(self, cloud_resources,
                                        cloud_account_ids, pay_as_you_go_item):
        result = {}
        for i in range(0, len(cloud_resources), BULK_SIZE):
            bulk_resources = cloud_resources[i:i + BULK_SIZE]
            bulk_ids = [r["cloud_resource_id"] for r in bulk_resources]
            match_pipeline = self.get_common_match_pipeline(
                bulk_ids, cloud_account_ids)
            group_pipeline = self.get_common_group_pipeline()
            group_pipeline['$group']['_id'] = {
                'resource_id': '$resource_id',
                'billing_item': '$BillingItem'
            }
            group_pipeline['$group'].update({
                'usages': {'$push': '$Usage'},
                'cost_without_discount':  {'$sum': '$PretaxGrossAmount'},
            })
            pipeline = [match_pipeline, group_pipeline]
            res = self.mongo_client.restapi.raw_expenses.aggregate(pipeline)
            for r in res:
                billing_item = r['_id']['billing_item']
                resource_id = r['_id']['resource_id']

                if resource_id in result:
                    LOG.info(
                        'Both pay-as-you-go and subscription costs found '
                        'for %s, choosing subscription costs', resource_id)
                    if billing_item == pay_as_you_go_item:
                        continue

                if billing_item == pay_as_you_go_item:
                    usages = sum(float(x) for x in r['usages'] if x)
                    if usages == 0:
                        # Alibaba may issue entries with Item=Adjustment, they
                        # have negative cost and empty usage. Sometimes,
                        # instances can have only adjustment entries, and no
                        # actual usage. Let's skip such instances.
                        LOG.warning('Zero usage for %s, skipping', resource_id)
                        continue
                    day_cost = r['cost'] * HOURS_IN_DAY / usages
                else:
                    day_cost = r['cost'] / DAYS_IN_MONTH

                result[resource_id] = [{
                    'day_cost': day_cost,
                    'total_cost': r['cost'],
                    'cloud_account_id': r['cloud_account_id'],
                    'resource_id': resource_id,
                    'discount_multiplier': r['cost'] / r[
                        'cost_without_discount'] if r[
                        'cost_without_discount'] else 1
                }]
        return result

    def get_base_gcp_instances_info(self, cloud_resources, cloud_account_ids):
        result = {}
        for cloud_resource in cloud_resources:
            resource_id = cloud_resource["cloud_resource_id"]
            current_flavor = self._find_flavor(
                "gcp_cnr", cloud_resource["region"],
                {"source_flavor_id": cloud_resource["meta"]["flavor"]},
                'current')
            if not current_flavor:
                # we do not currently support custom flavors,
                # so insider might return empty response
                continue
            hourly_cost = current_flavor["price"]
            daily_cost = hourly_cost * HOURS_IN_DAY
            result[resource_id] = [{
                    'day_cost': daily_cost,
                    'cloud_account_id': cloud_resource['cloud_account_id'],
                    'resource_id': resource_id,
                }]
        return result

    def get_base_nebius_instances_info(self, cloud_resources,
                                       cloud_account_ids):
        result = {}
        for cloud_resource in cloud_resources:
            resource_id = cloud_resource["cloud_resource_id"]
            cloud_account_id = cloud_resource['cloud_account_id']
            family_specs = self.get_base_nebius_family_specs(
                cloud_resource)
            if not family_specs:
                continue
            current_flavor = self._find_flavor(
                'nebius', cloud_resource.get("region"), family_specs,
                'current', cpu=cloud_resource['meta'].get('cpu_count'),
                cloud_account_id=cloud_account_id)
            LOG.info('current_flavor %s', current_flavor)
            hourly_cost = current_flavor["price"]
            daily_cost = hourly_cost * HOURS_IN_DAY
            result[resource_id] = [{
                    'day_cost': daily_cost,
                    'cloud_account_id': cloud_account_id,
                    'resource_id': resource_id,
                }]
        return result

    @staticmethod
    def get_base_family_specs(resource_info):
        return {'source_flavor_id': resource_info['meta']['flavor']}

    @staticmethod
    def get_base_nebius_family_specs(resource_info):
        result = {}
        meta = resource_info['meta']
        platform_name = meta.get('platform_name')
        if platform_name:
            result = {
                'source_flavor_id': platform_name,
                'cpu_fraction': meta.get('cpu_fraction', 100),
                'ram': meta.get('ram', 0) / BYTES_IN_GB,
            }
        return result

    def clean_excluded_flavor_regex(self, option_value, default_value):
        flavor_regex = option_value
        try:
            re.compile(flavor_regex)
        except Exception as exc:
            LOG.exception('Error while compiling regex %s, processing %s - %s',
                          self.excluded_flavor_regex_key, self.get_name(),
                          str(exc))
            if default_value is None:
                raise
            flavor_regex = default_value
            re.compile(flavor_regex)
        return flavor_regex

    def clean_rightsizing_metric(self, option_value, default_value):
        mertric = option_value
        metric_type = mertric.get('type')
        try:
            LimitType(metric_type)
        except ValueError:
            LOG.warning('incorrect rightsizing metric type value %s, '
                        'setting default', metric_type)
            return default_value
        metric_limit = mertric.get('limit')
        if not metric_limit:
            # to avoid division by zero
            LOG.warning('incorrect rightsizing metric limit value %s, '
                        'setting default', metric_limit)
            return default_value
        return option_value


class RightsizingArchiveBase(ArchiveBase, RightsizingBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            'flavor changed')

    @property
    def supported_cloud_types(self):
        return list(self._get_supported_func_map().keys())

    def _get_instances(self, cloud_account_ids, start_date):
        instances = super()._get_instances(cloud_account_ids, start_date)
        instances_by_account_map = {x: [] for x in cloud_account_ids}
        for instance in instances:
            cloud_account_id = instance['cloud_account_id']
            instances_by_account_map[cloud_account_id].append(instance)
        return instances_by_account_map

    def set_additional_reasons(self, cloud_resource_map, cloud_account,
                               cloud_resource_id_instance_map,
                               optimizations_dict, days_threshold, result):
        pass

    def _get(self, previous_options, optimizations, cloud_accounts_map,
             **kwargs):
        days_threshold = previous_options['days_threshold']

        cloud_acc_instances_map = defaultdict(dict)
        min_dt = datetime.utcnow() - timedelta(days=days_threshold)
        for cloud_acc_id, instances in self._get_instances(
                list(cloud_accounts_map.keys()),
                int(min_dt.timestamp())).items():
            for instance in instances:
                instance_key = self.get_record_key(instance)
                cloud_acc_instances_map[cloud_acc_id][instance_key] = instance

        account_optimizations_map = defaultdict(dict)
        for optimization in optimizations:
            optimization_key = self.get_record_key(optimization)
            account_optimizations_map[optimization['cloud_account_id']][
                optimization_key] = optimization

        result = []
        for cloud_account_id, optimizations_dict in account_optimizations_map.items():
            cloud_account = cloud_accounts_map.get(cloud_account_id)
            if not cloud_account:
                for optimization in optimizations_dict.values():
                    self._set_reason_properties(
                        optimization, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                    result.append(optimization)
                continue

            instances_map = cloud_acc_instances_map.get(cloud_account_id, {})
            cloud_resource_map = {}
            cloud_resource_id_instance_map = {}
            for instance_key, optimization in optimizations_dict.items():
                instance = instances_map.get(instance_key)
                if not instance:
                    self._set_reason_properties(
                        optimization, ArchiveReason.RESOURCE_DELETED)
                    result.append(optimization)
                    continue
                meta = instance['meta']
                inst_flavor = meta.get('flavor') or meta.get('platform_name')
                if (inst_flavor == optimization['recommended_flavor'] and
                        meta.get('cpu_count') == optimization[
                          'recommended_flavor_cpu']):
                    self._set_reason_properties(
                        optimization, ArchiveReason.RECOMMENDATION_APPLIED)
                    result.append(optimization)
                    continue
                else:
                    cloud_resource_map[instance['_id']] = instance
                    cloud_resource_id_instance_map[
                        instance['cloud_resource_id']] = instance

            if not cloud_resource_id_instance_map:
                continue

            self.set_additional_reasons(cloud_resource_map, cloud_account,
                                        cloud_resource_id_instance_map,
                                        optimizations_dict, days_threshold,
                                        result)
        return result
