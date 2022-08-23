import uuid
from unittest.mock import patch

import tornado.testing
import herald_client.client
import herald_client.client_v2
from herald_server.models.db_base import BaseDB
from herald_server.models.models import Field
from herald_server.server import make_app
from herald_server.models.db_factory import DBType, DBFactory


class TestHeraldBase(tornado.testing.AsyncHTTPTestCase):
    def get_rabbit_params(self):
        return 'root', 'pass', 'localhost', 27017

    def get_app(self):
        return make_app(DBType.Test, '127.0.0.1', 80)

    @patch('config_client.client.Client')
    @patch('herald_server.controllers.message_consumer.Consumer')
    def setUp(self, p_consumer, p_config):
        secret = str(uuid.uuid4())
        patch(
            'herald_server.controllers.base.Config').start()
        patch(
            'herald_server.controllers.message_consumer.Consumer').start()
        p_config.return_value.cluster_secret.return_value = secret
        p_config.return_value.rabbit_params.return_value = self.get_rabbit_params()
        p_config.return_value.events_queue.return_value = (
            'root', 'pass', 'localhost', 27017)
        p_consumer.return_value.publish_message.return_value = {}
        super().setUp()

        http_provider = herald_client.client.FetchMethodHttpProvider(
                self.fetch, rethrow=False)
        http_provider.token = 'token'
        http_provider.secret = secret

        self.client = herald_client.client.Client(
                http_provider=http_provider)
        self.client_v2 = herald_client.client_v2.Client(
            http_provider=http_provider)
        self._init_base_db_data()

    def _init_base_db_data(self):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()

        fields = 'object_type', 'object_id', 'class', 'level', 'ack'

        for field in fields:
            session.add(Field(name=field))

        session.commit()
        session.close()
