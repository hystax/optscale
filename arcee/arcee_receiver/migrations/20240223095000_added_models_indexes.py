"""
create indexes in model and model_version collections
indexes_map:
    {
        collection_name: {
            index_name: field_list
        }
    }
"""
from mongodb_migrations.base import BaseMigration

INDEXES = {
    'model': {
        'TokenKey': ['token', 'key']
    },
    'model_version': {
        'ModelIdRunId': ['model_id', 'run_id']
    }
}


class Migration(BaseMigration):
    def upgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name, index_fields in indexes.items():
                if index_name in existing_indexes:
                    continue
                index_info = {
                    'name': index_name,
                    'background': True
                }
                collection.create_index(
                    [(key, 1) for key in index_fields], **index_info
                )

    def downgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name in indexes.keys():
                if index_name in existing_indexes:
                    collection.drop_index(index_name)
