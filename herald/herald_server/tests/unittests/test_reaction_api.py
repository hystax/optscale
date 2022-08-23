import uuid
import string
import random
from unittest.mock import patch

import time

from herald_server.tests.unittests.test_herald_base import TestHeraldBase


class TestReactionApi(TestHeraldBase):
    def setUp(self, *args):
        super().setUp()
        self.user_id = str(uuid.uuid4())

        patch('herald_server.handlers.v1.base.BaseAuthHandler.get_meta_by_token',
              return_value={
                  'user_id': self.user_id,
                  'valid_until': time.time() * 2
              }).start()

        self.mail_reaction = {
            'type': 'EMAIL',
            'payload': '{"email":"test@mail.com"}'
        }

        self.sms_reaction = {
            'type': 'SMS',
            'payload': '{"phone":"+11234567890"}'
        }
        self.success_filter = 'level:SUCCESS'

    def test_reaction_invalid_inputs(self):
        invalid_reactions = [
            {},
            {'type': 'BAD_TYPE', 'payload': '{"email":"test@mail.com"}'},
            {'type': 'EMAIL'},
            {'type': 'EMAIL', 'payload': 'bad payload'},
            {'type': 'SMS'},
        ]

        for invalid_reaction in invalid_reactions:
            code, _ = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=[invalid_reaction])
            self.assertEqual(400, code)

    def test_edit_reaction(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])

        code, updated_notification = self.client.notification_update(
            notification['id'], reactions=[self.sms_reaction])

        self.assertEqual(200, code)
        self.assertEqual(1, len(updated_notification['reactions']))

    def test_add_reaction(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])

        code, updated_notification = self.client.notification_update(
            notification['id'], reactions=[
                self.mail_reaction,
                self.sms_reaction
            ])

        self.assertEqual(200, code)
        self.assertEqual(2, len(updated_notification['reactions']))

    def test_delete_reaction(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[
                self.mail_reaction,
                self.sms_reaction
            ])

        code, updated_notification = self.client.notification_update(
            notification['id'], reactions=[self.mail_reaction])

        self.assertEqual(200, code)
        self.assertEqual(1, len(updated_notification['reactions']))

    def test_create_reaction_with_immutable(self):
        for immutable in ['id', 'deleted_at', 'created_at']:
            reaction = self.mail_reaction.copy()
            reaction[immutable] = str(uuid.uuid4())
            code, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=[reaction])
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'parameter "%s" is immutable' % immutable)

    def test_create_reaction_with_unexpected(self):
        for unexpected in ['some', 123, '']:
            reaction = self.mail_reaction.copy()
            reaction[unexpected] = str(uuid.uuid4())
            code, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=[reaction])
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'Unexpected parameters: %s' % unexpected)

    def test_create_invalid_reaction(self):
        for expected_param, expected_error in [
            ('type', 'type is required for reaction'),
                ('payload', 'payload is not provided')]:
            reaction = self.mail_reaction.copy()
            reaction.pop(expected_param)
            code, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=[reaction])
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'], expected_error)
        for reaction in [123, '', 'asdasds']:
            code, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=reaction)
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'reactions has invalid format')

    def test_create_reaction_invalid_type(self):
        reaction = self.mail_reaction.copy()
        reaction['type'] = 123
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'type should be a string')
        reaction['type'] = ''
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'type should contain 1-255 characters')

    def test_create_reaction_invalid_payload(self):
        reaction = self.mail_reaction.copy()
        reaction['payload'] = 123
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'payload should be a string')
        reaction = self.mail_reaction.copy()
        reaction['payload'] = ''
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'payload should contain 1-255 characters')
        reaction = self.mail_reaction.copy()
        reaction['payload'] = 'asd'
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         '"payload" should be a string with valid JSON')

    def test_create_reaction_invalid_name(self):
        longname = "".join(random.choice(string.ascii_lowercase)
                           for _ in range(256))
        for name in [longname, '']:
            reaction = self.mail_reaction.copy()
            reaction['name'] = name
            code, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter,
                reactions=[reaction])
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'name should contain 1-255 characters')
        reaction = self.mail_reaction.copy()
        reaction['name'] = 123
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[reaction])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'name should be a string')

    def test_create_reaction_nullable_name(self):
        self.mail_reaction['name'] = None
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])
        self.assertEqual(code, 201)
        self.assertIsNone(notification['reactions'][0]['name'])

    def test_create_reaction_with_not_dict_in_list(self):
        self.mail_reaction['name'] = None
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=["123"])
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'reactions has invalid format')

    def test_update_reaction_with_not_dict_in_list(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])

        code, updated_notification = self.client.notification_update(
            notification['id'], reactions=['123'])
        self.assertEqual(code, 400)
        self.assertEqual(updated_notification['error']['reason'],
                         'reactions has invalid format')
