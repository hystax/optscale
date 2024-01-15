"""
create indexes in bulldozer db
indexes_map:
    {
        collection_name: {
            index_name: field_list
        },
    }
"""
from mongodb_migrations.base import BaseMigration

INDEXES = {
    'token': {
        'Token': ['token']
    },
    'template': {
        'Token': ['token']
    },
    'runset': {
        'Token': ['token'],
        'TemplateId': ['template_id']
    },
    'runner': {
        'Token': ['token'],
        'RunsetId': ['runset_id']
    }
}


class Migration(BaseMigration):
    def upgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name, keys in indexes.items():
                if index_name in existing_indexes:
                    continue
                collection.create_index(
                    [(key, 1) for key in keys],
                    name=index_name,
                    background=True
                )

    def downgrade(self):
        for collection_name, indexes in INDEXES.items():
            collection = getattr(self.db, collection_name)
            existing_indexes = [x['name'] for x in collection.list_indexes()]
            for index_name in indexes.keys():
                if index_name in existing_indexes:
                    collection.drop_index(index_name)
