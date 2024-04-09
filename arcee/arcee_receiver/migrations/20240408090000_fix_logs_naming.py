import logging
from mongodb_migrations.base import BaseMigration


LOG = logging.getLogger(__name__)

COLL_FIELDS_MAP = {
    'log': {
        'run': 'run_id',
        'time': 'timestamp'
    }
}


class Migration(BaseMigration):

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

    def upgrade(self):
        self.rename_fields(reverse=False)

    def downgrade(self):
        self.rename_fields(reverse=True)
