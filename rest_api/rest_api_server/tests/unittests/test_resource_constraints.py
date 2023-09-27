import uuid
from datetime import datetime
from unittest.mock import patch
from rest_api.rest_api_server.models.enums import ConstraintTypes
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestResourceConstraints(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.organization = self.client.organization_create(
            {'name': 'test organization'})
        valid_aws_creds = {
            'name': 'test_credentials',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.p_configure = patch(
            'tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.organization['id'],
            {'name': 'John Smith', 'auth_user_id': self.user_id})
        _, self.cloud_acc = self.create_cloud_account(
            self.organization['id'], valid_aws_creds, auth_user_id=self.user_id)
        self._mock_auth_user(self.user_id)
        self.valid_resource = {
            'cloud_resource_id': self.gen_id(),
            'name': 'test_resource',
            'resource_type': 'test_type',
            'employee_id': self.employee['id'],
            'pool_id': self.organization['pool_id']
        }
        _, self.resource = self._create_cloud_resource(self.cloud_acc['id'],
                                                       self.valid_resource)
        self.valid_constraint = {
            'limit': int(datetime.utcnow().timestamp()) + 3600,
            'type': 'ttl'
        }

    def _create_cloud_resource(self, cloud_acc_id, params, active=True,
                               valid_until=None, request_id=None):
        code, resource = self.cloud_resource_create(
            cloud_acc_id, params)
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
        return code, resource

    def test_create_constraint(self):
        code, constraint = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 201)
        self.assertEqual(constraint['resource_id'], self.resource['id'])
        self.assertEqual(constraint['type'], ConstraintTypes.TTL.value)
        self.assertEqual(constraint['limit'],
                         self.valid_constraint['limit'])

    def test_get_constraint(self):
        _, constraint = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        code, constraint = self.client.resource_constraint_get(
            constraint['id'])
        self.assertEqual(code, 200)
        self.assertEqual(constraint['resource_id'], self.resource['id'])

    def test_get_global_constraints(self):
        valid_azure_cloud_acc = {
            'name': 'azure',
            'type': 'azure_cnr',
            'config': {
                'client_id': 'client',
                'secret': 'secret',
                'tenant': 'tenant',
                'subscription_id': 'subscription',
            }
        }
        patch('tools.cloud_adapter.clouds.azure.Azure.configure_report').start()
        _, azure_cloud_acc = self.create_cloud_account(
            self.organization['id'], valid_azure_cloud_acc,
            auth_user_id=self.user_id)
        azure_resource_template = self.valid_resource.copy()
        azure_resource_template['cloud_resource_id'] = self.gen_id()
        azure_resource_template['name'] = 'azure_test_resource'
        _, azure_resource = self._create_cloud_resource(
            azure_cloud_acc['id'], azure_resource_template)
        _, aws_res_constraint = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        _, azure_res_constraint = self.client.resource_constraint_create(
            azure_resource['id'], self.valid_constraint)
        code, global_constraints = self.client.resource_constraints_list(
            self.organization['id'])
        self.assertEqual(code, 200)
        resource_constraints = global_constraints['resource_constraints']
        self.assertEqual(len(resource_constraints), 2)
        code, global_constraints = self.client.resource_constraints_list(
            self.organization['id'], details=True)
        self.assertEqual(code, 200)
        resource_constraints = global_constraints['resource_constraints']
        self.assertEqual(len(resource_constraints), 2)
        for resource_constraint in resource_constraints:
            details = resource_constraint['details']
            owner = details['owner']
            self.assertIsNotNone(owner)
            pool = details['pool']
            self.assertIsNotNone(pool)
            self.assertEqual(pool['id'], self.organization['pool_id'])
            self.assertEqual(pool['name'], self.organization['name'])
            self.assertEqual(pool['purpose'], 'business_unit')
            self.assertEqual(owner['id'], self.employee['id'])
            self.assertEqual(owner['name'], self.employee['name'])
        code, resp = self.client.cloud_account_delete(azure_cloud_acc['id'])
        self.assertEqual(code, 204)
        code, global_constraints = self.client.resource_constraints_list(
            self.organization['id'])
        self.assertEqual(code, 200)
        resource_constraints = global_constraints['resource_constraints']
        self.assertEqual(len(resource_constraints), 1)

    def test_list_constraints(self):
        self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        code, resp = self.client.resource_constraint_list(self.resource['id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(resp['constraints'])
        self.assertEqual(len(resp['constraints']), 1)

    def test_list_constraints_nonexistent(self):
        code, response = self.client.resource_constraint_list(
            str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_create_duplicate(self):
        code, _ = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 201)
        code, response = self.client.resource_constraint_create(
            self.resource['id'], {
                'limit': int(datetime.utcnow().timestamp()) + 7200,
                'type': 'ttl'
            }
        )
        self.assertEqual(code, 409)
        self.assertEqual(response['error']['error_code'], 'OE0441')

        code, response = self.client.resource_constraint_create(
            self.resource['id'], {
                'limit': 150,
                'type': 'total_expense_limit'
            }
        )
        self.assertEqual(code, 201)

    def test_create_invalid_id(self):
        code, response = self.client.resource_constraint_create(
            str(uuid.uuid4()), self.valid_constraint)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_get_invalid_id(self):
        code, response = self.client.resource_constraint_get(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0002')

    def test_create_invalid_params(self):
        invalid_params_map = {
            'limit': ['string', -1, None, '', 2**31],
            'type': ['value', 123, '', None],
        }
        for param, invalid_values in invalid_params_map.items():
            body = self.valid_constraint.copy()
            for invalid_value in invalid_values:
                body[param] = invalid_value
                code, response = self.client.resource_constraint_create(
                    self.resource['id'], body)
                self.assertEqual(code, 400)

    def test_unexpected_and_immutable(self):
        extra = {'extra_param': 'extra_value'}
        self.valid_constraint.update(extra)
        code, response = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

        code, constraint = self.client.resource_constraint_create(
            self.resource['id'], {
                'limit': 100,
                'type': 'total_expense_limit'
            })
        self.assertEqual(code, 201)
        code, response = self.client.resource_constraint_update(
            constraint['id'], extra)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

        self.valid_constraint.pop('extra_param')
        extra = {'deleted_at': 1}
        self.valid_constraint.update(extra)
        code, response = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0211')

        code, response = self.client.resource_constraint_update(
            constraint['id'], extra)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0211')

    def test_update(self):
        limit = int(datetime.utcnow().timestamp()) + 1800
        _, response = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        code, response = self.client.resource_constraint_update(
            response['id'], {'limit': limit})
        self.assertEqual(code, 200)
        self.assertEqual(response['limit'], limit)

    def test_delete(self):
        _, constraint = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        code, _ = self.client.resource_constraint_delete(constraint['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.resource_constraint_get(constraint['id'])
        self.assertEqual(code, 404)
        code, _ = self.client.resource_constraint_update(
            constraint['id'], {})
        self.assertEqual(code, 404)

    def test_limit_values(self):
        constraint = {
            'limit': 721,
            'type': 'ttl'
        }
        code, response = self.client.resource_constraint_create(
            self.resource['id'], constraint)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0461')
        constraint['type'] = 'total_expense_limit'
        code, response = self.client.resource_constraint_create(
            self.resource['id'], constraint)
        self.assertEqual(code, 201)

    def test_create_constraint_invactive_resource(self):
        _, inactive_resource = self._create_cloud_resource(self.cloud_acc['id'], {
            'cloud_resource_id': self.gen_id(),
            'name': 'test_resource',
            'resource_type': 'test_type'
        }, active=False)
        code, response = self.client.resource_constraint_create(
            inactive_resource['id'], {
                'limit': 100,
                'type': 'ttl'
            })
        self.assertEqual(code, 424)
        self.assertEqual(response['error']['error_code'], 'OE0443')

    def test_constraint_limit_min_max_values(self):
        out_of_limits_values = {
            'ttl': [(-1, 'OE0224'), (720, 'OE0461'),
                    (int(datetime.utcnow().timestamp()) - 1, 'OE0461')],
            'total_expense_limit': [(-1, 'OE0224'), (2147483648, 'OE0224')]
        }
        for constr_type, values in out_of_limits_values.items():
            for value, error_code in values:
                code, response = self.client.resource_constraint_create(
                    self.resource['id'], {
                        'limit': value,
                        'type': constr_type
                    })
                self.assertEqual(code, 400)
                self.assertEqual(response['error']['error_code'], error_code)
        code, constraint_ttl = self.client.resource_constraint_create(
            self.resource['id'], {
                'limit': int(datetime.utcnow().timestamp()) + 3600,
                'type': 'ttl'
            })
        self.assertEqual(code, 201)
        code, constraint_exp_limit = self.client.resource_constraint_create(
            self.resource['id'], {
                'limit': 100,
                'type': 'total_expense_limit'
            })
        self.assertEqual(code, 201)
        constraint_map = {
            'ttl': constraint_ttl,
            'total_expense_limit': constraint_exp_limit
        }
        for constr_type, values in out_of_limits_values.items():
            constraint = constraint_map[constr_type]
            for value, error_code in values:
                code, response = self.client.resource_constraint_update(
                    constraint['id'], {'limit': value})
                self.assertEqual(code, 400)
                self.assertEqual(response['error']['error_code'], error_code)

    def test_create_constraint_invalid_type(self):
        constraint = {
            'limit': 721,
        }
        code, response = self.client.resource_constraint_create(
            self.resource['id'], constraint)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0216')

        constraint['type'] = 'invalid'
        code, response = self.client.resource_constraint_create(
            self.resource['id'], constraint)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0004')

    def test_create_infinity_constraint(self):
        self.valid_constraint['limit'] = 0
        code, constraint = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 201)
        self.assertEqual(constraint['resource_id'], self.resource['id'])
        self.assertEqual(constraint['type'], ConstraintTypes.TTL.value)
        self.assertEqual(constraint['limit'], 0)

    def test_resource_constraint_events(self):
        user_info = {
            'display_name': 'John Doe', 'id': self._user_id,
            'email': 'example@hystax.com'
        }
        self.p_get_user_info.return_value = user_info

        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        limit = int(datetime.utcnow().timestamp()) + 3600
        code, constraint = self.client.resource_constraint_create(
            self.resource['id'], {'limit': limit, 'type': 'ttl'})
        self.assertEqual(code, 201)
        evt_args = dict(
            c_type='ttl',
            r_name=self.resource['name'],
            r_id=self.resource['id'],
            u_name=user_info['display_name'],
            u_email=user_info['email']
        )
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.resource['id'], 'resource',
            'constraint_created', {
                'object_name': self.resource['name'],
                'constraint_type': 'ttl'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, response = self.client.resource_constraint_update(
            constraint['id'], {'limit': limit})
        self.assertEqual(code, 200)
        p_publish_activities.assert_not_called()

        code, response = self.client.resource_constraint_update(
            constraint['id'], {'limit': limit - 100})
        self.assertEqual(code, 200)
        evt_args['params'] = 'limit: %s' % (limit - 100)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.resource['id'], 'resource',
            'constraint_updated', {
                'object_name': self.resource['name'],
                'constraint_type': 'ttl',
                'params': 'limit: %s' % (limit - 100)
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.resource_constraint_delete(constraint['id'])
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.organization['id'], self.resource['id'], 'resource',
            'constraint_deleted', {
                'object_name': self.resource['name'],
                'constraint_type': 'ttl'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_create_constraint_dependent(self):
        cluster_id = str(uuid.uuid4())
        self.resources_collection.update_one(
            filter={
                '_id': self.resource['id']
            },
            update={'$set': {
                    'cluster_id': cluster_id
                    }}
        )
        code, res = self.client.resource_constraint_create(
            self.resource['id'], self.valid_constraint)
        self.assertEqual(code, 424)
        self.assertEqual(res['error']['error_code'], 'OE0464')

    def test_get_resource_constraint_for_zero_pool_policy(self):
        code, response = self.client.rules_list(self.organization['id'])
        self.assertEqual(code, 200)
        rules = response['rules']
        self.assertEqual(len(rules), 1)
        created_cloud_rule = rules[0]
        self.set_allowed_pair(self.user_id, created_cloud_rule['pool_id'])
        code, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.assertEqual(code, 200)
        bp = {
            'limit': 0,
            'type': 'ttl'
        }
        code, policy = self.client.pool_policy_create(
            created_cloud_pool['id'], bp)
        self.assertEqual(code, 201)
        code, resp = self.cloud_resource_create(
            self.cloud_acc['id'], {
                'cloud_resource_id': self.gen_id(),
                'name': 'res_name',
                'resource_type': 'res_type',
                'employee_id': self.employee['id'],
                'pool_id': created_cloud_pool['id']
            })
        self.assertEqual(code, 201)
        code, cloud_resource = self.client.cloud_resource_get(
            resp['id'], details=True)
        self.assertEqual(code, 200)
        cloud_resource_details = cloud_resource['details']
        policies = cloud_resource_details['policies']
        self.assertEqual(len(policies), 1)
        ttl = policies['ttl']
        self.assertEqual(ttl['limit'], 0)
