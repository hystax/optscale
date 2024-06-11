from mongodb_migrations.base import BaseMigration


class Migration(BaseMigration):
    def get_dataset_tokens(self):
        tokens = self.db.dataset.aggregate([{'$group': {'_id': '$token'}}])
        return list(map(lambda x: x['_id'], tokens))

    def upgrade(self):
        for token in self.get_dataset_tokens():
            self.db.dataset.update_many({'token': token}, {
                "$set": {
                    "timespan_from": None,
                    "timespan_to": None
                },
                '$unset': {
                    "training_set": "",
                    "validation_set": "",
                }
            })

    def downgrade(self):
        for token in self.get_dataset_tokens():
            self.db.dataset.update_many({'token': token}, {
                "$unset": {
                    "timespan_from": "",
                    "timespan_to": ""
                },
                '$set': {
                    "training_set": None,
                    "validation_set": None,
                }
            })
