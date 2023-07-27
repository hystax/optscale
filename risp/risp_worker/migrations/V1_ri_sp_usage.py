from risp_worker.migrations.base import MigrationBase


class Migration(MigrationBase):
    def upgrade(self):
        query = """CREATE TABLE IF NOT EXISTS ri_sp_usage (
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
                               offer_id, offer_type)"""
        self.clickhouse_client.execute(query)
