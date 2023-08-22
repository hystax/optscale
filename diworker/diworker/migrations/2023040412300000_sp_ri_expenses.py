import logging
from clickhouse_driver import Client as ClickHouseClient
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from diworker.diworker.importers.aws import AWSReportImporter
from diworker.diworker.migrations.base import BaseMigration
from pymongo import UpdateOne
from optscale_client.rest_api_client.client_v2 import Client as RestClient

"""
Regenerate expenses for Reserved Instances and Savings Plan resources:
1. find all RI/SP raw expenses
2. update resource_id for each RI/SP raw expense
3. delete old resources for RI/SP expenses
4. delete clean expenses for deleted resources
5. create new RI/SP resources
6. generate clean expenses for new resources
7. regenerate clean expenses for affected resources
"""

LOG = logging.getLogger(__name__)

CHUNK_SIZE = 200
RESOURCE_TYPE_RESOURCE_ID_FIELD = {
    'ri': 'reservation/ReservationARN',
    'sp': 'savingsPlan/SavingsPlanARN',
}
RAW_EXPENSES_CHUNK_SIZE = 10000


class Migration(BaseMigration):
    def __init__(self, config_cl, db):
        super().__init__(config_cl, db)
        self._clickhouse_cl = None

    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    @property
    def mongo_resources(self):
        return self.db.resources

    @property
    def mongo_temp_table(self):
        # temporary table for storing handled cloud accounts
        return self.db.migration_2023040412300000

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def clickhouse_cl(self):
        if self._clickhouse_cl is None:
            user, password, host, db_name = self.config_cl.clickhouse_params()
            self._clickhouse_cl = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_cl

    def get_cloud_accounts_ids(self):
        cloud_accounts_ids = set()
        _, organizations = self.rest_cl.organization_list({
            'with_connected_accounts': True, 'is_demo': False})
        for org in organizations['organizations']:
            _, accounts = self.rest_cl.cloud_account_list(
                org['id'], type='aws_cnr')
            for cloud_account in accounts['cloud_accounts']:
                if cloud_account['auto_import']:
                    cloud_accounts_ids.add(cloud_account['id'])
        return cloud_accounts_ids

    def delete_old_mongo_resources(self, cloud_account_id, cloud_resource_ids):
        LOG.info('Deleting old resources for cloud account: %s' % (
            cloud_account_id))
        count = 0
        resources_ids = set()
        for i in range(0, len(cloud_resource_ids), CHUNK_SIZE):
            resources = self.mongo_resources.find({
                'cloud_account_id': cloud_account_id,
                'cloud_resource_id': {
                    '$in': cloud_resource_ids[i:i+CHUNK_SIZE]}})
            resources_ids.update(r['_id'] for r in resources)
            result = self.mongo_resources.delete_many(
                {'_id': {'$in': list(resources_ids)}})
            count += result.deleted_count
        LOG.info('Deleted %s resources. Cloud resources ids: %s' % (
            count, cloud_resource_ids))
        return list(resources_ids)

    def delete_clickhouse_expenses(self, cloud_account_id, resource_ids):
        LOG.info('Deleting clickhouse expenses for %s resources: %s' % (
            len(resource_ids), resource_ids))
        self.clickhouse_cl.execute(
            """ALTER TABLE expenses DELETE
               WHERE cloud_account_id=%(ca_id)s
                 AND resource_id IN %(res_ids)s""",
            params={'ca_id': cloud_account_id, 'res_ids': resource_ids})

    @staticmethod
    def get_months(start_date):
        months_starts = []
        end_date = datetime.utcnow()
        while start_date < end_date:
            months_starts.append(start_date)
            start_date = start_date + relativedelta(months=1)
        months_starts.append(end_date)
        return months_starts

    def get_resource_id_expenses(self, cloud_account_id, cloud_resource_ids,
                                 min_date):
        result = defaultdict(list)
        months_starts = self.get_months(min_date)
        for i in range(0, len(months_starts) - 1):
            start_date = months_starts[i]
            end_date = months_starts[i + 1]
            LOG.info('Getting expenses for resources: %s - %s' % (
                start_date, end_date))
            raw_groups = self.mongo_raw.aggregate([
                {'$match': {'cloud_account_id': cloud_account_id,
                            'resource_id': {'$in': cloud_resource_ids},
                            'start_date': {'$gte': start_date,
                                           '$lt': end_date}}},
                {'$group': {
                    '_id': {'resource_id': '$resource_id',
                            'start': {
                                'day': {'$dayOfMonth': '$start_date'},
                                'month': {'$month': '$start_date'},
                                'year': {'$year': '$start_date'}},
                            'lineItem/ResourceId': '$lineItem/ResourceId'
                            },
                    'expenses': {'$push': '$$ROOT'}}}
            ], allowDiskUse=True)
            for group in raw_groups:
                result[group['_id']['resource_id']].extend(group['expenses'])
        return result

    def clickhouse_optimize(self):
        LOG.info('Optimizing clickhouse expenses')
        self.clickhouse_cl.execute('OPTIMIZE TABLE expenses FINAL')

    def handle_raw_expenses(self, resource_type, raw_expenses_ids,
                            update_count, old_cloud_res_ids, new_cloud_res_ids,
                            affected_cloud_res_ids, min_date):
        resource_id_field = RESOURCE_TYPE_RESOURCE_ID_FIELD[resource_type]
        update_raw_bulk = []
        ri_sp_expenses = self.mongo_raw.find({
            '_id': {'$in': raw_expenses_ids}})
        for expense in ri_sp_expenses:
            item_type = expense['lineItem/LineItemType']
            resource_id = expense.get('resource_id')
            if item_type in ['DiscountedUsage', 'Credit']:
                continue
            elif item_type == 'SavingsPlanCoveredUsage':
                # SavingsPlanCoveredUsage expense has id of a valid resource as
                # 'resource_id', so these resources shouldn't be deleted, but
                # require regenerating of clean expenses
                affected_cloud_res_ids.add(resource_id)
            else:
                # old resources to delete
                if resource_id:
                    old_cloud_res_ids.add(resource_id)
            offer_id = expense[resource_id_field]
            expense['resource_id'] = offer_id
            new_cloud_res_ids.add(offer_id)
            if min_date > expense['start_date']:
                min_date = expense['start_date']
            update_raw_bulk.append(UpdateOne({'_id': expense['_id']},
                                             {'$set': expense}))
            if len(update_raw_bulk) >= CHUNK_SIZE:
                self.mongo_raw.bulk_write(update_raw_bulk)
                update_count += len(update_raw_bulk)
                update_raw_bulk = []
        if update_raw_bulk:
            self.mongo_raw.bulk_write(update_raw_bulk)
            update_count += len(update_raw_bulk)
        return (update_count, old_cloud_res_ids, new_cloud_res_ids,
                affected_cloud_res_ids, min_date)

    def process(self, cloud_account_id, resource_type):
        LOG.info('Processing %s expenses for cloud account %s' % (
            resource_type, cloud_account_id))
        importer = AWSReportImporter(cloud_account_id, self.rest_cl,
                                     self.config_cl, self.mongo_raw,
                                     self.mongo_resources, self.clickhouse_cl,
                                     recalculate=True)
        resource_id_field = RESOURCE_TYPE_RESOURCE_ID_FIELD[resource_type]
        ri_sp_expenses = list(
            x['_id'] for x in self.mongo_raw.find({
                'cloud_account_id': cloud_account_id,
                resource_id_field: {'$regex': '(.*)'}}, {'_id': 1}))
        old_cloud_res_ids = set()
        new_cloud_res_ids = set()
        affected_cloud_res_ids = set()
        min_date = datetime.utcnow()
        update_count = 0
        for i in range(0, len(ri_sp_expenses), RAW_EXPENSES_CHUNK_SIZE):
            raw_expenses_ids_chunk = ri_sp_expenses[i:i+RAW_EXPENSES_CHUNK_SIZE]
            (update_count, old_cloud_res_ids, new_cloud_res_ids,
             affected_cloud_res_ids, min_date) = self.handle_raw_expenses(
                resource_type, raw_expenses_ids_chunk, update_count,
                old_cloud_res_ids, new_cloud_res_ids, affected_cloud_res_ids,
                min_date)
        LOG.info('Updated %s raw expenses' % update_count)

        deleted_resources_ids = self.delete_old_mongo_resources(
            cloud_account_id, list(old_cloud_res_ids))
        for i in range(0, len(deleted_resources_ids), CHUNK_SIZE):
            self.delete_clickhouse_expenses(
                cloud_account_id, deleted_resources_ids[i:i + CHUNK_SIZE])
        LOG.info('Finished deleting old resources and expenses')

        cloud_res_ids_to_regen_exp = list(new_cloud_res_ids) + list(
            affected_cloud_res_ids)
        LOG.info('Will generate new clean expenses for %s resources' % len(
            cloud_res_ids_to_regen_exp))
        for i in range(0, len(cloud_res_ids_to_regen_exp), CHUNK_SIZE):
            LOG.info('Started processing for chunk %s/%s' % (
                i+1, len(cloud_res_ids_to_regen_exp)))
            cloud_res_id_expenses_chunk = self.get_resource_id_expenses(
                cloud_account_id, cloud_res_ids_to_regen_exp[i:i + CHUNK_SIZE],
                min_date)
            LOG.info('Generating new clean expenses for %s resources: %s' % (
                len(cloud_res_id_expenses_chunk),
                list(cloud_res_id_expenses_chunk.keys())))
            importer.save_clean_expenses(cloud_account_id,
                                         cloud_res_id_expenses_chunk)
        self.mongo_temp_table.insert_one({
            'cloud_account_id': cloud_account_id,
            'resource_type': resource_type,
        })
        LOG.info('Finished generating new resources and expenses')

    def upgrade(self):
        cloud_accounts_ids = self.get_cloud_accounts_ids()
        for i, cloud_account_id in enumerate(cloud_accounts_ids):
            LOG.info('Started processing for cloud account: %s (%s/%s)' % (
                cloud_account_id, i+1, len(cloud_accounts_ids)))
            cloud_acc_handled = self.mongo_temp_table.find({
                'cloud_account_id': cloud_account_id})
            processed_resource_types = set(x['resource_type']
                                           for x in cloud_acc_handled)
            for resource_type in ['ri', 'sp']:
                if resource_type not in processed_resource_types:
                    self.process(cloud_account_id, resource_type)
                else:
                    LOG.info('Skipping %s expenses for cloud account %s' % (
                        resource_type, cloud_account_id))
        self.clickhouse_optimize()
        try:
            self.mongo_temp_table.drop()
        except Exception as exc:
            LOG.warning('Failed to drop temp table: %s' % str(exc))

    def downgrade(self):
        pass
