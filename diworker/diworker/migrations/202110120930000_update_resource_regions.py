from pymongo import UpdateMany
from diworker.diworker.migrations.base import BaseMigration
from optscale_client.rest_api_client.client_v2 import Client as RestClient


GET_CHUNK_SIZE = 5000
UPDATE_CHUNK_SIZE = 100
MAIN_RESOURCE_PRODUCT_FAMILY_MAP = {
    'Bucket': ['Storage', 'Data Transfer', 'Fee'],
    'Instance': ['Compute Instance', 'Stopped Instance'],
    'Snapshot': ['Storage Snapshot'],
    'Volume': ['Storage']
}

"""
Fix resource, clean_expenses and expenses_group_month_resource regions according to raw_expenses regions
"""


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def mongo_clean(self):
        return self.db.expenses

    @property
    def mongo_resource(self):
        return self.db.resources

    @property
    def mongo_group_month_resource(self):
        return self.db.expenses_group_month_resource

    @staticmethod
    def set_raw_chunk(expenses):
        chunk = {}
        for ex in expenses:
            resource_id = ex['resource_id']
            if not chunk.get(resource_id):
                chunk[resource_id] = list()
            chunk[resource_id].append(ex)
        return chunk

    @staticmethod
    def get_resource_type(raw_expense, resource_type):
        usage_type = raw_expense.get('lineItem/UsageType')
        operation = raw_expense.get('lineItem/Operation')
        tax_type = raw_expense.get('lineItem/TaxType')
        product = raw_expense.get('lineItem/ProductCode')
        product_family = raw_expense.get('product/productFamily')
        resource_type_map = {
            'Instance': usage_type and operation and ('BoxUsage' in usage_type or 'Instance' in operation),
            'Snapshot': usage_type and operation and ('Snapshot' in usage_type or 'Snapshot' in operation),
            'Volume': usage_type and 'Volume' in usage_type,
            'Bucket': product and 'AmazonS3' in product,
            'IP Address': product_family and 'IP Address' in product_family,
            'Other': tax_type or resource_type or product_family or usage_type
        }
        resource_type_keys = [k for k, v in resource_type_map.items() if v is True]
        return resource_type_keys[0] if resource_type_keys else resource_type_map.get('Other')

    def calculate_correct_region_map(self, raw_chunk):
        res_id_correct_region_map = {}
        not_main_resource_type_list = []
        for resource_id, raw_expenses in raw_chunk.items():
            resource_type = None
            family_region_map = {}
            for raw_expense in raw_expenses:
                if resource_type not in MAIN_RESOURCE_PRODUCT_FAMILY_MAP.keys():
                    resource_type = self.get_resource_type(raw_expense, resource_type)
                # set region only for main resource types (Bucket, Instance, Snapshot, Volume)
                product_region = raw_expense.get('product/region')
                product_family = raw_expense.get('product/productFamily')
                if resource_type:
                    if resource_type in MAIN_RESOURCE_PRODUCT_FAMILY_MAP.keys():
                        if product_region:
                            family_value_list = MAIN_RESOURCE_PRODUCT_FAMILY_MAP.get(resource_type, [])
                            for family_value in family_value_list:
                                if product_family and family_value in product_family:
                                    if not family_region_map.get(family_value):
                                        family_region_map[family_value] = product_region
                    else:
                        not_main_resource_type_list.append(resource_id)
                        break
            product_family_by_resource_list = MAIN_RESOURCE_PRODUCT_FAMILY_MAP.get(resource_type, [])
            for product_family_value in product_family_by_resource_list:
                for product_family, _region in family_region_map.items():
                    if product_family_value in product_family:
                        res_id_correct_region_map[resource_id] = _region
                        break
        return res_id_correct_region_map, not_main_resource_type_list

    def init_resource_with_correct_region_map(self, cloud_account_resources_with_some_regions_map):
        all_resource_id_list = []
        for resource_ids in cloud_account_resources_with_some_regions_map.values():
            all_resource_id_list.extend(resource_ids)
        all_resource_ids = list(set(all_resource_id_list))
        cloud_res_id_region_map = {}
        for cloud_account_id in list(cloud_account_resources_with_some_regions_map.keys()):
            filters = {
                'resource_id': {'$in': all_resource_ids},
                'cloud_account_id': cloud_account_id
            }
            raw_chunk = self.set_raw_chunk(list(self.mongo_raw.find(filters)))
            res_id_correct_region_map, not_main_resource_type_list = self.calculate_correct_region_map(raw_chunk)
            cloud_res_id_region_map.update(res_id_correct_region_map)
            all_resource_ids = list(set(all_resource_ids) - set(list(res_id_correct_region_map.keys())) -
                                    set(not_main_resource_type_list))
            if not all_resource_ids:
                break
        return cloud_res_id_region_map

    def upgrade(self):
        active_cloud_account_ids = []
        _, organization_list = self.rest_cl.organization_list()
        organizations = organization_list['organizations']
        for org in organizations:
            _, cloud_acc_list = self.rest_cl.cloud_account_list(org['id'], type='aws_cnr')
            cloud_accounts = cloud_acc_list['cloud_accounts']
            for cloud_account in cloud_accounts:
                if cloud_account['last_import_at'] == 0 or cloud_account['last_import_modified_at'] == 0:
                    continue
                active_cloud_account_ids.append(cloud_account['id'])
        all_cloud_resource_ids = [(x['cloud_account_id'], x['cloud_resource_id'])
                                  for x in self.mongo_resource.find(
                {'cloud_account_id': {'$in': active_cloud_account_ids}},
                ['cloud_account_id', 'cloud_resource_id'])]
        cloud_account_resources = {}
        for cloud_account_id, cloud_resource_id in all_cloud_resource_ids:
            if not cloud_account_resources.get(cloud_account_id):
                cloud_account_resources[cloud_account_id] = []
            cloud_account_resources[cloud_account_id].append(cloud_resource_id)
        cloud_account_resources_with_some_regions_map = {}
        for cloud_account_id, cloud_resource_ids in cloud_account_resources.items():
            for i in range(0, len(cloud_resource_ids), GET_CHUNK_SIZE):
                ids_chunk = cloud_resource_ids[i:i + GET_CHUNK_SIZE]
                raw_resource_ids_with_some_regions_list = list(self.mongo_raw.aggregate([
                    {'$match': {'$and': [
                        {'cloud_account_id': cloud_account_id},
                        {'resource_id': {'$in': ids_chunk}}]
                    }},
                    {'$group': {
                        '_id': '$resource_id',
                        'regions': {'$addToSet': '$product/region'}
                    }},
                    {'$project': {
                        'size': {'$size': '$regions'},
                    }},
                    {'$match': {
                        'size': {'$gt': 1}
                    }}
                ]))
                if not cloud_account_resources_with_some_regions_map.get(cloud_account_id):
                    cloud_account_resources_with_some_regions_map[cloud_account_id] = []
                cloud_account_resources_with_some_regions_map[cloud_account_id].extend(
                    [item['_id'] for item in raw_resource_ids_with_some_regions_list if item.get('_id') is not None])
        cloud_res_id_region_map = self.init_resource_with_correct_region_map(
            cloud_account_resources_with_some_regions_map)
        update_requests = []
        for cloud_resource_id, region in cloud_res_id_region_map.items():
            update_requests.append(UpdateMany(
                filter={'cloud_resource_id': cloud_resource_id, 'region': {'$ne': region}},
                update={'$set': {'region': region}},
            ))
        for i in range(0, len(update_requests), UPDATE_CHUNK_SIZE):
            chunk_update_request = update_requests[i:i + UPDATE_CHUNK_SIZE]
            self.mongo_clean.bulk_write(chunk_update_request)
            self.mongo_resource.bulk_write(chunk_update_request)
            self.mongo_group_month_resource.bulk_write(chunk_update_request)

    def downgrade(self):
        pass
