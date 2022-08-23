class BaseMigration():
    def __init__(self, config_cl, db):
        self.config_cl = config_cl
        self.db = db
        self._rest_cl = None

    def upgrade(self):
        raise NotImplementedError

    def downgrade(self):
        raise NotImplementedError
