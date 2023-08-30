from unittest.mock import patch
from datetime import datetime

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestContextApi(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('optscale_client.config_client.client.Client.delete').start()
        patch('optscale_client.config_client.client.Client.read').start()
        patch('tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        _, self.organization = self.organization_create("Hystax")
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.organization['id'],
            {'name': 'John Smith', 'auth_user_id': self.user_id})
        self._mock_auth_user(self.user_id)
        self.cloud_acc_id = None

    def _create_cloud_account(self):
        if not self.cloud_acc_id:
            valid_aws_cloud_acc = {
                'name': 'test_credentials',
                'type': 'aws_cnr',
                'config': {
                    'access_key_id': 'key',
                    'secret_access_key': 'secret',
                }
            }
            code, cloud_acc = self.create_cloud_account(
                self.organization['id'], valid_aws_cloud_acc,
                auth_user_id=self.user_id)
            self.assertEqual(code, 201)
            self.cloud_acc_id = cloud_acc['id']

    def _create_resource(self, employee_id=None, pool_id=None, active=False):
        self._create_cloud_account()
        self.valid_resource = {
            'cloud_resource_id': self.gen_id(),
            'name': 'test_resource',
            'resource_type': 'test_type',
            'employee_id': employee_id,
            'pool_id': pool_id
        }
        code, resource = self.cloud_resource_create(
            self.cloud_acc_id, self.valid_resource)
        self.assertEqual(code, 201)
        if active:
            self.resources_collection.update_one(
                filter={
                    '_id': resource['id']
                },
                update={'$set': {
                    'last_seen': int(datetime.utcnow().timestamp() - 1),
                    'active': True
                }}
            )
        return resource

    def test_organization_context(self):
        code, context = self.client.context_get('organization',
                                                self.organization['id'])
        self.assertEqual(code, 200)
        self.assertEqual(context['organization'], [self.organization['id']])

    def test_incomplete_params(self):
        code, context = self.client.context_get(None, self.organization['id'])
        self.assertEqual(code, 400)
        self.assertEqual(context['error']['reason'],
                         'Type or/and uuid is missing')

    def test_invalid_type(self):
        type = 'unknown'
        code, context = self.client.context_get(type, self.organization['id'])
        self.assertEqual(code, 400)
        self.assertEqual(context['error']['reason'], 'Type %s is invalid' %
                         type)

    def organization_create(self, name):
        return self.client.organization_create({'name': name})

    def organization_delete(self, org_id):
        return self.client.organization_delete(org_id)

    def test_hierarchical_pool_context(self):
        _, pool1 = self.client.pool_create(self.organization['id'], {
            'name': 'b1'
        })
        _, pool2 = self.client.pool_create(self.organization['id'], {
            'name': 'b2'
        })
        _, pool3 = self.client.pool_create(self.organization['id'], {
            'name': 'b3', 'parent_id': pool2['id']
        })
        _, pool4 = self.client.pool_create(self.organization['id'], {
            'name': 'b4', 'parent_id': pool3['id']
        })
        _, pool5 = self.client.pool_create(self.organization['id'], {
            'name': 'b5', 'parent_id': pool1['id']
        })

        org_pool_id = self.organization['pool_id']
        context_map = {
            org_pool_id: [org_pool_id],
            pool1['id']: [org_pool_id, pool1['id']],
            pool2['id']: [org_pool_id, pool2['id']],
            pool3['id']: [org_pool_id, pool2['id'], pool3['id']],
            pool4['id']: [org_pool_id, pool2['id'], pool3['id'],
                          pool4['id']],
            pool5['id']: [org_pool_id, pool1['id'], pool5['id']]
        }
        for pool_id, parents in context_map.items():
            code, context = self.client.context_get('pool', pool_id)
            self.assertEqual(code, 200)
            self.assertEqual(context['organization'], [self.organization['id']])
            self.assertEqual(len(context['pool']), len(parents))
            for item_id in parents:
                self.assertIn(item_id, context['pool'])

    def test_resource_context(self):
        res = self._create_resource()
        code, context = self.client.context_get('cloud_resource', res['id'])
        self.assertEqual(code, 200)
        self.assertEqual(context['organization'], [self.organization['id']])

        _, pool = self.client.pool_create(
            self.organization['id'], {'name': 'pool'})
        res = self._create_resource(
            pool_id=pool['id'], employee_id=self.employee['id'])
        code, context = self.client.context_get('cloud_resource', res['id'])
        self.assertEqual(code, 200)
        for val in [pool['id'], self.organization['pool_id']]:
            self.assertIn(val, context['pool'])

    def test_resource_constraint_context(self):
        res = self._create_resource(
            active=True, pool_id=self.organization['pool_id'],
            employee_id=self.employee['id'])
        code, constraint = self.client.resource_constraint_create(
            res['id'], {'limit': int(datetime.utcnow().timestamp()) + 3600,
                        'type': 'ttl'})
        self.assertEqual(code, 201)

        code, context = self.client.context_get('resource_constraint',
                                                constraint['id'])
        self.assertEqual(code, 200)
        self.assertEqual(context['organization'], [self.organization['id']])

        _, pool = self.client.pool_create(
            self.organization['id'], {'name': 'pool'})
        res = self._create_resource(
            pool_id=pool['id'], employee_id=self.employee['id'],
            active=True
        )
        _, constraint = self.client.resource_constraint_create(
            res['id'],
            {'limit': int(datetime.utcnow().timestamp()) + 3600,
             'type': 'ttl'})
        code, context = self.client.context_get(
            'resource_constraint', constraint['id'])
        self.assertEqual(code, 200)
        for val in [pool['id'], self.organization['pool_id']]:
            self.assertIn(val, context['pool'])

    def test_deleted_parent(self):
        self._create_cloud_account()
        patch('rest_api.rest_api_server.controllers.employee.EmployeeController.'
              'get_org_manager_user', return_value=None).start()
        code, _ = self.organization_delete(self.organization['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.context_get('cloud_account', self.cloud_acc_id)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0472')
        self.assertEqual(resp['error']['params'], [
            'cloud_account', self.cloud_acc_id,
            'organization', self.organization['id']])
