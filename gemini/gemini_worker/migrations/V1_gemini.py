from gemini.gemini_worker.migrations.base import MigrationBase


class Migration(MigrationBase):
    def upgrade(self):
        query = """
                CREATE TABLE IF NOT EXISTS gemini (
                    id String,
                    tag String,
                    bucket String,
                    key String,
                    size Int64
                )
                ENGINE = MergeTree
                ORDER BY (id, tag, bucket, key)
                """
        self.clickhouse_client.execute(query)
