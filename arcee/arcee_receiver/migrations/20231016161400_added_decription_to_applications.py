from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        self.db.application.update_many({}, {"$set": {"description": None}})

    def downgrade(self):
        self.db.application.update_many({}, {"$unset": {"description": ""}})
