from mongodb_migrations.base import BaseMigration

NEW_INDEX_NAME = 'LeaderboardTemplateId'


class Migration(BaseMigration):

    def upgrade(self):
        self.db.leaderboard.rename('leaderboard_template')
        self.db.leaderboard_dataset.rename('leaderboard')

        leaderboard_templates = self.db.leaderboard_template.find({}, [])
        for leaderboard_template in leaderboard_templates:
            self.db.leaderboard.update_many(
                {'leaderboard_id': leaderboard_template['_id']},
                {"$rename": {
                    "leaderboard_id": "leaderboard_template_id"
                }}
            )

        self.db.leaderboard.create_index(
            [('leaderboard_template_id', 1)],
            name=NEW_INDEX_NAME,
            background=True
        )

    def downgrade(self):
        self.db.leaderboard.rename('leaderboard_dataset')
        self.db.leaderboard_template.rename('leaderboard')

        leaderboards = self.db.leaderboard.find({}, [])
        for leaderboard in leaderboards:
            self.db.leaderboard_dataset.update_many(
                {'leaderboard_template_id': leaderboard['_id']},
                {"$rename": {
                    "leaderboard_template_id": "leaderboard_id"
                }}
            )

        self.db.leaderboard_dataset.drop_index(NEW_INDEX_NAME)
