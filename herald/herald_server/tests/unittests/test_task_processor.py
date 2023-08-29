import uuid
from unittest.mock import patch

import time

from herald.herald_server.controllers.notification import NotificationController
from herald.herald_server.models.db_base import BaseDB
from herald.herald_server.models.db_factory import DBFactory, DBType
from herald.herald_server.processors.main import MainProcessor
from herald.herald_server.tests.unittests.test_herald_base import TestHeraldBase


class TestTaskProcessor(TestHeraldBase):
    def setUp(self, *args):
        super().setUp()
        self.user_id = str(uuid.uuid4())

        self.mail_reaction = {
            'type': 'EMAIL',
            'payload': '{"email":"test@mail.com"}'
        }

        self.test_event = {
            'object_type': 'device',
            'object_id': '123',
            'class': 'INITIAL_REPLICATION_FAILED',
            'level': 'INFO',
            'ack': False
        }

        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        self.notification_controller = NotificationController(session)

    def _create_notification(self, filter, user_id=None):
        user_id = user_id or self.user_id

        patch('herald.herald_server.handlers.v1.base.BaseAuthHandler.get_meta_by_token',
              return_value={
                  'user_id': user_id,
                  'valid_until': time.time() * 2
              }).start()

        self.client.notification_create(
            user_id, 'First notification', filter,
            reactions=[self.mail_reaction])

    @patch("optscale_client.auth_client.client_v2.Client.authorize_user_list")
    def test_event_reactions(self, p_authorize_users):

        p_authorize_users.return_value = 200, {
            self.user_id: {'POLL_EVENT'}
        }

        self._create_notification('level:INFO')
        self._create_notification('level:ERROR')
        self._create_notification('object_type:cs')
        self._create_notification('object_id:123')

        test_event = {
            'level': 'INFO'
        }

        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(1, len(reactions))

        test_event['level'] = 'ERROR'
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(1, len(reactions))

        test_event['object_type'] = 'cs'
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(2, len(reactions))

        test_event['object_id'] = '123'
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(3, len(reactions))

        # create another user
        self.user2_id = str(uuid.uuid4())
        self._create_notification('level:ERROR', self.user2_id)
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        # second user doesn't have POLL_EVENT for this object
        self.assertEqual(3, len(reactions))

        # give second user access to object
        p_authorize_users.return_value = 200, {
            self.user_id: {'POLL_EVENT'},
            self.user2_id: {'POLL_EVENT'}
        }
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(4, len(reactions))

        # no one has access
        p_authorize_users.return_value = 200, {
            self.user_id: set()
        }
        reactions = self.notification_controller.event_user_reactions(
            test_event)
        self.assertEqual(0, len(reactions))

    @patch("optscale_client.auth_client.client_v2.Client.authorize_user_list")
    def test_ack_events(self, p_authorize_users):
        p_authorize_users.return_value = 200, {
            self.user_id: {'POLL_EVENT'}
        }

        self._create_notification('ack:true')

        reactions = self.notification_controller.event_user_reactions(
            self.test_event)
        self.assertEqual(0, len(reactions))

        self.test_event['ack'] = True
        reactions = self.notification_controller.event_user_reactions(
            self.test_event)
        self.assertEqual(1, len(reactions))
