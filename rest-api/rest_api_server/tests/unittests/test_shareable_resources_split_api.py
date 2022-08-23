from datetime import datetime
from unittest.mock import patch
from cloud_adapter.model import ResourceTypes
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestSplitShareableResourcesApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.org = self.client.organization_create({'name': "super_org"})
        self.org_id = self.org['id']

        self.auth_user = self.gen_id()
        self._mock_auth_user(self.auth_user)

        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': self.auth_user})
        cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc, auth_user_id=self.auth_user)
        self.cloud_acc_id = self.cloud_acc['id']
        self.instance_resource = self.create_cloud_resource(
            self.cloud_acc_id, name='instance',
            resource_type=ResourceTypes.instance.value)
        self.not_instance = self.create_cloud_resource(
            self.cloud_acc_id, name='snapshot', tags={'tag': 'value'},
            resource_type=ResourceTypes.snapshot.value)
        self._prepare_cluster_resources()

    def _prepare_cluster_resources(self):
        code, self.cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'name', 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        self.instance_cluster_res = self.create_cloud_resource(
            self.cloud_acc_id, name='instance in cluster',
            resource_type=ResourceTypes.instance.value,
            tags={'tag': 'value'})
        self.assertEqual(code, 201)
        self.cluster_resource = list(self.resources_collection.find(
            {'cluster_type_id': self.cluster_type['id']}))[0]

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='test_type',
                              name='test_resource', tags=None, last_seen=None,
                              region=None, first_seen=None):
        now = int(datetime.utcnow().timestamp())
        resource = {
            'cloud_resource_id': self.gen_id(),
            'name': name,
            'resource_type': resource_type,
            'employee_id': employee_id,
            'pool_id': pool_id,
            'last_seen': last_seen or now,
            'first_seen': first_seen or now,
            'region': region,
        }
        if tags:
            resource['tags'] = tags
        code, resource = self.cloud_resource_create(
            cloud_account_id, resource)
        self.assertEqual(code, 201)
        return resource

    def test_shareable_get(self):
        self._make_resources_active([self.instance_resource['id'],
                                     self.not_instance['id'],
                                     self.instance_cluster_res['id'],
                                     self.cluster_resource['_id']])

        code, data = self.client.shareable_resources_get(
            self.org_id, resource_ids=[self.instance_resource['id'],
                                       self.not_instance['id'],
                                       self.cluster_resource['_id']])
        self.assertEqual(code, 200)
        eligible_ids = [x['id'] for x in data['eligible']]
        not_eligible_ids = [x['id'] for x in data['not_eligible']]
        self.assertEqual(eligible_ids, [self.instance_resource['id'],
                                        self.cluster_resource['_id']])
        self.assertEqual(not_eligible_ids, [self.not_instance['id']])

        self._make_resources_inactive([self.instance_resource['id']])
        code, data = self.client.shareable_resources_get(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 200)
        not_eligible_ids = [x['id'] for x in data['not_eligible']]
        self.assertEqual(not_eligible_ids, [self.instance_resource['id']])

        self._make_resources_active([self.instance_resource['id']])
        code, _ = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 201)
        code, data = self.client.shareable_resources_get(
            self.org_id, resource_ids=[self.instance_resource['id'],
                                       self.instance_cluster_res['id'],
                                       self.cluster_resource['_id']])
        self.assertEqual(code, 200)
        eligible_ids = [x['id'] for x in data['eligible']]
        not_eligible_ids = [x['id'] for x in data['not_eligible']]
        already_shareable_ids = [x['id'] for x in data['already_shareable']]
        self.assertEqual(already_shareable_ids,
                         [self.instance_resource['id']])
        self.assertEqual(eligible_ids, [self.cluster_resource['_id']])
        self.assertEqual(not_eligible_ids, [self.instance_cluster_res['id']])

    def test_shareable_get_invalid_resource(self):
        resource_ids = 'abcd'
        code, res = self.client.shareable_resources_get(
            self.org_id, resource_ids)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0385')
        resource_ids = ['abcd']
        code, res = self.client.shareable_resources_get(
            self.org_id, resource_ids)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_shareable_get_empty(self):
        code, data = self.client.shareable_resources_get(
            self.org_id, [])
        self.assertEqual(code, 200)
        for v in data.values():
            self.assertEqual(v, [])

    def test_shareable_get_invalid(self):
        resource_id = '123'
        code, res = self.client.shareable_resources_get(
            self.org_id, resource_ids=[resource_id])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_shareable_get_deleted(self):
        resource = self.create_cloud_resource(
            self.cloud_acc_id, name='instance',
            resource_type=ResourceTypes.instance.value)
        code, _ = self.client.cloud_resource_delete(resource['id'])
        self.assertEqual(code, 204)
        code, res = self.client.shareable_resources_get(
            self.org_id, resource_ids=[resource['id']])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')
