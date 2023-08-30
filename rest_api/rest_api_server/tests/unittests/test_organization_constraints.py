from datetime import datetime, timedelta
from unittest.mock import patch

from sqlalchemy import and_

from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.models import (OrganizationConstraintTypes,
                                                    OrganizationLimitHit)
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import get_nil_uuid


class TestOrganizationConstraints(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        self.org_id = self.org['id']
        self.org_name = self.org['name']
        user_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': user_id
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        self.employee_id = self.employee['id']
        self.pool_id = self.org['pool_id']
        self.pool_name = self.org_name

        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        cloud_acc = {
            'name': 'cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc, auth_user_id=user_id)

        self.valid_constraint_params = {
            "name": "constraint",
            "type": "resource_count_anomaly",
            "definition": {
                "threshold_days": 7,
                "threshold": 30,
            },
            "filters": {
                "pool_id": [self.pool_id],
                "region": ["eu-north-1"]
            }
        }
        self._mock_auth_user(user_id)
        _, self.deleted_org = self.client.organization_create(
            {'name': "deleted"})
        self.delete_organization(self.deleted_org['id'])

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='test_type',
                              name='test_resource', tags=None, last_seen=None,
                              region=None, created_by_kind=None, created_by_name=None,
                              host_ip=None, instance_address=None, k8s_namespace=None,
                              k8s_node=None, pod_ip=None, first_seen=None, k8s_service=None,
                              service_name=None):
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
            'service_name': service_name
        }

        if tags:
            resource.update({'tags': tags})
        if created_by_kind:
            resource.update({'created_by_kind': created_by_kind})
        if created_by_name:
            resource.update({'created_by_name': created_by_name})
        if host_ip:
            resource.update({'host_ip': host_ip})
        if instance_address:
            resource.update({'instance_address': instance_address})
        if k8s_namespace:
            resource.update({'k8s_namespace': k8s_namespace})
        if k8s_node:
            resource.update({'k8s_node': k8s_node})
        if pod_ip:
            resource.update({'pod_ip': pod_ip})
        if k8s_service:
            resource.update({'k8s_service': k8s_service})
        code, resource = self.cloud_resource_create(
            cloud_account_id, resource)
        return code, resource

    def test_create_resource_count_constraints(self):
        params = self.valid_constraint_params.copy()
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region=params['filters']['region'][0])
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        params['filters'].pop('pool_id', None)
        params['filters']['pool'] = [{
            'id': self.pool_id, 'name': self.pool_name,
            'purpose': 'business_unit'}]
        params['filters']['region'] = [{
            'name': params['filters']['region'][0],
            'cloud_type': self.cloud_acc['type']}]
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            self.assertIsNotNone(resp.get(p))
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_expense_anomaly(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region=params['filters']['region'][0])
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        params['filters'].pop('pool_id', None)
        params['filters']['pool'] = [{
            'id': self.pool_id, 'name': self.pool_name,
            'purpose': 'business_unit'}]
        params['filters']['region'] = [{
            'name': params['filters']['region'][0],
            'cloud_type': self.cloud_acc['type']}]
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_clean_expenses_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        self.assertEqual(code, 201)

        params = self.valid_constraint_params.copy()
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'tag': 'val'})
        self.assertEqual(code, 201)

        params['filters'] = {'cloud_account_id': [get_nil_uuid()]}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)

    def test_create_filters(self):
        region = 'us-west-1'
        service_name = 'AWS svc'
        resource_type = 'Instance'
        tag_key = 'tag_key'
        _, resource = self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1', region=region,
            resource_type=resource_type, service_name=service_name,
            tags={tag_key: 'tag_val'})
        self._make_resources_active([resource['id']])

        params = self.valid_constraint_params.copy()
        params['filters'] = {
            'region': [region],
            'service_name': [service_name],
            'resource_type': ['%s:regular' % resource_type],
            'cloud_account_id': [self.cloud_acc['id']],
            'tag': [tag_key],
            'active': True
        }

        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        params['filters'].pop('cloud_account_id', None)
        params['filters']['cloud_account'] = [{
            'id': self.cloud_acc['id'],
            'name': self.cloud_acc['name'],
            'type': self.cloud_acc['type']}]
        params['filters']['region'] = [{
            'name': region,
            'cloud_type': self.cloud_acc['type']}]
        params['filters']['service_name'] = [{
            'name': service_name,
            'cloud_type': self.cloud_acc['type']}]
        params['filters']['resource_type'] = [{
            'name': resource_type,
            'type': 'regular'}]
        params['filters']['active'] = [True]
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_wrong_filters_format(self):
        filters_map = {
            'cloud_account_id': (self.cloud_acc['id'], 'OE0385'),
            'region': ('us-west-1', 'OE0385'),
            'service_name': ('AWS svc', 'OE0385'),
            'resource_type': (True, 'OE0385'),
            'tag': (1, 'OE0385'),
            'active': ([True], 'OE0226'),
        }

        params = self.valid_constraint_params.copy()
        for k, v in filters_map.items():
            params['filters'] = {k: v[0]}
            code, resp = self.client.organization_constraint_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], v[1])

    def test_create_resource_quota(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RESOURCE_QUOTA.value
        params['definition'] = {'max_value': 0}
        params['filters'] = {}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            self.assertIsNotNone(resp.get(p))
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_recurring_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RECURRING_BUDGET.value
        params['definition'] = {'monthly_budget': 0}
        params['filters'] = {}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            self.assertIsNotNone(resp.get(p))
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_expiring_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'total_budget': 0, 'start_date': 0}
        params['filters'] = {}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_tagging_policy(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {
            'start_date': 0,
            'conditions': {'tag': 'tag1', 'without_tag': 'tag2'}}
        params['filters'] = {}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        params['organization_id'] = self.org_id
        for p in ['id', 'created_at', 'deleted_at', 'last_run', 'last_run_result']:
            self.assertIsNotNone(resp.get(p))
            resp.pop(p, None)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp, params)

    def test_create_with_last_run(self):
        params = self.valid_constraint_params.copy()
        params['filters'] = {}
        params['last_run'] = 0
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_create_with_last_run_result(self):
        params = self.valid_constraint_params.copy()
        params['filters'] = {}
        params['last_run_result'] = {'some': 'result'}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_create_invalid_org(self):
        params = ['123', self.deleted_org['id']]
        for p in params:
            code, resp = self.client.organization_constraint_create(
                p, self.valid_constraint_params)
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_missing_params(self):
        required_params = self.valid_constraint_params.copy()
        required_params.pop('filters', None)
        for key in required_params.keys():
            params = required_params.copy()
            params.pop(key, None)
            code, resp = self.client.organization_constraint_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_filtering_unavailable(self):
        params = self.valid_constraint_params.copy()
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region='us-west-1')
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0504')

    def test_create_filtering_wrong_resource_type(self):
        resource_type = 'Instance'

        params = self.valid_constraint_params.copy()
        params['filters']['resource_type'] = [resource_type]

        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            resource_type=resource_type)
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0218')

    def test_create_unexpected_param(self):
        params = self.valid_constraint_params.copy()
        params['filters'] = {}
        params['param'] = '123'
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_create_invalid_threshold(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold'] = '123'
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_threshold(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold'] = -123
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_threshold(self):
        params = self.valid_constraint_params.copy()
        params['definition'].pop('threshold', None)
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_threshold_days(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold_days'] = '123'
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_threshold_days(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold_days'] = -123
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_below_minimum_threshold_days(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold_days'] = 0
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_exceeded_threshold_days(self):
        params = self.valid_constraint_params.copy()
        params['definition']['threshold_days'] = 181
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_threshold_days(self):
        params = self.valid_constraint_params.copy()
        params['definition'].pop('threshold_days', None)
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_max_value(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RESOURCE_QUOTA.value
        params['definition'] = {'max_value': 'str'}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_max_value(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RESOURCE_QUOTA.value
        params['definition'] = {'max_value': -123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_max_value(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RESOURCE_QUOTA.value
        params['definition'].pop('max_value', None)
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_monthly_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RECURRING_BUDGET.value
        params['definition'] = {'monthly_budget': 'str'}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_monthly_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RECURRING_BUDGET.value
        params['definition'] = {'monthly_budget': -123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_monthly_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.RECURRING_BUDGET.value
        params['definition'].pop('monthly_budget', None)
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_total_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'start_date': 0, 'total_budget': 'str'}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_total_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'start_date': 0, 'total_budget': -123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_total_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'start_date': 0}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_start_date_expiring_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'start_date': 'str', 'total_budget': 123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_invalid_start_date_tagging_policy(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {
            'start_date': 'str',
            'conditions': {'tag': 'tag1', 'without_tag': 'tag2'}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0223')

    def test_create_negative_start_date_expiring_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'start_date': -123, 'total_budget': 123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_negative_start_date_tagging_policy(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {
            'start_date': -123,
            'conditions': {'tag': 'tag1', 'without_tag': 'tag2'}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0224')

    def test_create_without_start_date_expiring_budget(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.EXPIRING_BUDGET.value
        params['definition'] = {'total_budget': 123}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_without_start_date_tagging_policy(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {
            'conditions': {
                'tag': 'tag1',
                'without_tag': 'tag2'
            }
        }
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_conditions(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1, 'conditions': 'str'}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_empty_conditions(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1, 'conditions': {}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_without_conditions(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1, 'conditions': None}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0216')

    def test_create_invalid_condition_in_conditions(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1,
                                'conditions': {'some': 'cond'}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0517')

    def test_create_invalid_tag(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1, 'conditions': {'tag': 123}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0214')

    def test_create_invalid_without_tag(self):
        params = self.valid_constraint_params.copy()
        params['type'] = OrganizationConstraintTypes.TAGGING_POLICY.value
        params['definition'] = {'start_date': 1,
                                'conditions': {'without_tag': 123}}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0214')

    def test_create_invalid_type(self):
        params = self.valid_constraint_params.copy()
        params['type'] = '123'
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0004')

    def test_create_invalid_filters(self):
        params = self.valid_constraint_params.copy()
        for p in ['123', 123]:
            params['filters'] = p
            code, resp = self.client.organization_constraint_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0344')

    def test_create_unexpected_filters(self):
        params = self.valid_constraint_params.copy()
        for p in ['name_like', 'cloud_resource_id_like']:
            params['filters'] = {p: p}
            code, resp = self.client.organization_constraint_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_create_invalid_entity_in_filters(self):
        params = self.valid_constraint_params.copy()
        for p in ['pool_id', 'cloud_account_id', 'owner_id']:
            params['filters'][p] = ['123']
            code, resp = self.client.organization_constraint_create(
                self.org_id, params)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_create_pool_with_subs_filters(self):
        params = self.valid_constraint_params.copy()
        pool_id = params['filters']['pool_id'][0] + '+'
        params['filters']['pool_id'][0] = pool_id

        self.create_cloud_resource(self.cloud_acc['id'], name='name_1',
                                   region=params['filters']['region'][0])

        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters']['pool'][0]['id'], pool_id)

    def test_create_incompatible_filters(self):
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0504')

    def test_create_not_overlapping_valid_filters(self):
        # make region a valid filter value by creating resource with region
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region=self.valid_constraint_params['filters']['region'][0])
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters']['pool'][0]['id'], self.pool_id)
        self.assertEqual(resp['filters']['region'][0]['name'],
                         self.valid_constraint_params['filters']['region'][0])

    def test_create_not_overlapping_invalid_filter_value(self):
        fake_region = 'eu-test'
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1', region=fake_region)
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0504')

    def test_create_not_overlapping_valid_invalid_filter_value(self):
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region=self.valid_constraint_params['filters']['region'][0])
        params = self.valid_constraint_params.copy()
        fake_region = 'eu-tes'
        params['filters']['region'].append(fake_region)

        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0504')

    def test_create_optscale_entity_in_filter(self):
        _, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.pool_id,
        })
        pool_filter = {
            'id': pool['id'], 'name': pool['name'], 'purpose': pool['purpose']
        }
        self.create_cloud_resource(
            self.cloud_acc['id'], name='name_1',
            region='eu-central-1', pool_id=self.pool_id)
        params = self.valid_constraint_params.copy()
        params['filters'].pop('region', None)
        params['filters']['pool_id'] = [pool['id']]
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['filters']['pool']), 1)
        self.assertDictEqual(resp['filters']['pool'][0], pool_filter)

    def test_create_without_tag_filter(self):
        self.create_cloud_resource(self.cloud_acc['id'], tags={'tag': 'tag'})
        params = self.valid_constraint_params.copy()
        params['filters'] = {'without_tag': ['tag']}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)
        self.assertDictEqual(resp['filters'], params['filters'])

    def test_create_invalid_name(self):
        params = self.valid_constraint_params.copy()
        params['filters'] = {}
        params['name'] = 123
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0214')

    def test_create_empty_filters(self):
        params = self.valid_constraint_params.copy()
        params['filters'] = {}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)

    def test_constraint_list(self):
        count = 3
        for x in range(0, count):
            self.create_org_constraint(self.org_id, self.pool_id)
        code, resp = self.client.organization_constraint_list(self.org_id)
        pool_constraints = list(filter(lambda x: 'pool' in x['filters'],
                                       resp['organization_constraints']))
        self.assertEqual(code, 200)
        self.assertEqual(len(pool_constraints), count)

    def test_list_constraints_by_types(self):
        quota = self.create_org_constraint(
            self.org_id, self.pool_id, constraint_type='resource_quota')
        rec_budget = self.create_org_constraint(
            self.org_id, self.pool_id, constraint_type='recurring_budget')
        self.create_org_constraint(
            self.org_id, self.pool_id, constraint_type='expiring_budget')
        code, resp = self.client.organization_constraint_list(
            self.org_id, type=['resource_quota', 'recurring_budget'])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['organization_constraints']), 2)
        for x in resp['organization_constraints']:
            self.assertIn(x['id'], [quota['id'], rec_budget['id']])

    def test_list_invalid_type(self):
        self.create_org_constraint(
            self.org_id, self.pool_id, constraint_type='resource_quota')
        code, resp = self.client.organization_constraint_list(
            self.org_id, type='unknown')
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['organization_constraints']), 0)

    def test_list_constraints_with_hit_days(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        created_at = int((datetime.utcnow() - timedelta(days=2)).timestamp())
        old_hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                            constraint_id=constr['id'],
                                            created_at=created_at)
        hit = self.create_org_limit_hit(self.org_id, self.pool_id,
                                        constraint_id=constr['id'])
        code, resp = self.client.organization_constraint_list(self.org_id,
                                                              hit_days=1)
        self.assertEqual(code, 200)
        # 1 constraint + 2 default constraints for organization
        self.assertEqual(len(resp['organization_constraints']), 3)
        resp_constraint = [x for x in resp['organization_constraints']
                           if x['id'] == constr['id']][0]
        self.assertEqual(resp_constraint['limit_hits'][0]['id'], hit['id'])
        self.assertNotIn(
            'constraint', resp['organization_constraints'][0].keys())

    def test_limit_hit_with_invalid_hit_days(self):
        code, resp = self.client.organization_constraint_list(self.org_id,
                                                              hit_days='str')
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0217')

    def test_constraint_list_empty(self):
        code, resp = self.client.organization_constraint_list(self.org_id)
        for c in resp['organization_constraints']:
            self.client.organization_constraint_delete(c['id'])
        code, resp = self.client.organization_constraint_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['organization_constraints']), 0)

    def test_constraint_list_invalid_org(self):
        params = ['123', self.deleted_org['id']]
        for p in params:
            code, resp = self.client.organization_constraint_list(p)
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        code, resp = self.client.organization_constraint_delete(constr['id'])
        self.assertEqual(code, 204)
        self.assertEqual(resp, None)

    def test_delete_constraint_with_hits(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        self.create_org_limit_hit(self.org_id, self.pool_id,
                                  constraint_id=constr['id'])
        code, resp = self.client.organization_constraint_delete(constr['id'])
        self.assertEqual(code, 204)
        self.assertEqual(resp, None)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        hits = session.query(OrganizationLimitHit).filter(and_(
            OrganizationLimitHit.organization_id == self.org_id,
            OrganizationLimitHit.deleted.is_(False)
            )).one_or_none()
        self.assertEqual(hits, None)

    def test_delete_invalid(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        params = ['str', constr['id']]
        for p in params:
            code, resp = self.client.organization_constraint_delete(p)
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete_deleted(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        code, resp = self.client.organization_constraint_delete(constr['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_get_constraint(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        code, resp = self.client.organization_constraint_get(constr['id'])
        self.assertEqual(code, 200)
        self.assertIn('pool', resp['filters'])

    def test_get_invalid(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        params = ['str', constr['id']]
        for p in params:
            code, resp = self.client.organization_constraint_get(p)
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_patch_constraint(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        mutable = {'name': 'name', 'last_run': 123}
        for k, v in mutable.items():
            code, resp = self.client.organization_constraint_update(
                constr['id'], {k: v})
            self.assertEqual(code, 200)
            self.assertEqual(resp[k], v)
            self.assertIn('pool', resp['filters'])

    def test_patch_anomaly_last_run_result(self):
        def _test(case):
            for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                          OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
                constr = self.create_org_constraint(
                    self.org_id, self.pool_id, {}, type_)
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': case})
                assertion_message = 'Error on %s constraint update' % type_
                self.assertEqual(code, 200, assertion_message)
                self.assertIsInstance(resp.get('last_run_result'), dict,
                                      assertion_message)

        last_run_result = {'average': 0, 'today': 0, 'breakdown': {}}
        _test(last_run_result)

        now = int(datetime.utcnow().timestamp())
        average = 2
        last_run_result = {
            'average': average, 'today': 20,
            'breakdown': {now: average, now - 1000: average}
        }
        _test(last_run_result)

    def test_patch_anomaly_last_last_run_result_invalid(self):
        cases = ['total', [1, 2], 1.2]
        for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                      OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            for v in cases:
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': v})
                self.assertEqual(code, 400, assertion_message)
                self.assertEqual(resp['error']['error_code'], 'OE0344', assertion_message)
        verification_template = {
            OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value: (
                ['test', [1.2]], {'today': 'OE0223', 'average': 'OE0466'}),
            OrganizationConstraintTypes.EXPENSE_ANOMALY.value: (
                ['test', [1.2]], {'today': 'OE0466', 'average': 'OE0466'}),
        }
        now = int(datetime.utcnow().timestamp())
        for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                      OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            cases, key_errors_map = verification_template[type_]
            for k, error_code in key_errors_map.items():
                last_run_result = {
                    'average': 2, 'today': 20,
                    'breakdown': {now: 2, now - 1000: 2}
                }
                for v in cases:
                    last_run_result[k] = v
                    code, resp = self.client.organization_constraint_update(
                        constr['id'], {'last_run_result': last_run_result})
                    self.assertEqual(code, 400, assertion_message)
                    self.assertEqual(resp['error']['error_code'],
                                     error_code, assertion_message)

    def test_patch_anomaly_last_last_run_result_unexpected_breakdown(self):
        for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                      OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            last_run_result = {
                'average': 0, 'today': 0,
                'breakdown': {int(datetime.utcnow().timestamp()): 123}
            }
            code, resp = self.client.organization_constraint_update(
                constr['id'], {'last_run_result': last_run_result})
            self.assertEqual(code, 400, assertion_message)
            self.assertEqual(resp['error']['error_code'], 'OE0522', assertion_message)

    def test_patch_anomaly_last_last_run_result_not_provided_breakdown(self):
        for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                      OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            last_run_result = {'average': 1, 'today': 0, 'breakdown': {}}
            code, resp = self.client.organization_constraint_update(
                constr['id'], {'last_run_result': last_run_result})
            self.assertEqual(code, 400, assertion_message)
            self.assertEqual(resp['error']['error_code'], 'OE0216', assertion_message)

    def test_patch_anomaly_last_last_run_result_not_provided(self):
        for type_ in [OrganizationConstraintTypes.RESOURCE_COUNT_ANOMALY.value,
                      OrganizationConstraintTypes.EXPENSE_ANOMALY.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            last_run_result = {'average': 1, 'today': 0, 'breakdown': {}}
            for k in last_run_result.keys():
                last_run_result_dub = last_run_result.copy()
                last_run_result_dub.pop(k)
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': last_run_result_dub})
                self.assertEqual(code, 400, assertion_message)
                self.assertEqual(resp['error']['error_code'], 'OE0216', assertion_message)

    def test_patch_quota_and_budget_last_run_result(self):
        last_run_result = {'limit': 0, 'current': 0}
        for type_ in [OrganizationConstraintTypes.RESOURCE_QUOTA.value,
                      OrganizationConstraintTypes.RECURRING_BUDGET.value,
                      OrganizationConstraintTypes.EXPIRING_BUDGET.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            code, resp = self.client.organization_constraint_update(
                constr['id'], {'last_run_result': last_run_result})
            assertion_message = 'Error on %s constraint update' % type_
            self.assertEqual(code, 200, assertion_message)
            self.assertEqual(resp.get('last_run_result'), last_run_result,
                             assertion_message)

    def test_patch_quota_and_budget_last_run_result_invalid(self):
        float_cases = ['total', [1, 2]]
        int_cases = float_cases + [1.2]
        verification_template = {
            OrganizationConstraintTypes.RESOURCE_QUOTA.value: (int_cases, 'OE0223'),
            OrganizationConstraintTypes.RECURRING_BUDGET.value: (float_cases, 'OE0466'),
            OrganizationConstraintTypes.EXPIRING_BUDGET.value: (float_cases, 'OE0466'),
        }
        for type_ in [OrganizationConstraintTypes.RESOURCE_QUOTA.value,
                      OrganizationConstraintTypes.RECURRING_BUDGET.value,
                      OrganizationConstraintTypes.EXPIRING_BUDGET.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            cases, error_code = verification_template[type_]
            assertion_message = 'Error on %s constraint update' % type_
            for v in cases:
                last_run_result = {'limit': v, 'current': 0}
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': last_run_result})
                self.assertEqual(code, 400, assertion_message)
                self.assertEqual(resp['error']['error_code'], error_code, assertion_message)
            for v in cases:
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': v})
                self.assertEqual(code, 400, assertion_message)
                self.assertEqual(resp['error']['error_code'], 'OE0344', assertion_message)

    def test_patch_quota_and_budget_last_run_result_not_provided(self):
        for type_ in [OrganizationConstraintTypes.RESOURCE_QUOTA.value,
                      OrganizationConstraintTypes.RECURRING_BUDGET.value,
                      OrganizationConstraintTypes.EXPIRING_BUDGET.value]:
            constr = self.create_org_constraint(
                self.org_id, self.pool_id, {}, type_)
            assertion_message = 'Error on %s constraint update' % type_
            for k in ['total', 'count']:
                last_run_result = {k: 1}
                code, resp = self.client.organization_constraint_update(
                    constr['id'], {'last_run_result': last_run_result})
                self.assertEqual(code, 400, assertion_message)
                self.assertEqual(resp['error']['error_code'], 'OE0216', assertion_message)

    def test_patch_tagging_policy_last_run_result(self):
        last_run_result = {'value': 0}
        constr = self.create_org_constraint(
            self.org_id, self.pool_id, {},
            OrganizationConstraintTypes.TAGGING_POLICY.value)
        code, resp = self.client.organization_constraint_update(
            constr['id'], {'last_run_result': last_run_result})
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('last_run_result'), last_run_result)

    def test_patch_tagging_policy_last_run_result_invalid(self):
        cases = ['value', [1, 2], -1]
        constr = self.create_org_constraint(
            self.org_id, self.pool_id, {},
            OrganizationConstraintTypes.TAGGING_POLICY.value)
        for v in cases:
            code, resp = self.client.organization_constraint_update(
                constr['id'], {'last_run_result': v})
            self.assertEqual(code, 400,)
            self.assertEqual(resp['error']['error_code'], 'OE0344')
        last_run_result = {'total': 1}
        code, resp = self.client.organization_constraint_update(
            constr['id'], {'last_run_result': last_run_result})
        self.assertEqual(code, 400, )
        self.assertEqual(resp['error']['error_code'], 'OE0216')

        last_run_result['value'] = 0
        code, resp = self.client.organization_constraint_update(
            constr['id'], {'last_run_result': last_run_result})
        self.assertEqual(code, 400, )
        self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_immutable(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        params = ['organization_id', 'created_at', 'definition', 'filters']
        for p in params:
            code, resp = self.client.organization_constraint_update(
                constr['id'], {p: '123'})
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OE0211')

    def test_patch_unexpected(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        code, resp = self.client.organization_constraint_update(
            constr['id'], {'unexpected': 'param'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OE0212')

    def test_patch_invalid(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id,
                                            deleted=True)
        params = ['str', constr['id']]
        for p in params:
            code, resp = self.client.organization_constraint_update(
                p, {'name': '123'})
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_patch_empty(self):
        constr = self.create_org_constraint(self.org_id, self.pool_id)
        code, resp = self.client.organization_constraint_update(
            constr['id'], {})
        self.assertEqual(code, 200)
        self.assertIn('pool', resp['filters'])

    def test_create_without_filters(self):
        self.valid_constraint_params.pop('filters')
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters'], {})

    def test_create_filters_nil_uuid(self):
        self.create_cloud_resource(self.cloud_acc['id'], name='name_1')
        self.valid_constraint_params['filters'] = {
            'region': [get_nil_uuid()],
            'service_name': [get_nil_uuid()]
        }
        code, resp = self.client.organization_constraint_create(
            self.org_id, self.valid_constraint_params)
        self.assertEqual(code, 201)
        expected_filters = {'service_name': [None], 'region': [None]}
        self.assertEqual(resp['filters'], expected_filters)
        code, constraint = self.client.organization_constraint_get(resp['id'])
        self.assertEqual(code, 200)
        self.assertEqual(constraint['filters'], expected_filters)

    def test_org_creation_constraints(self):
        _, org = self.client.organization_create({'name': "some_org"})
        code, resp = self.client.organization_constraint_list(org['id'])
        self.assertEqual(code, 200)
        expected_constraints = ['expense_anomaly', 'resource_count_anomaly']
        self.assertEqual(len(resp['organization_constraints']),
                         len(expected_constraints))
        for constraint in resp['organization_constraints']:
            self.assertEqual(constraint['definition'],
                             {'threshold_days': 7, 'threshold': 30})
            self.assertEqual(constraint['filters'], {})
            self.assertEqual(constraint['last_run'], 0)
            self.assertIn(constraint['type'], expected_constraints)
            self.assertIn(constraint['name'], [
                'Default - expense anomaly',
                'Default - resource count anomaly'
            ])
            self.assertEqual(constraint['organization_id'], org['id'])

    def test_organization_constraints_traffic_filters(self):
        _, res1 = self.create_cloud_resource(self.cloud_acc['id'])
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': int(datetime.utcnow().timestamp()),
                'type': 1,
                'from': 'region_2',
                'to': 'External',
                'usage': 2,
                'cost': 2,
                'sign': 1
            }
        ]
        params = self.valid_constraint_params.copy()
        params['filters'] = {'traffic_from': ['region0:aws_cnr']}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0504')

        params['filters'] = {'traffic_from': ['region_2:aws_cnr'],
                             'traffic_to': ['External:aws_cnr']}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters']['traffic_from'],
                         [{'name': 'region_2', 'cloud_type': 'aws_cnr'}])
        self.assertEqual(resp['filters']['traffic_to'],
                         [{'name': 'External', 'cloud_type': 'aws_cnr'}])

        params['filters'] = {'traffic_from': ['ANY']}
        code, resp = self.client.organization_constraint_create(
            self.org_id, params)
        self.assertEqual(code, 201)
        self.assertEqual(resp['filters']['traffic_from'], ['ANY'])
