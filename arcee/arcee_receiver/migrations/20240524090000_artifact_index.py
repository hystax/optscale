from mongodb_migrations.base import BaseMigration


INDEX_NAME = 'RunIdCreatedAtDt'
INDEX_FIELDS = ['run_id', '_created_at_dt']


class Migration(BaseMigration):
    def existing_indexes(self):
        return [x['name'] for x in self.db.artifact.list_indexes()]

    def upgrade(self):
        if INDEX_NAME not in self.existing_indexes():
            self.db.artifact.create_index(
                    [(key, 1) for key in INDEX_FIELDS],
                    name=INDEX_NAME,
                    background=True
                )

    def downgrade(self):
        if INDEX_NAME in self.existing_indexes():
            self.db.artifact.drop_index(INDEX_NAME)
