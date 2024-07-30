from mongodb_migrations.base import BaseMigration
from pymongo import UpdateMany

FIELDS = ['grouping_tags', 'filters', 'group_by_hp', 'primary_metric',
          'other_metrics', 'dataset_coverage_rules']


class Migration(BaseMigration):

    def upgrade(self):
        leaderboards = self.db.leaderboard.find({}, FIELDS)
        updates_chunk = []
        for leaderboard in leaderboards:
            _id = leaderboard.pop('_id')
            updates_chunk.append(UpdateMany(
                filter={
                    'leaderboard_id': _id
                }, update={'$set': leaderboard}))
        if updates_chunk:
            self.db.leaderboard_dataset.bulk_write(updates_chunk)

    def downgrade(self):
        self.db.leaderboard_dataset.update_many({}, {
            '$unset': {k: '' for k in FIELDS}
        })
