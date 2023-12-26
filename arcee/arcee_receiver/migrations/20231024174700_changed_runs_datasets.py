from mongodb_migrations.base import BaseMigration
from pymongo import UpdateOne

BULK_SIZE = 5000


class Migration(BaseMigration):
    def upgrade(self):
        run_dataset_map = {}
        for run in self.db.run.find({'dataset_ids': {'$exists': True}}):
            run_dataset_map[run['_id']] = run['dataset_ids'][-1]
        update_operations = []
        for run_id, dataset_id in run_dataset_map.items():
            update_operations.append(UpdateOne(
                filter={
                    '_id': run_id
                },
                update={'$set': {'dataset_id': dataset_id}},
            ))
        if update_operations:
            self.db.run.update_many({}, {'$unset': {'dataset_ids': ""}})
            for i in range(0, len(update_operations), BULK_SIZE):
                bulk = update_operations[i:i + BULK_SIZE]
            self.db.run.bulk_write(bulk)

    def downgrade(self):
        # there is no need to revert dataset_ids -> dataset_id transition
        pass
