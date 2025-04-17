from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        self.db.runset.update_many(
            {},
            {"$set": {"image": ""}}
        )

    def downgrade(self):
        pass
