import uuid
import string
import random
from unittest.mock import patch

import time

from freezegun import freeze_time

from herald.herald_server.tests.unittests.test_herald_base import TestHeraldBase


class TestNotificationApi(TestHeraldBase):
    def setUp(self, *args):
        super().setUp(*args)
        self.user_id = str(uuid.uuid4())

        patch('herald.herald_server.handlers.v1.base.BaseAuthHandler.get_meta_by_token',
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

    def check_notification_count(self, expected_count):
        code, notifications = self.client.user_notification_list(self.user_id)
        self.assertEqual(200, code)
        self.assertEqual(expected_count, len(notifications))

    def test_create_empty_notification(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter)
        self.assertEqual(201, code)
        self.assertEqual('First notification', notification['name'])
        self.assertEqual([], notification['reactions'])

    def test_create_with_reaction(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])
        self.assertEqual(201, code)
        self.assertEqual('First notification', notification['name'])
        self.assertEqual(1, len(notification['reactions']))

    def test_edit(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter)

        code, updated_notification = self.client.notification_update(
            notification['id'], name='New name')
        self.assertEqual(200, code)
        self.assertEqual('New name', updated_notification['name'])

    def test_edit_filter(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])

        code, updated_notification = self.client.notification_update(
            notification['id'], filter='level:ERROR')
        self.assertEqual(200, code)

        notification['filter'] = 'level:ERROR'
        self.assertEqual(notification, updated_notification)

    def test_update_nonexisting(self):
        code, _ = self.client.notification_update(str(uuid.uuid4()))
        self.assertEqual(404, code)

    def test_api(self):
        self.check_notification_count(0)

        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter)

        self.check_notification_count(1)

        code, _ = self.client.notification_delete(notification['id'])
        self.assertEqual(204, code)

        self.check_notification_count(0)

    def test_filter_format(self):
        valid_cases = (
            'level:SUCCESS',
            'level:ERROR',
            'level:SUCCESS level:ERROR',
            'ack:true'
        )

        invalid_cases = (
            '',
            'level',
            ':',
            'elelv:SUCCESS'
        )

        for case in valid_cases:
            code, updated_notification = self.client.notification_create(
                self.user_id, 'First notification', case)
            self.assertEqual(201, code)
            self.assertEqual(case, updated_notification['filter'])

        for case in invalid_cases:
            code, _ = self.client.notification_create(
                self.user_id, 'First notification', case)
            self.assertEqual(400, code)

    def test_get_notification(self):
        _, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter)
        code, notification = self.client.notification_get(
            notification['id'])
        self.assertEqual(200, code)

    def test_create_notification_with_immutable(self):
        correct_body = {
            "name": 'First notification',
            "filter": self.success_filter,
            "reactions": [self.mail_reaction.copy()]
        }
        for immutable in ['id', 'deleted_at', 'created_at']:
            body = correct_body.copy()
            body[immutable] = 'value'
            code, notification = self.client.post('users/%s/notifications' %
                                                  self.user_id, body)
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'parameter "%s" is immutable' % immutable)

    def test_create_notification_with_unexpected(self):
        correct_body = {
            "name": 'First notification',
            "filter": self.success_filter,
            "reactions": [self.mail_reaction.copy()]
        }
        for unexpected in ['some', '9']:
            body = correct_body.copy()
            body[unexpected] = 'value'
            code, notification = self.client.post('users/%s/notifications' %
                                                  self.user_id, body)
            self.assertEqual(code, 400)
            self.assertEqual(notification['error']['reason'],
                             'Unexpected parameters: %s' % unexpected)

    def test_update_notification_with_immutable(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])
        self.assertEqual(code, 201)
        for immutable in ['deleted_at', 'created_at', 'user_id']:
            body = {
                'filter': 'level:ERROR',
                immutable: 'value'
            }
            code, updated_notification = self.client.notification_update(
                notification['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(updated_notification['error']['reason'],
                             'parameter "%s" is immutable' % immutable)

    def test_update_notification_with_unexpected(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])
        self.assertEqual(code, 201)
        for unexpected in ['value', '']:
            body = {
                'filter': 'level:ERROR',
                unexpected: 'value'
            }
            code, updated_notification = self.client.notification_update(
                notification['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(updated_notification['error']['reason'],
                             'Unexpected parameters: %s' % unexpected)

    def test_create_notification_invalid_name_len(self):
        longname = "".join(random.choice(string.ascii_lowercase)
                           for _ in range(256))
        for name in ['', longname]:
            code, notification = self.client.notification_create(
                self.user_id, name, self.success_filter)
            self.assertEqual(400, code)
            self.assertEqual(notification['error']['reason'],
                             'name should contain 1-255 characters')

    def test_create_notification_without_name(self):
        code, notification = self.client.notification_create(
            self.user_id, None, self.success_filter)
        self.assertEqual(400, code)
        self.assertEqual(notification['error']['reason'],
                         'name is not provided')
        code, notification = self.client.post(
            'users/%s/notifications' % self.user_id, {
                "filter": self.success_filter,
                "reactions": [self.mail_reaction.copy()]
            })
        self.assertEqual(code, 400)
        self.assertEqual(notification['error']['reason'],
                         'name is not provided')

    def test_create_notification_invalid_filter(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', 9)
        self.assertEqual(400, code)
        self.assertEqual(notification['error']['reason'],
                         'filter should be a string')

    def test_create_notification_without_filter(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', None)
        self.assertEqual(400, code)
        self.assertEqual(notification['error']['reason'],
                         'filter is not provided')

    def test_create_notification_int_name(self):
        code, notification = self.client.notification_create(
            self.user_id, 123, self.success_filter)
        self.assertEqual(400, code)
        self.assertEqual(notification['error']['reason'],
                         'name should be a string')

    def test_create_notification_int_filter(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', 123)
        self.assertEqual(400, code)
        self.assertEqual(notification['error']['reason'],
                         'filter should be a string')

    def test_create_notification_without_reactions(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=None)
        self.assertEqual(201, code)
        code, notification = self.client.post(
            'users/%s/notifications' % self.user_id, {
                "name": 'name',
                "filter": self.success_filter,
            })
        self.assertEqual(code, 201)

    def test_update_notification_with_invalid_name(self):
        code, notification = self.client.notification_create(
            self.user_id, 'First notification', self.success_filter,
            reactions=[self.mail_reaction])
        self.assertEqual(code, 201)
        longname = "".join(random.choice(string.ascii_lowercase)
                           for _ in range(256))
        for bad_name in [longname, '']:
            body = {
                'name': bad_name,
            }
            code, updated_notification = self.client.notification_update(
                notification['id'], **body)
            self.assertEqual(code, 400)
            self.assertEqual(updated_notification['error']['reason'],
                             'name should contain 1-255 characters')
        code, updated_notification = self.client.notification_update(
            notification['id'], **{'name': 123})
        self.assertEqual(code, 400)
        self.assertEqual(updated_notification['error']['reason'],
                         'name should be a string')

    def test_creation_timestamp(self):
        with freeze_time() as frozen_datetime:
            _, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter)
            first_notification_created_at = notification['created_at']
            frozen_datetime.tick()
            _, notification = self.client.notification_create(
                self.user_id, 'First notification', self.success_filter)
            second_notification_created_at = notification['created_at']
            self.assertLess(first_notification_created_at,
                            second_notification_created_at)
