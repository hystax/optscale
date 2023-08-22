from diworker.diworker.migrations.base import BaseMigration
from clickhouse_driver import Client as ClickHouseClient

"""
Adds a clickhouse traffic expenses table.
"""
AZURE_INDEX_NAME = 'AzureMeterCategory'
AZURE_FIELD_LIST = [
    'cloud_account_id', 'start_date', 'meter_details.meter_category'
]
AZURE_PARTIAL_FILTER_EXPRESSION = {
    'meter_details.meter_category': {'$exists': True},
}
ALIBABA_INDEX_NAME = 'AlibabaBillingItemCode'
ALIBABA_FIELD_LIST = [
    'cloud_account_id', 'start_date', 'BillingItemCode'
]
ALIBABA_PARTIAL_FILTER_EXPRESSION = {
    'BillingItemCode': {'$exists': True},
}


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def _get_clickhouse_client(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user)

    def upgrade(self):
        clickhouse_client = self._get_clickhouse_client()
        clickhouse_client.execute(
            """
            CREATE TABLE traffic_expenses (
                cloud_account_id String,
                resource_id String,
                date DateTime,
                type Enum8('outbound' = 1, 'inbound' = 2),
                from String,
                to String,
                usage Float64,
                cost Float64,
                sign Int8)
            ENGINE = CollapsingMergeTree(sign)
            PARTITION BY toYYYYMM(date)
            ORDER BY (cloud_account_id, resource_id, date, from, to)
            """)
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        if AZURE_INDEX_NAME not in existing_indexes:
            self.mongo_raw.create_index(
                [(f, 1) for f in AZURE_FIELD_LIST], name=AZURE_INDEX_NAME,
                background=True,
                partialFilterExpression=AZURE_PARTIAL_FILTER_EXPRESSION,
            )
        if ALIBABA_INDEX_NAME not in existing_indexes:
            self.mongo_raw.create_index(
                [(f, 1) for f in ALIBABA_FIELD_LIST], name=ALIBABA_INDEX_NAME,
                background=True,
                partialFilterExpression=ALIBABA_PARTIAL_FILTER_EXPRESSION,
            )

    def downgrade(self):
        clickhouse_client = self._get_clickhouse_client()
        clickhouse_client.execute('DROP TABLE IF EXISTS traffic_expenses')
        existing_indexes = [x['name'] for x in self.mongo_raw.list_indexes()]
        for index in [AZURE_INDEX_NAME, ALIBABA_INDEX_NAME]:
            if index in existing_indexes:
                self.mongo_raw.drop_index(index)
