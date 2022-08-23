import uuid

from unittest.mock import patch
from rest_api_server.models.enums import ConstraintTypes
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestPoolPolicies(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.organization = self.client.organization_create(
            {'name': 'test organization'})
        self.valid_policy = {
            'limit': 100,
            'type': 'ttl'
        }
        self.code, self.policy = self.client.pool_policy_create(
            self.organization['pool_id'], self.valid_policy)

    def test_create_policy(self):
        self.assertEqual(self.code, 201)
        self.assertEqual(self.policy['pool_id'],
                         self.organization['pool_id'])
        self.assertEqual(self.policy['type'], ConstraintTypes.TTL.value)
        self.assertTrue(self.policy['active'])
        self.assertEqual(self.policy['limit'], self.valid_policy['limit'])

    def test_get_policy(self):
        code, policy = self.client.pool_policy_get(self.policy['id'])
        self.assertEqual(code, 200)
        self.assertEqual(policy['pool_id'], self.organization['pool_id'])

    def test_list_policy(self):
        code, resp = self.client.pool_policy_list(
            self.organization['pool_id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(resp['policies'])
        self.assertEqual(len(resp['policies']), 1)

    def test_org_list_policy(self):
        code, resp = self.client.resource_policies_list(
            self.organization['id'])
        self.assertEqual(code, 200)
        policies = resp['resource_policies']
        self.assertIsNotNone(policies)
        self.assertEqual(len(policies), 1)
        pool_policy = policies[0]
        self.assertIsNone(pool_policy.get('details'))
        code, resp = self.client.resource_policies_list(
            self.organization['id'], details=True)
        self.assertEqual(code, 200)
        policies = resp['resource_policies']
        self.assertIsNotNone(policies)
        self.assertEqual(len(policies), 1)
        pool_policy = policies[0]
        self.assertIsNotNone(pool_policy.get('details'))
        pool_details = pool_policy.get('details')
        self.assertEqual(pool_details['id'], self.organization['pool_id'])

    def test_list_policy_deleted_pool(self):
        self.client.organization_delete(self.organization['id'])
        code, response = self.client.pool_policy_list(
            self.organization['pool_id'])
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_list_policy_for_deleted_pool(self):
        code, child_pool = self.client.pool_create(self.organization['id'], {
            'name': 'subpool', 'parent_id': self.organization['pool_id']})
        self.assertEqual(code, 201)
        code, response = self.client.pool_policy_create(
            child_pool['id'], {
                'limit': 50,
                'type': 'ttl'
            }
        )
        self.assertEqual(code, 201)
        code, resp = self.client.resource_policies_list(
            self.organization['id'])
        self.assertEqual(code, 200)
        policies = resp['resource_policies']
        self.assertIsNotNone(policies)
        self.assertEqual(len(policies), 2)
        code, resp = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.resource_policies_list(
            self.organization['id'])
        self.assertEqual(code, 200)
        policies = resp['resource_policies']
        self.assertIsNotNone(policies)
        self.assertEqual(len(policies), 1)

    def test_create_duplicate(self):
        code, response = self.client.pool_policy_create(
            self.organization['pool_id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )
        self.assertEqual(code, 409)
        self.assertEqual(response['error']['error_code'], 'OE0440')

        code, response = self.client.pool_policy_create(
            self.organization['pool_id'], {
                'limit': 150,
                'type': 'total_expense_limit'
            }
        )
        self.assertEqual(code, 201)

    def test_create_invalid_id(self):
        code, response = self.client.pool_policy_create(
            str(uuid.uuid4()), self.valid_policy)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_get_invalid_id(self):
        code, response = self.client.pool_policy_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_create_invalid_params(self):
        _, organization = self.client.organization_create(
            {'name': 'test organization 2'})
        invalid_params_map = {
            'limit': ['string', -1, None, '', 2**31],
            'type': ['value', 123, '', None],
            'active': [123, '']
        }
        for param, invalid_values in invalid_params_map.items():
            body = self.valid_policy.copy()
            for invalid_value in invalid_values:
                body[param] = invalid_value
                code, response = self.client.pool_policy_create(
                    organization['pool_id'], body)
                self.assertEqual(code, 400)

    def test_unexpected_and_immutable(self):
        _, organization = self.client.organization_create(
            {'name': 'test organization 2'})
        extra = {'extra_param': 'extra_value'}
        self.valid_policy.update(extra)
        code, response = self.client.pool_policy_create(
            organization['pool_id'], self.valid_policy)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

        code, response = self.client.pool_policy_update(
            self.policy['id'], extra)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

        self.valid_policy.pop('extra_param')
        extra = {'deleted_at': 1}
        self.valid_policy.update(extra)
        code, response = self.client.pool_policy_create(
            organization['pool_id'], self.valid_policy)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0211')

        code, response = self.client.pool_policy_update(
            self.policy['id'], extra)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0211')

    def test_update(self):
        code, response = self.client.pool_policy_update(
            self.policy['id'], {'limit': 200})
        self.assertEqual(code, 200)
        self.assertEqual(response['limit'], 200)

    def test_delete(self):
        code, _ = self.client.pool_policy_delete(self.policy['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.pool_policy_get(self.policy['id'])
        self.assertEqual(code, 404)
        code, _ = self.client.pool_policy_update(
            self.policy['id'], {})
        self.assertEqual(code, 404)

    def test_limit_values(self):
        _, organization = self.client.organization_create(
            {'name': 'test organization 2'})
        policy = {
            'limit': 721,
            'type': 'ttl'
        }
        code, response = self.client.pool_policy_create(
            organization['pool_id'], policy)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')
        policy['type'] = 'total_expense_limit'
        code, response = self.client.pool_policy_create(
            organization['pool_id'], policy)
        self.assertEqual(code, 201)

    def test_policy_limit_min_max_values(self):
        _, organization = self.client.organization_create(
            {'name': 'test organization 2'})
        out_of_limits_values = {
            'ttl': [-1, 721],
            'total_expense_limit': [-1, 2147483648]
        }
        for policy_type, values in out_of_limits_values.items():
            for value in values:
                code, response = self.client.pool_policy_create(
                    organization['pool_id'], {
                        'limit': value,
                        'type': policy_type
                    })
                self.assertEqual(code, 400)
                self.assertEqual(response['error']['error_code'], 'OE0224')
        code, policy_ttl = self.client.pool_policy_create(
            organization['pool_id'], {
                'limit': 100,
                'type': 'ttl'
            })
        self.assertEqual(code, 201)
        code, policy_exp_limit = self.client.pool_policy_create(
            organization['pool_id'], {
                'limit': 100,
                'type': 'total_expense_limit'
            })
        self.assertEqual(code, 201)
        policies_map = {
            'ttl': policy_ttl,
            'total_expense_limit': policy_exp_limit
        }
        for policy_type, values in out_of_limits_values.items():
            policy = policies_map[policy_type]
            for value in values:
                code, response = self.client.pool_policy_update(
                    policy['id'], {'limit': value})
                self.assertEqual(code, 400)
                self.assertEqual(response['error']['error_code'], 'OE0224')

    def test_create_policy_invalid_type(self):
        policy = {
            'limit': 5,
        }
        code, response = self.client.pool_policy_create(
            self.organization['pool_id'], policy)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0216')
        self.assertEqual(response['error']['reason'], 'type is not provided')

        policy['type'] = 'invalid'
        code, response = self.client.pool_policy_create(
            self.organization['pool_id'], policy)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0004')

    def test_create_infinity_policy(self):
        valid_policy = {
            'limit': 0,
            'type': 'total_expense_limit'
        }
        code, policy = self.client.pool_policy_create(
            self.organization['pool_id'], valid_policy)
        self.assertEqual(code, 201)
        self.assertEqual(policy['pool_id'],
                         self.organization['pool_id'])
        self.assertEqual(policy['type'], ConstraintTypes.TOTAL_EXPENSE_LIMIT.value)
        self.assertTrue(policy['active'])
        self.assertEqual(policy['limit'], 0)

    def test_policy_events(self):
        self.p_get_user_info.return_value = {
            'display_name': 'John Doe', 'id': self._user_id,
            'email': 'example@hystax.com'}
        p_publish_activity = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()

        valid_policy = {'limit': 100, 'type': 'total_expense_limit'}
        code, policy = self.client.pool_policy_create(
            self.organization['pool_id'], valid_policy)
        self.assertEqual(code, 201)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.organization['pool_id'], 'pool',
            'policy_created', {'object_name': 'test organization',
                               'policy_type': 'total_expense_limit'})
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)

        p_publish_activity = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, resp = self.client.pool_policy_update(
            policy['id'], {'active': False})
        self.assertEqual(code, 200)
        self.assertFalse(resp['active'])
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.organization['pool_id'], 'pool',
            'policy_disabled', {'object_name': 'test organization',
                                'policy_type': 'total_expense_limit'})
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)

        p_publish_activity = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.pool_policy_update(
            policy['id'], {'active': False, 'limit': 50})
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.organization['pool_id'], 'pool',
            'policy_updated', {'object_name': 'test organization',
                               'policy_type': 'total_expense_limit',
                               'params': 'limit: 50'})
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)

        p_publish_activity = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, response = self.client.pool_policy_update(
            policy['id'], {'active': True})
        self.assertEqual(code, 200)
        self.assertTrue(response['active'])
        code, _ = self.client.pool_policy_update(
            policy['id'], {'active': True})
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.organization['pool_id'], 'pool',
            'policy_enabled', {'object_name': 'test organization',
                               'policy_type': 'total_expense_limit'})
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)

        p_publish_activity = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.pool_policy_delete(policy['id'])
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.organization['pool_id'], 'pool',
            'policy_deleted', {'object_name': 'test organization',
                               'policy_type': 'total_expense_limit'})
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)
