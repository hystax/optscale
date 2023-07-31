import logging
from risp_worker.migrations.base import MigrationBase

CHUNK_SIZE = 500
LOG = logging.getLogger(__name__)


class Migration(MigrationBase):

    def _add_offer_ids_to_query(self, change_from, change_to):
        queries_list = []
        query_template = "ALTER TABLE ri_sp_usage " \
                         "UPDATE cloud_offer_id='{0}' WHERE offer_id='{1}'"
        resource_ids = list(x[0] for x in self.clickhouse_client.execute(
            """SELECT DISTINCT offer_id FROM ri_sp_usage"""))
        for i in range(0, len(resource_ids), CHUNK_SIZE):
            chunk = resource_ids[i:i+CHUNK_SIZE]
            cloud_res_ids = self.mongo_client.restapi.resources.find(
                {change_from: {'$in': chunk}},
                {'_id': 1, 'cloud_resource_id': 1})
            for resource in cloud_res_ids:
                queries_list.append(query_template.format(
                    resource[change_to], resource[change_from]))
        return queries_list

    def prepare_table(self):
        # create new column `cloud_offer_id` and fill it by cloud_resource_id
        LOG.info('Preparing ri_sp_usage table')
        self.clickhouse_client.execute(
            """ALTER TABLE ri_sp_usage
                ADD COLUMN IF NOT EXISTS cloud_offer_id String DEFAULT offer_id""")
        queries_list = self._add_offer_ids_to_query(
            change_to='cloud_resource_id', change_from='_id')
        queries_list.append("OPTIMIZE TABLE ri_sp_usage FINAL")
        for query in queries_list:
            LOG.info('Executing query: %s' % query)
            self.clickhouse_client.execute(query)

    def copy_data(self):
        # copy data to new table using cloud_offer_id instead as offer_id
        LOG.info('Copying data')
        self.clickhouse_client.execute(
            """INSERT INTO new_ri_sp_usage (
                    cloud_account_id, resource_id, date, offer_id, offer_type,
                    offer_cost, on_demand_cost, usage, sign)
               SELECT cloud_account_id, resource_id, date, cloud_offer_id,
                    offer_type, offer_cost, on_demand_cost, usage, sign
               FROM ri_sp_usage""")

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
        self.prepare_table()
        self.create_new_table()
        self.copy_data()
        self.rename_new_table()
