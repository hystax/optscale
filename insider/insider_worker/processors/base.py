class BasePriceProcessor(object):
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client

    @property
    def discoveries(self):
        raise NotImplementedError()

    @property
    def prices(self):
        raise NotImplementedError()

    def get_last_discovery(self):
        raise NotImplementedError()

    def process_prices(self):
        raise NotImplementedError()
