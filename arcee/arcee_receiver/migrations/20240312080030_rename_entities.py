import logging
from mongodb_migrations.base import BaseMigration


LOG = logging.getLogger(__name__)
OLD_COLLECTION = 'goal'
NEW_COLLECTION = 'metric'

COLL_FIELDS_MAP = {
    'log': {
        'run': 'run_id',
        'time': 'timestamp'
    },
    'task': {
        'goals': 'metrics'
    },
    'leaderboard': {
        'primary_goal': 'primary_metric',
        'other_goals': 'other_metrics'
    }
}

COLL_INDEXES_MAP = {
    'log': {
        'old': ('Run', ['run']),
        'new': ('RunId', ['run_id']),
    },
}


class Migration(BaseMigration):
    def rename_collection(self, old_name, new_name):
        existing_coll = [x for x in self.db.list_collection_names()]
        if new_name in existing_coll:
            LOG.info('Collection with name %s exists', new_name)
        else:
            collection = getattr(self.db, old_name)
            LOG.info('Renaming collection %s -> %s', old_name, new_name)
            collection.rename(new_name)

    def rename_fields(self, reverse=False):
        for collection_name, fields in COLL_FIELDS_MAP.items():
            collection = getattr(self.db, collection_name)
            for k, v in fields.items():
                if reverse is False:
                    old_name = k
                    new_name = v
                else:
                    old_name = v
                    new_name = k
                LOG.info('Renaming %s -> %s in %s', old_name, new_name,
                         collection_name)
                collection.update_many({}, {"$rename": {old_name: new_name}})

    def rebuilt_indexes(self, reverse=False):
        for collection_name, indexes in COLL_INDEXES_MAP.items():
            collection = getattr(self.db, collection_name)
            if reverse is False:
                old_index = indexes['old']
                new_index = indexes['new']
            else:
                old_index = indexes['new']
                new_index = indexes['old']
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            old_index_name = old_index[0]
            if old_index_name in existing_indexes:
                LOG.info('Dropping index %s', old_index_name)
                collection.drop_index(old_index_name)
            new_index_name = new_index[0]
            if new_index_name in existing_indexes:
                LOG.info('Index %s exists, skipping it', new_index_name)
            else:
                LOG.info('Building index %s', new_index_name)
                new_index_fields = new_index[1]
                index_info = {
                    'name': new_index_name,
                    'background': True
                }
                collection.create_index(
                    [(key, 1) for key in new_index_fields], **index_info
                )

    def upgrade(self):
        self.rename_collection(OLD_COLLECTION, NEW_COLLECTION)
        self.rename_fields(reverse=False)
        self.rebuilt_indexes(reverse=False)

    def downgrade(self):
        self.rename_collection(NEW_COLLECTION, OLD_COLLECTION)
        self.rename_fields(reverse=True)
        self.rebuilt_indexes(reverse=True)
