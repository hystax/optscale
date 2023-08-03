import logging
from risp_worker.migrations.base import MigrationBase
from pymongo import UpdateOne

RES_CHUNK_SIZE = 500
CH_CHUNK_SIZE = 1000
LOG = logging.getLogger(__name__)


class Migration(MigrationBase):

    def _add_resource_ids_queries(self, change_from, change_to):
        queries_list = []
        query_template = "ALTER TABLE ri_sp_usage " \
                         "UPDATE cloud_resource_id='{0}' WHERE resource_id='{1}'"
        resource_ids = list(x[0] for x in self.clickhouse_client.execute(
            """SELECT DISTINCT resource_id FROM ri_sp_usage"""))
        for i in range(0, len(resource_ids), RES_CHUNK_SIZE):
            chunk = resource_ids[i:i+RES_CHUNK_SIZE]
            cloud_res_ids = self.mongo_client.restapi.resources.find(
                {change_from: {'$in': chunk}},
                {'_id': 1, 'cloud_resource_id': 1})
            for resource in cloud_res_ids:
                queries_list.append(query_template.format(
                    resource[change_to], resource[change_from]))
        return queries_list

    def fix_ri_sp_resource_ids(self):
        # fix mongodb cloud resources ids in resources and raw_expenses, example:
        # "arn:aws::::reserved-instances/422c3515-ffe9-4fdd-975f-10a8b5382b17" ->
        #       "422c3515-ffe9-4fdd-975f-10a8b5382b17"
        resources = list(self.mongo_client.restapi.resources.find({
            'resource_type': {'$in': ['Reserved Instances', 'Savings Plan']}},
            ['_id', 'cloud_resource_id', 'cloud_account_id']))
        chunk = []
        for r in resources:
            old_cloud_res_id = r['cloud_resource_id']
            new_cloud_res_id = old_cloud_res_id[old_cloud_res_id.find('/') + 1:]
            _id = r['_id']
            if new_cloud_res_id != old_cloud_res_id:
                self.mongo_client.restapi.raw_expenses.update_many(
                    {'cloud_account_id': r['cloud_account_id'],
                     'resource_id': old_cloud_res_id},
                    {'$set': {'resource_id': new_cloud_res_id}})
                chunk.append(UpdateOne(
                    {'_id': _id},
                    {'$set': {'cloud_resource_id': new_cloud_res_id}}))
            if len(chunk) >= RES_CHUNK_SIZE:
                self.mongo_client.restapi.resources.bulk_write(chunk)
                chunk.clear()
        if chunk:
            self.mongo_client.restapi.resources.bulk_write(chunk)

    def prepare_table(self):
        LOG.info('Preparing ri_sp_usage table')
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage
                ADD COLUMN IF NOT EXISTS
                 cloud_resource_id String DEFAULT resource_id""")
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage
                ADD COLUMN IF NOT EXISTS new_offer_id String DEFAULT SUBSTRING(
                    offer_id, POSITION(offer_id, '/') + 1)""")

        queries_list = self._add_resource_ids_queries(
            change_to='cloud_resource_id', change_from='_id')
        queries_list.append("OPTIMIZE TABLE ri_sp_usage FINAL")
        for query in queries_list:
            LOG.info('Executing query: %s' % query)
            self.clickhouse_client.execute(query)

    def copy_data_in_bulks(self):
        # copy data to new table using cloud_resource_id instead as resource_id
        LOG.info('Copying data')
        insert_query = """
                       INSERT INTO new_ri_sp_usage (
                         cloud_account_id, resource_id, date, offer_id, offer_type,
                         offer_cost, on_demand_cost, usage, sign)
                       SELECT cloud_account_id, cloud_resource_id, date, new_offer_id,
                         offer_type, offer_cost, on_demand_cost, usage, sign
                       FROM ri_sp_usage
                       WHERE offer_id=%(offer_id)s
                       ORDER BY (cloud_account_id, resource_id, date,
                         offer_id, offer_type, on_demand_cost, sign) DESC
                       """
        offer_ids = [
            x[0] for x in self.clickhouse_client.execute(
                """SELECT DISTINCT offer_id from ri_sp_usage""")]
        for i, offer_id in enumerate(offer_ids):
            LOG.info("Copying data for offer %s (%s/%s)" % (
                offer_id, i + 1, len(offer_ids)))
            count = self.clickhouse_client.execute(
                """SELECT COUNT(*) from ri_sp_usage WHERE offer_id=%(offer_id)s""",
                params={"offer_id": offer_id})[0][0]
            if count:
                for j in range(0, count, CH_CHUNK_SIZE):
                    query = insert_query + 'LIMIT %s OFFSET %s' % (
                        CH_CHUNK_SIZE, j)
                    self.clickhouse_client.execute(
                        query, params={"offer_id": offer_id})

    def create_new_table(self):
        self.clickhouse_client.execute(
            """DROP TABLE IF EXISTS new_ri_sp_usage""")
        self.clickhouse_client.execute(
            """CREATE TABLE new_ri_sp_usage (
                             cloud_account_id String,
                             resource_id String,
                             date DateTime,
                             offer_id String,
                             offer_type Enum8('ri' = 1, 'sp' = 2),
                             offer_cost Float64,
                             on_demand_cost Float64,
                             usage Float64,
                             sign Int8)
               ENGINE = CollapsingMergeTree(sign)
               PARTITION BY toYYYYMM(date)
               ORDER BY (cloud_account_id, resource_id, date,
                   offer_id, offer_type)""")

    def rename_new_table(self):
        self.clickhouse_client.execute("""DROP TABLE ri_sp_usage""")
        self.clickhouse_client.execute(
            """RENAME TABLE new_ri_sp_usage TO ri_sp_usage""")

    def upgrade(self):
        self.fix_ri_sp_resource_ids()
        self.prepare_table()
        self.create_new_table()
        self.copy_data_in_bulks()
        self.rename_new_table()
