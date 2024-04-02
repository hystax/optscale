import logging
from mongodb_migrations.base import BaseMigration

LOG = logging.getLogger(__name__)
OLD_COLLECTION = 'application'
NEW_COLLECTION = 'task'

COLL_INDEXES_MAP = {
    'leaderboard': {
        'old': ('TokenApplicationId', ['token', 'application_id']),
        'new': ('TokenTaskId', ['token', 'task_id']),
    },
    'leaderboard_dataset': {
        # leaderboard_dataset doesn't have application_id/task_id column
        'old': ('TokenApplicationId', ['token', 'application_id']),
        'new': ('Token', ['token']),
    },
    'run': {
        'old': ('ApplicationId', ['application_id']),
        'new': ('TaskId', ['task_id']),
    },
}

COLL_OLD_NEW_NAME_MAP = {
    'leaderboard': ('application_id', 'task_id'),
    'run': ('application_id', 'task_id')
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
        for collection_name, fields in COLL_OLD_NEW_NAME_MAP.items():
            collection = getattr(self.db, collection_name)
            if reverse is False:
                old_name, new_name = fields
            else:
                new_name, old_name = fields
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
