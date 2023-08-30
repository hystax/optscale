from datetime import datetime
from unittest.mock import patch, ANY
from tools.cloud_adapter.model import ResourceTypes
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.exceptions import Err


class TestShareableResourcesApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.org = self.client.organization_create({'name': "super_org"})
        self.client.pool_update(self.org['pool_id'], {'limit': 100})
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
        self.env_resource = self.create_cloud_resource(
            self.cloud_acc_id, shareable=True)

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='test_type',
                              name='test_resource', tags=None, last_seen=None,
                              region=None, first_seen=None,
                              shareable=False):
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
        if shareable:
            resource_id = resource['id']
            self.resources_collection.update_one(
                filter={'_id': resource_id},
                update={'$set': {'shareable': True}}
            )
        return resource

    def verify_shareable_resources_response(
            self, response, shared_ids=None, not_shared_ids=None,
            invalid_ids=None, not_active_ids=None):
        if not shared_ids:
            shared_ids = []
        succeeded = {'succeeded': shared_ids}

        failed = {'failed': []}
        if not_shared_ids:
            failed_template = {
                "code": Err.OE0478.name,
                "message": Err.OE0478.value[0]
            }
            for res in not_shared_ids:
                failed_template['id'] = res[0]
                failed_template['message'] = failed_template['message'] % res[1]
                failed['failed'].append(failed_template)
        if invalid_ids:
            failed_template = {
                "code": Err.OE0412.name,
                "message": Err.OE0412.value[0]
            }
            for res in invalid_ids:
                failed_template['id'] = res[0]
                failed_template['message'] = failed_template['message'] % res[1]
                failed['failed'].append(failed_template)
        if not_active_ids:
            failed_template = {
                "code": Err.OE0443.name,
                "message": Err.OE0443.value[0]
            }
            for res in not_active_ids:
                failed_template['id'] = res[0]
                failed_template['message'] = failed_template['message'] % res[1]
                failed['failed'].append(failed_template)
        expected = {**succeeded, **failed}
        self.assertDictEqual(expected, response)

    def test_shareable_bulk(self):
        self._make_resources_active([self.instance_resource['id'],
                                     self.not_instance['id'],
                                     self.cluster_resource['_id']])
        # shareable instance
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, shared_ids=[self.instance_resource['id']])

        resource = list(self.resources_collection.find(
            {'_id': self.instance_resource['id']}))[0]
        self.assertEqual(resource['shareable'], True)

        # not shareable snapshot
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.not_instance['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, not_shared_ids=[
                (self.not_instance['id'],
                 self.not_instance['cloud_resource_id'])])

        # shareable cluster
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.cluster_resource['_id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, shared_ids=[self.cluster_resource['_id']])

        # shareable environment
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.env_resource['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, shared_ids=[self.env_resource['id']])

    def test_shareable_bulk_unexpected(self):
        body = {'resource_ids': [], 'unexpected': 'arg'}
        code, res = self.client.post(
            self.client.shareable_bulk_url(self.org_id), body)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_shareable_resource_not_provided(self):
        body = {}
        code, res = self.client.post(
            self.client.shareable_bulk_url(self.org_id), body)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_shareable_resource_ids_not_list(self):
        body = {'resource_ids': 'resource_ids'}
        code, res = self.client.post(
            self.client.shareable_bulk_url(self.org_id), body)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0385')

    def test_shareable_resource_ids_empty(self):
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(data, shared_ids=[])

    def test_share_already_shared(self):
        self._make_resources_active([self.instance_resource['id']])
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 201)

        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, shared_ids=[self.instance_resource['id']])

    def test_email_share_resources(self):
        p_email_send = self.mock_email_send_enable()
        self.resources_collection.update_many(
            filter={},
            update={'$set': {'shareable': False}}
        )
        self._make_resources_active([self.instance_resource['id'],
                                     self.not_instance['id'],
                                     self.cluster_resource['_id']])
        # shareable instance
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[self.instance_resource['id']])
        self.assertEqual(code, 201)
        p_email_send.assert_called_once_with(
            [ANY], 'OptScale shareable resources notification',
            template_type='first_shareable_resources',
            template_params={
                'texts': {'organization': {
                    'id': self.org['id'],
                    'name': self.org['name'],
                    'currency_code': '$'},
                    'title': 'First shareable resource',
                    'shareable_resource_count': 1}}
        )

    def test_shareable_resource_not_active(self):
        resource = self.create_cloud_resource(
            self.cloud_acc_id, name='instance',
            resource_type=ResourceTypes.instance.value)
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[resource['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, not_active_ids=[(resource['id'],
                                   resource['cloud_resource_id'])])

    def test_shareable_resource_invalid(self):
        resource_id = '123'
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[resource_id])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, invalid_ids=[(resource_id, resource_id)])

    def test_shareable_resource_deleted(self):
        resource = self.create_cloud_resource(
            self.cloud_acc_id, name='instance',
            resource_type=ResourceTypes.instance.value)
        code, data = self.client.cloud_resource_delete(resource['id'])
        self.assertEqual(code, 204)
        code, data = self.client.resources_bulk_share(
            self.org_id, resource_ids=[resource['id']])
        self.assertEqual(code, 201)
        self.verify_shareable_resources_response(
            data, invalid_ids=[(resource['id'],
                               resource['cloud_resource_id'])])
