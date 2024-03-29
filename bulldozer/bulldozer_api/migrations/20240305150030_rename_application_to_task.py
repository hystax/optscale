import logging
from mongodb_migrations.base import BaseMigration


LOG = logging.getLogger(__name__)
COLL_OLD_NEW_NAME_MAP = {
    'template': ('application_ids', 'task_ids'),
    'runner': ('application_id', 'task_id'),
    'runset': ('application_id', 'task_id')
}


class Migration(BaseMigration):
    def rename_fields(self, collection_fields_map):
        for collection_name, fields in collection_fields_map.items():
            collection = getattr(self.db, collection_name)
            old_name, new_name = fields
            LOG.info('Renaming %s -> %s in %s', old_name, new_name,
                     collection_name)
            collection.update_many({}, {"$rename": {old_name: new_name}})

    def upgrade(self):
        self.rename_fields(COLL_OLD_NEW_NAME_MAP)

    def downgrade(self):
        collection_fields_map = {
            collection: (fields[1], fields[0])
            for collection, fields in COLL_OLD_NEW_NAME_MAP.items()
        }
        self.rename_fields(collection_fields_map)
