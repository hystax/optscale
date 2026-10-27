class BasePriceProcessor(object):
    def __init__(self, mongo_client, config_client):
        self.mongo_client = mongo_client
        self.config_client = config_client

    @property
    def discoveries(self):
        raise NotImplementedError()

    @property
    def prices(self):
        raise NotImplementedError()

    def process_prices(self, last_discovery_ts):
        raise NotImplementedError()
