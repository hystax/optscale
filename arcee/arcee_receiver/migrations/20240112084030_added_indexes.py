"""
create indexes in arcee db
indexes_map:
    {
        collection_name: {
            index_name: (field_list, partial_param_list)
        },
    }
"""
from mongodb_migrations.base import BaseMigration

INDEXES = {
    'application': {
        'Token': (['token'], [])
    },
    'console': {
        'RunId': (['run_id'], [])
    },
    'dataset': {
        'Token': (['token'], [])
    },
    'goal': {
        'Token': (['token'], [])
    },
    'leaderboard': {
        'TokenApplicationId': (['token', 'application_id'], [])
    },
    'leaderboard_dataset': {
        'TokenApplicationId': (['token', 'application_id'], [])
    },
    'log': {
        'Run': (['run'], [])
    },
    'milestone': {
        'RunId': (['run_id'], [])
    },
    'platform': {
        'InstanceId': (['instance_id'], [])
    },
    'proc_data': {
        'RunId': (['run_id'], []),
        'InstanceId': (['instance_id'], [])
    },
    'run': {
        'ApplicationId': (['application_id'], []),
        'RunsetId': (['runset_id'], ['runset_id'])
    },
    'stage': {
        'RunId': (['run_id'], [])
    },
    'token': {
        'Token': (['token'], [])
    }
}


class Migration(BaseMigration):
    def upgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name, index in indexes.items():
                if index_name in existing_indexes:
                    continue
                keys, partial_keys = index
                index_info = {
                    'name': index_name,
                    'background': True
                }
                if partial_keys:
                    index_info['partialFilterExpression'] = {
                        partial_key: {'$exists': True}
                        for partial_key in partial_keys
                    }
                collection.create_index(
                    [(key, 1) for key in keys], **index_info
                )

    def downgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name in indexes.keys():
                if index_name in existing_indexes:
                    collection.drop_index(index_name)
