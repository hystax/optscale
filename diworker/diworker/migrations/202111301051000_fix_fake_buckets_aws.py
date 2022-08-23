import logging
from pymongo import UpdateMany
from diworker.migrations.base import BaseMigration
from rest_api_client.client_v2 import Client as RestClient

CHUNK_SIZE = 200
STORAGE_LENS_TYPE = 'StorageLens'
USAGE_NAME = 'AmazonS3 '
BUCKET_TYPE = 'Bucket'
NOT_FAKE_BUCKETS_TYPES = ['IP Address', 'NAT Gateway', 'Instance', 'Snapshot',
                          'Volume', 'Bucket']
CHECKED_PRODUCT = 'AmazonS3'
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def mongo_resources(self):
        return self.db.resources

    @property
    def mongo_expenses(self):
        return self.db.expenses

    @property
    def mongo_expenses_groupings(self):
        return self.db.expenses_group_month_resource

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def check_resources_with_id(
            self, ca_id, resources_with_id, change_resources=None):
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        'resource_id': {'$in': resources_with_id}
                    }
            },
            {
                '$group':
                    {
                        '_id': '$resource_id',
                        'operations': {'$addToSet': '$lineItem/Operation'},
                        'tax_type': {'$first': '$lineItem/TaxType'},
                        'product_family': {'$first': '$product/productFamily'},
                        'usage_type': {'$first': '$lineItem/UsageType'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = {}
        for record in resources_info:
            is_bucket = False
            is_storage_lens = False
            for operation in record['operations']:
                if BUCKET_TYPE in operation:
                    is_bucket = True
                    break
                if operation == STORAGE_LENS_TYPE:
                    is_storage_lens = True
                    break
            if not is_bucket:
                if is_storage_lens:
                    new_type = STORAGE_LENS_TYPE
                else:
                    new_type = record['tax_type'] or record[
                        'product_family'] or record['usage_type']
                if not change_resources.get(new_type):
                    change_resources[new_type] = []
                change_resources[new_type].append(record['_id'])
        return change_resources

    def check_usage_resources(
            self, ca_id, usage_resources, change_resources=None):
        usage_conditions = []
        for resource in usage_resources:
            try:
                product_code, operation, region = resource.split(' ')
                usage_conditions.append({
                    'lineItem/ProductCode': product_code,
                    'lineItem/Operation': operation,
                    'product/region': region
                })
            except ValueError:
                LOG.warning('Usage resource - split error, ca_id %s, '
                            'cloud_resource_id %s', ca_id, resource)
                usage_resources.remove(resource)
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        '$or': usage_conditions
                    }
            },
            {
                '$group':
                    {
                        '_id':
                            {
                                'product_code': '$lineItem/ProductCode',
                                'operation': '$lineItem/Operation',
                                'region': '$product/region'
                            },
                        'resource_id': {'$first': '$resource_id'},
                        'raw_resource_id': {'$first': '$lineItem/ResourceId'},
                        'tax_type': {'$first': '$lineItem/TaxType'},
                        'product_family': {'$first': '$product/productFamily'},
                        'usage_type': {'$first': '$lineItem/UsageType'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = {}
        for record in resources_info:
            if record['resource_id'] or record['raw_resource_id'] or record['tax_type']:
                LOG.warning('Usage resource - unexpected fields, ca_id %s, '
                            'details: %s', ca_id, record)
            new_type = record['tax_type'] or record[
                'product_family'] or record['usage_type']
            if not change_resources.get(new_type):
                change_resources[new_type] = []
            resource_id = ' '.join([record['_id']['product_code'],
                                    record['_id']['operation'],
                                    record['_id']['region']])
            change_resources[new_type].append(resource_id)
            try:
                usage_resources.remove(resource_id)
            except ValueError:
                LOG.warning('Usage resource - ca_id %s, removed unexpected '
                            'resource_id %s', ca_id, resource_id)
        if usage_resources:
            LOG.warning('Usage resources - not all resources have been '
                        'processed, ca_id %s, resources: %s',
                        ca_id, usage_resources)
        return change_resources

    def check_tax_resources(self, ca_id, tax_resources, change_resources=None):
        tax_conditions = []
        for resource in tax_resources:
            try:
                tax_type, product_name = resource.split(' ', 1)
                tax_conditions.append({
                    'lineItem/TaxType': tax_type,
                    'product/ProductName': product_name
                })
            except ValueError:
                LOG.warning('Tax resource - split error, ca_id %s, '
                            'cloud_resource_id %s', ca_id, resource)
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        '$or': tax_conditions
                    }
            },
            {
                '$group':
                    {
                        '_id':
                            {
                                'tax_type': '$lineItem/TaxType',
                                'product_name': '$lineItem/ProductName'
                            },
                        'resource_id': {'$first': '$resource_id'},
                        'raw_resource_id': {'$first': '$lineItem/ResourceId'},
                        'product_family': {'$first': '$product/productFamily'},
                        'usage_type': {'$first': '$lineItem/UsageType'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = {}
        for record in resources_info:
            if record['resource_id'] or record['raw_resource_id']:
                LOG.warning('Tax resource - unexpected fields, ca_id %s, '
                            'details: %s', ca_id, record)
            new_type = record['_id']['tax_type'] or record[
                'product_family'] or record['usage_type']
            if not change_resources.get(new_type):
                change_resources[new_type] = []
            resource_id = ' '.join([record['_id']['tax_type'],
                                    record['_id']['product_name']])
            change_resources[new_type].append(resource_id)
            try:
                tax_resources.remove(resource_id)
            except ValueError:
                LOG.warning('Tax resource - ca_id %s, removed unexpected '
                            'resource_id %s', ca_id, resource_id)
        if tax_resources:
            LOG.warning('Tax resources - not all resources have been '
                        'processed, ca_id %s, resources: %s',
                        ca_id, tax_resources)
        return change_resources

    def upgrade(self):
        _, organization_list = self.rest_cl.organization_list()
        organizations = organization_list['organizations']
        org_len = len(organizations)
        count = 0
        new_types = set()
        for org in organizations:
            if org['is_demo']:
                continue
            _, cloud_acc_list = self.rest_cl.cloud_account_list(org['id'],
                                                                type='aws_cnr')
            ca_ids = [x['id'] for x in cloud_acc_list['cloud_accounts']]
            for ca_id in ca_ids:
                bucket_ids = [
                    x['cloud_resource_id'] for x in self.mongo_resources.find({
                        'cloud_account_id': ca_id,
                        'resource_type': 'Bucket'})]
                resources_with_id = []
                usage_resources = []
                tax_resources = []
                for bucket_id in bucket_ids:
                    if ' ' not in bucket_id:
                        resources_with_id.append(bucket_id)
                    elif bucket_id.startswith(USAGE_NAME):
                        usage_resources.append(bucket_id)
                    else:
                        tax_resources.append(bucket_id)
                if resources_with_id:
                    change_resources = self.check_resources_with_id(
                        ca_id, resources_with_id)
                if usage_resources:
                    change_resources = self.check_usage_resources(
                        ca_id, usage_resources, change_resources)
                if tax_resources:
                    change_resources = self.check_tax_resources(
                        ca_id, tax_resources, change_resources)
                updates = []
                for new_type, resource_ids in change_resources.items():
                    updates.append(UpdateMany(
                        filter={
                            'cloud_account_id': ca_id,
                            'cloud_resource_id': {'$in': resource_ids}
                        }, update={'$set': {'resource_type': new_type}}))
                    new_types.add(new_type)
                if updates:
                    self.mongo_resources.bulk_write(updates)
                    self.mongo_expenses.bulk_write(updates)
            count += 1
            LOG.info('Processed %s organization out of %s', count, org_len)
        LOG.info('Processing is completed, fake buckets are converted to the '
                 'following types: %s', new_types)

    def downgrade_check_resources_with_id(
            self, ca_id, resources_with_id, change_resources=None):
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        'resource_id': {'$in': resources_with_id}
                    }
            },
            {
                '$group':
                    {
                        '_id': '$resource_id',
                        'product': {'$first': '$lineItem/ProductCode'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = []
        for record in resources_info:
            if CHECKED_PRODUCT in record['product']:
                change_resources.append(record['_id'])
        return change_resources

    def downgrade_check_usage_resources(
            self, ca_id, usage_resources, change_resources=None):
        usage_conditions = []
        for resource in usage_resources:
            try:
                product_code, operation, region = resource.split(' ')
                usage_conditions.append({
                    'lineItem/ProductCode': product_code,
                    'lineItem/Operation': operation,
                    'product/region': region
                })
            except ValueError:
                LOG.warning('Usage resource - split error, ca_id %s, '
                            'cloud_resource_id %s', ca_id, resource)
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        '$or': usage_conditions
                    }
            },
            {
                '$group':
                    {
                        '_id':
                            {
                                'product_code': '$lineItem/ProductCode',
                                'operation': '$lineItem/Operation',
                                'region': '$product/region'
                            },
                        'product': {'$first': '$lineItem/ProductCode'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = []
        for record in resources_info:
            if CHECKED_PRODUCT in record['product']:
                resource_id = ' '.join([record['_id']['product_code'],
                                        record['_id']['operation'],
                                        record['_id']['region']])
                change_resources.append(resource_id)
        return change_resources

    def downgrade_check_tax_resources(
            self, ca_id, tax_resources, change_resources=None):
        tax_conditions = []
        for resource in tax_resources:
            try:
                tax_type, product_name = resource.split(' ', 1)
                tax_conditions.append({
                    'lineItem/TaxType': tax_type,
                    'product/ProductName': product_name
                })
            except ValueError:
                LOG.warning('Tax resource - split error, ca_id %s, '
                            'cloud_resource_id %s', ca_id, resource)
        pipeline = [
            {
                '$match':
                    {
                        'cloud_account_id': ca_id,
                        '$or': tax_conditions
                    }
            },
            {
                '$group':
                    {
                        '_id':
                            {
                                'tax_type': '$lineItem/TaxType',
                                'product_name': '$lineItem/ProductName'
                            },
                        'product': {'$first': '$lineItem/ProductCode'}
                    }
            }
        ]
        resources_info = self.mongo_raw.aggregate(pipeline)
        if not change_resources:
            change_resources = {}
        for record in resources_info:
            if CHECKED_PRODUCT in record['product']:
                resource_id = ' '.join([record['_id']['tax_type'],
                                        record['_id']['product_name']])
                change_resources.append(resource_id)
        return change_resources

    def downgrade(self):
        _, organization_list = self.rest_cl.organization_list()
        organizations = organization_list['organizations']
        org_len = len(organizations)
        count = 0
        for org in organizations:
            if org['is_demo']:
                continue
            _, cloud_acc_list = self.rest_cl.cloud_account_list(org['id'],
                                                                type='aws_cnr')
            ca_ids = [x['id'] for x in cloud_acc_list['cloud_accounts']]
            for ca_id in ca_ids:
                potential_bucket_ids = [
                    x['cloud_resource_id'] for x in self.mongo_resources.find({
                        'cloud_account_id': ca_id,
                        'resource_type': {'$nin': NOT_FAKE_BUCKETS_TYPES}})]
                resources_with_id = []
                usage_resources = []
                tax_resources = []
                for resource_id in potential_bucket_ids:
                    if ' ' not in resource_id:
                        resources_with_id.append(resource_id)
                    elif resource_id.startswith(USAGE_NAME):
                        usage_resources.append(resource_id)
                    else:
                        tax_resources.append(resource_id)
                change_resources = self.downgrade_check_resources_with_id(
                    ca_id, resources_with_id)
                change_resources = self.downgrade_check_usage_resources(
                    ca_id, usage_resources, change_resources)
                change_resources = self.downgrade_check_tax_resources(
                    ca_id, tax_resources, change_resources)
                self.mongo_resources.update_many(
                    filter={
                        'cloud_account_id': ca_id,
                        'cloud_resource_id': {'$in': change_resources}
                    }, update={'$set': {'resource_type': BUCKET_TYPE}})
                self.mongo_expenses.update_many(
                    filter={
                        'cloud_account_id': ca_id,
                        'cloud_resource_id': {'$in': change_resources}
                    }, update={'$set': {'resource_type': BUCKET_TYPE}})
            count += 1
            LOG.info('Processed %s organization out of %s', count, org_len)
