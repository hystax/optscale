from mongodb_migrations.base import BaseMigration
from pymongo.operations import UpdateOne

CHUNK_SIZE = 500


class Migration(BaseMigration):

    def upgrade(self):
        updates = []
        for doc in self.db.dataset.find({'name': {'$in': [None, '']}}):
            updates.append(UpdateOne(filter={'_id': doc['_id']},
                                     update={'$set': {'name': doc['path']}}))
            if len(updates) >= CHUNK_SIZE:
                self.db.dataset.bulk_write(updates)
                updates.clear()
        if updates:
            self.db.dataset.bulk_write(updates)

    def downgrade(self):
        pass
