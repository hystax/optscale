import json
import uuid

from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestCloudAccountApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org1 = self.client.organization_create({'name': "organization"})
        _, self.org2 = self.client.organization_create(
            {'name': "second_organization"})
        self.org_id1 = self.org1['id']
        self.org_id2 = self.org2['id']
        self.value1 = {'value': json.dumps({'key1': 'value1'})}
        self.name1 = 'default_option'
        self.value2 = {'value': json.dumps({'key2': 'value2'})}
        self.name2 = 'new_option'
        _, _ = self.client.organization_option_create(
            self.org_id1, self.name1, self.value1)
        _, _ = self.client.organization_option_create(
            self.org_id2, self.name2, self.value2)

    def test_create_organization_option(self):
        code, resp = self.client.organization_option_create(
            self.org_id1, self.name2, self.value1)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value1)
        # trying to create an option with the same keys should result
        # in the record being updated
        code, resp = self.client.organization_option_create(
            self.org_id1, self.name2, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)
        code, _ = self.client.organization_option_create(
            'abcd', self.name1, self.value1)
        self.assertEqual(code, 404)

    def test_update_organization_option(self):
        code, resp = self.client.organization_option_update(
            self.org_id1, self.name1, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)
        # trying to update an option with nonexistent keys should result
        # in a record being created
        code, resp = self.client.organization_option_update(
            self.org_id2, self.name1, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)
        code, _ = self.client.organization_option_update(
            'abcd', self.name1, self.value1)
        self.assertEqual(code, 404)

    def test_update_locked_by_user_organization_option(self):
        patch('rest_api_server.controllers.base.BaseController.get_user_id',
              return_value=self._user_id).start()
        patch('rest_api_server.handlers.v1.base.BaseAuthHandler.check_cluster_secret',
              return_value=False).start()
        another_user_id = str(uuid.uuid4())

        # lock the record by current user
        value1_with_user = {'value': json.dumps(
            {'key2': 'value1', 'locked_by': self._user_id})}
        code, resp = self.client.organization_option_update(
            self.org_id1, self.name1, value1_with_user)
        self.assertEqual(code, 200)
        self.assertEqual(resp, value1_with_user)

        # updating a record locked by current user should be ok
        # let's lock the record by another user
        value1_with_another_user = {'value': json.dumps(
            {'key2': 'value1', 'locked_by': another_user_id})}
        code, resp = self.client.organization_option_update(
            self.org_id1, self.name1, value1_with_another_user)
        self.assertEqual(code, 200)
        self.assertEqual(resp, value1_with_another_user)

        # trying to update a locked by another user record should result in 403
        tmp_value = {'value': json.dumps({'key2': 'value1_updated'})}
        code, resp = self.client.organization_option_update(
            self.org_id1, self.name1, tmp_value)
        self.assertEqual(code, 403)

        # trying to update a record locked by a user when using a
        # cluster_secret should go fine
        patch('rest_api_server.handlers.v1.base.BaseAuthHandler.'
              'check_cluster_secret', return_value=True).start()
        code, resp = self.client.organization_option_update(
            self.org_id1, self.name1, tmp_value)
        self.assertEqual(code, 200)

    def test_get_organization_option(self):
        code, resp = self.client.organization_option_get(
            self.org_id1, self.name1)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value1)
        code, resp = self.client.organization_option_get(
            self.org_id1, self.name2)
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('value'), '{}')
        code, _ = self.client.organization_option_get('abcd', self.name1)
        self.assertEqual(code, 404)

    def test_list_organization_option(self):
        code, resp = self.client.organization_options_list(self.org_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 1)
        _, _ = self.client.organization_option_create(
            self.org_id1, self.name2, self.value2)
        code, resp = self.client.organization_options_list(self.org_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 2)
        _, _ = self.client.organization_option_delete(self.org_id2, self.name2)
        code, resp = self.client.organization_options_list(self.org_id2)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 0)
        code, _ = self.client.organization_options_list('abcd')
        self.assertEqual(code, 404)

    def test_delete_organization_option(self):
        code, _ = self.client.organization_option_delete(
            self.org_id1, self.name1)
        self.assertEqual(code, 204)
        code, resp = self.client.organization_options_list(self.org_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 0)
        code, _ = self.client.organization_option_delete(
            self.org_id1, self.name1)
        self.assertEqual(code, 404)
        code, _ = self.client.organization_option_delete(
            'abcd', self.name1)
        self.assertEqual(code, 404)
