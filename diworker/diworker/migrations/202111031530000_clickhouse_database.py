from diworker.diworker.migrations.base import BaseMigration
from clickhouse_driver import Client as ClickHouseClient


"""
Adds a clickhouse database for expenses.
"""


class Migration(BaseMigration):
    def _get_clickhouse_client(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user)

    def upgrade(self):
        clickhouse_client = self._get_clickhouse_client()
        clickhouse_client.execute(
            """
            CREATE TABLE expenses (
                cloud_account_id String,
                resource_id String,
                date DateTime,
                cost Float64,
                sign Int8)
            ENGINE = CollapsingMergeTree(sign)
            PARTITION BY toYYYYMM(date)
            ORDER BY (cloud_account_id, date, resource_id)
            """)

    def downgrade(self):
        clickhouse_client = self._get_clickhouse_client()
        clickhouse_client.execute('DROP TABLE IF EXISTS expenses')
