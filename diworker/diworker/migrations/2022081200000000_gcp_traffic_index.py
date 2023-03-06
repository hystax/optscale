from diworker.migrations.base import BaseMigration

"""
Adds an index for searching for GCP traffic expenses.
"""
INDEX_NAME = "GcpSku"
INDEX_FIELD_LIST = ["cloud_account_id", "start_date", "sku"]
PARTIAL_FILTER_EXPRESSION = {
    "sku": {"$exists": True},
}


class Migration(BaseMigration):
    @property
    def mongo_raw(self):
        return self.db.raw_expenses

    def upgrade(self):
        existing_indexes = [x["name"] for x in self.mongo_raw.list_indexes()]
        if INDEX_NAME not in existing_indexes:
            self.mongo_raw.create_index(
                [(f, 1) for f in INDEX_FIELD_LIST],
                name=INDEX_NAME,
                background=True,
                partialFilterExpression=PARTIAL_FILTER_EXPRESSION,
            )

    def downgrade(self):
        existing_indexes = [x["name"] for x in self.mongo_raw.list_indexes()]
        if INDEX_NAME in existing_indexes:
            self.mongo_raw.drop_index(INDEX_NAME)
