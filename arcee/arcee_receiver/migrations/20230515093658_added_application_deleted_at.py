from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        self.db.application.update_many({}, {"$set": {"deleted_at": 0}})

    def downgrade(self):
        self.db.application.delete_many({"deleted_at": {"$ne": 0}})
        self.db.application.update_many({}, {"$unset": {"deleted_at": ""}})
