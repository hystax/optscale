from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def upgrade(self):
        self.db.dataset.update_many({}, {"$set": {
            "training_set": None,
            "validation_set": None,
            "timespan_from": None,
            "timespan_to": None
        }})

    def downgrade(self):
        self.db.dataset.update_many({}, {"$unset": {
            "training_set": "",
            "validation_set": "",
            "timespan_from": "",
            "timespan_to": ""
        }})
