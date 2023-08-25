
class BaseMigration:
    def __init__(self, config_cl, db):
        self.config_cl = config_cl
        self.db = db

    @property
    def discoveries(self):
        return self.db.discoveries

    @property
    def azure_prices(self):
        return self.db.azure_prices

    def upgrade(self):
        raise NotImplementedError

    def downgrade(self):
        raise NotImplementedError
