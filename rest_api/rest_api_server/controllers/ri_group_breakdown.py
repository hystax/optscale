import logging
from collections import defaultdict
from datetime import datetime
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.ri_breakdown import (
    RiBreakdownController)

CHUNK_SIZE = 200
LOG = logging.getLogger(__name__)
SEC_IN_HR = 3600
SUPPORTED_CLOUD_TYPES = ['aws_cnr']


class RiGroupBreakdownController(RiBreakdownController):

    def get_usage_breakdown(self, cloud_account_ids):
        return self.execute_clickhouse(
            """SELECT cloud_account_id, date, resource_id, instance_type,
                 location, os, sum(usage * sign), sum(cost * sign)
               FROM uncovered_usage
               WHERE cloud_account_id IN cloud_account_ids AND
                 date >= %(start_date)s AND date <= %(end_date)s AND
                 os!='' and location!='' and instance_type!=''
               GROUP BY cloud_account_id, date, resource_id, instance_type,
                 location, os
               HAVING sum(sign) > 0""",
            params={
                'start_date': datetime.fromtimestamp(self.start_date),
                'end_date': datetime.fromtimestamp(self.end_date)
            },
            external_tables=[{'name': 'cloud_account_ids',
                              'structure': [('id', 'String')],
                              'data': [{'id': r_id} for r_id in
                                       cloud_account_ids]}])

    def get_resources_info(self, resource_account_map):
        resources_info = {}
        cloud_resource_ids = list(resource_account_map)
        for i in range(0, len(resource_account_map), CHUNK_SIZE):
            resource_chunk = cloud_resource_ids[i:i + CHUNK_SIZE]
            cloud_account_chunk = set(
                resource_account_map[x] for x in resource_chunk)
            resources = self.resources_collection.find({
                'cloud_account_id': {'$in': list(cloud_account_chunk)},
                'cloud_resource_id': {'$in': resource_chunk}
            }, {'cloud_resource_id': 1, '_id': 1, 'name': 1})
            for resource in resources:
                resources_info[resource['cloud_resource_id']] = resource
        return resources_info

    def get(self, organization_id, **params):
        filters = params.copy()
        aws_cloud_accs_map = self.get_aws_accounts_map(organization_id)
        self.handle_filters(params, filters, organization_id)
        cloud_account_ids = self.filter_cloud_accounts(
            params, aws_cloud_accs_map)
        result = defaultdict(list)
        usages = self.get_usage_breakdown(cloud_account_ids)
        res_account_map = {}
        date_group_usage = defaultdict(lambda: defaultdict(list))
        for exp in usages:
            (cloud_account_id, date, resource_id, instance_type, location, os,
             usage, cost) = exp
            res_account_map[resource_id] = cloud_account_id
            group_id = (instance_type, os, location)
            usage = {
                'cloud_account_id': cloud_account_id,
                'cloud_resource_id': resource_id,
                'usage': usage,
                'cost': cost
            }
            usage.update(self.format_cloud_account(
                cloud_account_id, aws_cloud_accs_map))
            date_group_usage[int(date.timestamp())][group_id].append(usage)
        resources_info = self.get_resources_info(res_account_map)
        for date, group_usage in date_group_usage.items():
            for group_id, usages_list in group_usage.items():
                instance_type, os, location = group_id
                group = {
                    'instance_type': instance_type,
                    'os': os,
                    'location': location
                }
                data = []
                for usage in usages_list:
                    resource = resources_info.get(usage['cloud_resource_id'])
                    if resource:
                        usage['id'] = resource['_id']
                        usage['name'] = resource.get('name')
                    data.append(usage)
                result[date].append({
                    'group_id': group,
                    'data': data
                })

        breakdown_dates = self.breakdown_dates(self.start_date, self.end_date)
        if result:
            for date in breakdown_dates:
                if date not in result:
                    result[date] = []
        return result


class RiGroupBreakdownAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RiGroupBreakdownController
