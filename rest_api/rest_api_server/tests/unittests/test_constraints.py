from datetime import datetime, timedelta
import time
from unittest.mock import patch, call, ANY
from freezegun import freeze_time
from pymongo import UpdateOne

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.models.db_factory import DBType, DBFactory
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import (ResourceConstraint, PoolPolicy)
from rest_api.rest_api_server.models.enums import ConstraintTypes

from tools.cloud_adapter.model import InstanceResource


REDISCOVER_TIME = 300


class TestConstraints(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        self.session = BaseDB.session(engine)()
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        self.valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.org_id = self.org['id']
        self.org_name = self.org['name']
        user_id = self.gen_id()
        self.valid_employee = {
            'name': 'Eliot Alderson', 'auth_user_id': user_id
        }
        _, self.employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        self.employee_id = self.employee['id']
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee_id)
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, auth_user_id=user_id)
        self.cloud_acc_id = cloud_account['id']
        self.pool_id = self.org['pool_id']
        self._mock_auth_user(user_id)
        patch('rest_api.rest_api_server.handlers.v1.base.BaseAuthHandler.'
              'get_meta_by_token',
              return_value={'user_id': user_id,
                            'valid_until': time.time() * 2}
              ).start()
        self.instances = self.get_instances()
        self.m_recipients = patch(
            'rest_api.rest_api_server.controllers.limit_hit.'
            'LimitHitsController._get_recipients').start()
        self.m_supported_constraint_types = patch(
            'rest_api.rest_api_server.controllers.resource_constraint.'
            'ConstraintBaseController.supported_constraint_types',
            return_value=[
                ConstraintTypes.TTL,
                ConstraintTypes.DAILY_EXPENSE_LIMIT,
                ConstraintTypes.TOTAL_EXPENSE_LIMIT
            ]).start()
        self.m_activities = patch(
            'rest_api.rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()

    def mock_assign_resources(self, data):
        updates = []
        for k, v in data.items():
            owner_id, pool_id = v
            updates.append(UpdateOne(
                filter={'_id': k},
                update={'$set': {
                    'pool_id': pool_id,
                    'employee_id': owner_id,
                }}
            ))
        self.resources_collection.bulk_write(updates)

    def get_expenses(self, instances):
        expenses_list = []
        for instance in instances:
            today = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0)
            for dt, cost in [(today - timedelta(days=14), 2),
                             (today, 3)]:
                expenses_list.append({
                    'resource_id': instance['id'] if isinstance(
                        instance, dict) else instance.resource_id,
                    'cloud_account_id':
                        instance['cloud_account_id'] if isinstance(
                            instance, dict) else instance.cloud_account_id,
                    'date': dt,
                    'cost': cost,
                    'sign': 1
                })
        return expenses_list

    def update_expenses(self, expenses, extend=False):
        if extend:
            self.expenses.extend(expenses)
        else:
            self.expenses = expenses
        resource_ids = list(map(lambda x: x['resource_id'], expenses))
        self.update_resource_info_by_expenses(resource_ids)

    def get_instances(self, org_id=None):
        tags = {'tn': 'tv'}
        if not org_id:
            org_id = self.org_id
        i1 = InstanceResource(
            cloud_resource_id='i-aaa',
            cloud_account_id=self.cloud_acc_id,
            region='us-1',
            name='Instance1',
            flavor='t1-tiny',
            tags=tags,
        )
        i2 = InstanceResource(
            cloud_resource_id='i-aab',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='instance2',
            flavor='t1-tiny',
            tags=tags,
        )
        i3 = InstanceResource(
            cloud_resource_id='i-ccb',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='Instance3',
            flavor='t1-tiny',
            tags=tags,
        )
        i4 = InstanceResource(
            cloud_resource_id='i-cbe',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='INstance7',
            flavor='t777-superlarge',
            tags=tags,
        )
        return [i1, i2, i3, i4]

    def get_auth_users(self, employees):
        auth_users = []
        for employee in employees:
            id = self.gen_id()
            name = 'test__%s' % id
            auth_users.append({
                'assignment_resource_id': employee['organization_id'],
                'user_display_name': name,
                'user_email': '%s@%s.com' % (id, name),
                'user_id': employee['auth_user_id']
            })
        return auth_users

    def create_resource_constraints(self, resources, constraint_type=None,
                                    limit=1, is_cluster=False):
        constraints = []
        constraint_types = []
        try:
            ConstraintTypes(constraint_type)
            constraint_types.append(constraint_type)
        except ValueError:
            constraint_types.extend(map(lambda c: c.value, ConstraintTypes))
        for resource in resources:
            keys = ('id', 'resource_id') if not is_cluster else ('cluster_id', 'cluster_id')
            r_id = resource[keys[0]] if isinstance(
                resource, dict) else getattr(resource, keys[1])
            for constraint_type in constraint_types:
                constraints.append(ResourceConstraint(
                    type=constraint_type,
                    limit=limit,
                    resource_id=r_id,
                    organization_id=self.org_id,
                ))
        self.session.add_all(constraints)
        self.session.commit()
        return constraints

    def update_resource_constraints(self, constraints, limit):
        for constraint in constraints:
            constraint.limit = limit
        self.session.commit()

    def create_pool_constraints(self, pool_ids, constraint_type=None, limit=1):
        constraints = []
        constraint_types = []
        try:
            ConstraintTypes(constraint_type)
            constraint_types.append(constraint_type)
        except ValueError:
            constraint_types.extend(map(lambda c: c.value, ConstraintTypes))
        for pool_id in pool_ids:
            for constraint_type in constraint_types:
                constraints.append(PoolPolicy(
                    type=constraint_type,
                    limit=limit,
                    pool_id=pool_id,
                    organization_id=self.org_id,
                ))
        self.session.add_all(constraints)
        self.session.commit()
        return constraints

    def assign_resources(self, resources, pool_id, employee_id, include_cluster=False):
        assign_data = {}
        for resource in resources:
            assign_data[resource['id']] = (employee_id, pool_id)
            if include_cluster:
                assign_data[resource['cluster_id']] = (employee_id, pool_id)
        self.mock_assign_resources(assign_data)

    def create_cluster_type(self, name=None, tag_key=None):
        if not name:
            name = 'default'
            if not tag_key:
                tag_key = 'tn'
        code, res = self.client.cluster_type_create(
            self.org_id, {'name': name, 'tag_key': tag_key})
        self.assertEqual(code, 201)
        return res

    def discover_and_process_violations(self):
        bulk = [self._to_discovered_resource(r) for r in self.instances]
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc_id, {'resources': bulk}, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        return response['resources']

    def test_no_constraints(self):
        self.update_expenses(self.get_expenses(self.instances))
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        self.discover_and_process_violations()
        self.m_activities.assert_called_once()

    def test_environment_resource_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        code, resource = self.environment_resource_create(
            self.org_id, {'name': 'test', 'resource_type': 'env'})
        self.assertEqual(code, 201)
        resources = [resource]
        self.update_expenses(self.get_expenses(resources))

        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)

        constraints = self.create_resource_constraints(resources)
        self.update_expenses(self.get_expenses(resources))

        # constraint hits
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            code, resp = self.client.process_resource_violations(self.org_id)
            self.assertEqual(code, 204)
            self.m_activities.assert_has_calls([
                call(self.org_id, self.m_recipients.return_value[0]['user_id'],
                     'user', 'constraint_violated', {'violations': [
                        ANY for _ in range(0, len(constraints))]},
                     'alert.violation.constraint_violated')])

        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 3 - 1)):
            # all same, no hits
            code, resp = self.client.process_resource_violations(self.org_id)
            self.assertEqual(code, 204)
            self.m_activities.assert_has_calls([
                call(self.org_id, self.m_recipients.return_value[0]['user_id'],
                     'user', 'constraint_violated', {'violations': [
                        ANY for _ in range(0, len(constraints))]},
                     'alert.violation.constraint_violated')])

            # update constraints limits. constraint hits
            self.update_resource_constraints(constraints, 2)
            code, _ = self.client.process_resource_violations(self.org_id)
            self.assertEqual(code, 204)
            # org_create, pool_create, cloud_acc_create, 2 deactivated
            # rules events + 2 violated
            self.assertEqual(self.m_activities.call_count, 7)

    def test_resource_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        resources = self.discover_and_process_violations()
        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_resource_constraints(resources)
        # constraint hits
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_has_calls([
            call(self.org_id, self.m_recipients.return_value[0]['user_id'],
                 'user', 'constraint_violated', {'violations': [
                    ANY for _ in range(0, len(constraints))]},
                 'alert.violation.constraint_violated')])

        # re-discover. no hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)

        # update constraints limits. constraint hits
        self.update_resource_constraints(constraints, 2)
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 3 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 3)

    def test_cluster_resource_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        self.create_cluster_type()
        # initial
        resources = self.discover_and_process_violations()
        self.assign_resources(
            resources, self.pool_id, self.employee_id, include_cluster=True)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_resource_constraints([resources[0]],
                                                       is_cluster=True)
        # constraint hits
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_has_calls([
            call(self.org_id, ANY, 'rule', 'rule_deactivated', ANY,
                 'rule.rule_deactivated', add_token=True),
            call(self.org_id, self.m_recipients.return_value[0]['user_id'],
                 'user', 'constraint_violated', {'violations': [
                    ANY for _ in range(0, len(constraints))]},
                 'alert.violation.constraint_violated')])
        self.assertEqual(self.m_activities.call_count, 2)
        for constraint in self.m_activities.call_args[0][4]['violations']:
            self.assertEqual(resources[0]['cluster_id'],
                             constraint['resource_id'])

        # re-discover. no hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)

        # update constraints limits. constraint hits
        self.update_resource_constraints(constraints, 2)
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 3 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 3)

    def test_resource_constraint_combi(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        resources = self.discover_and_process_violations()

        self.assign_resources(
            resources[1:], self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        self.create_resource_constraints(resources)
        # constraint hits
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        # send alert to resource owner
        self.assertEqual(self.m_activities.call_count, 2)

    def test_pool_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            resources = self.discover_and_process_violations()

        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_pool_constraints([self.pool_id])
        # constraint hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_called_with(
            self.org_id, self.m_recipients.return_value[0]['user_id'], 'user',
            'constraint_violated', {'violations': [
                ANY for _ in range(0, len(constraints) * len(self.instances))]},
            'alert.violation.constraint_violated')

        # re-discover. no hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 3 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)

        # update constraints limits. constraint hits
        self.update_resource_constraints(constraints, 2)
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 4 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 3)

    def test_cluster_pool_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        self.create_cluster_type()
        # initial
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            resources = self.discover_and_process_violations()

        self.assign_resources(
            resources, self.pool_id, self.employee_id, include_cluster=True)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_pool_constraints([self.pool_id])
        # constraint hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_called_with(
            self.org_id, self.m_recipients.return_value[0]['user_id'], 'user',
            'constraint_violated', {
                'violations': [ANY for _ in range(0, len(constraints))]},
            'alert.violation.constraint_violated')

        # re-discover. no hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 3 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)

        # update constraints limits. constraint hits
        self.update_resource_constraints(constraints, 2)
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 4 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 3)

    def test_pool_constraint_different_owner(self):
        self.valid_employee['auth_user_id'] = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        auth_responses = self.get_auth_users([employee, self.employee])
        self.m_recipients.return_value = auth_responses
        # initial
        resources = self.discover_and_process_violations()

        self.assign_resources(
            resources, self.pool_id, employee['id'])
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_pool_constraints([self.pool_id])
        # constraint hit. Expect alerts for employee and pool owner
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_has_calls([
            call(self.org_id, auth_responses[0]['user_id'], 'user',
                 'constraint_violated', {'violations': [
                    ANY for _ in range(
                        0, len(constraints) * len(self.instances))]},
                 'alert.violation.constraint_violated')])

    def test_constraint_overlap(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        resources = self.discover_and_process_violations()

        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_pool_constraints([self.pool_id], limit=1)
        # pool constraint hit
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 2)
        self.m_activities.assert_has_calls([
            call(self.org_id, ANY, 'rule', 'rule_deactivated', ANY,
                 'rule.rule_deactivated', add_token=True),
            call(self.org_id, self.m_recipients.return_value[0]['user_id'],
                 'user', 'constraint_violated',
                 {'violations': [ANY for _ in range(
                     0, len(constraints) * len(self.instances))]},
                 'alert.violation.constraint_violated')
        ])
        self.m_activities.reset_mock()

        constraints = self.create_resource_constraints(resources, limit=2)
        # resource constraint hit
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.m_activities.assert_has_calls([call(
            self.org_id, self.m_recipients.return_value[0]['user_id'], 'user',
            'constraint_violated', {'violations': [ANY for _ in range(
                0, len(constraints))]}, 'alert.violation.constraint_violated')])

    def test_pool_constraint_split_owner(self):
        self.valid_employee['auth_user_id'] = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        auth_users = self.get_auth_users([employee, self.employee])
        self.m_recipients.return_value = auth_users
        # initial
        resources = self.discover_and_process_violations()

        emp1_rss = []
        emp2_rss = []
        for i, rss in enumerate(resources):
            if i % 2 == 0:
                emp1_rss.append(rss)
            else:
                emp2_rss.append(rss)
        self.assign_resources(
            emp1_rss, self.pool_id, employee['id'])
        self.assign_resources(
            emp2_rss, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(emp1_rss), extend=True)
        self.update_expenses(self.get_expenses(emp2_rss), extend=True)
        constraints = self.create_pool_constraints([self.pool_id])
        # constraint hit. Expect:
        # - 3 alerts for employee 1 as a resource owner,
        # - 3 alerts for employee 2 as a resource owner,
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 3)
        meta = {'violations': [
            ANY for _ in range(0, len(constraints) * len(emp1_rss))]}
        calls = []
        for auth_user in auth_users:
            calls.append(call(self.org_id, auth_user['user_id'],
                              'user', 'constraint_violated', meta,
                              'alert.violation.constraint_violated'))

    def test_pool_constraint_pool_change(self):
        _, pool = self.client.pool_create(self.org_id, {
            'name': 'sub', 'parent_id': self.org['pool_id']})
        auth_users = self.get_auth_users([self.employee])
        scoped_user = auth_users[0].copy()
        scoped_user['assignment_resource_id'] = pool['id']
        scoped_user['user_id'] = self.gen_id()
        auth_users.append(scoped_user)
        self.m_recipients.side_effect = [[], auth_users, auth_users]
        # initial
        resources = self.discover_and_process_violations()

        self.update_expenses(self.get_expenses(resources))
        self.assign_resources(
            resources, self.org['pool_id'], self.employee_id)
        constraints = self.create_pool_constraints([self.org['pool_id']])
        # constraint hit
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        # pool created + rule deactivated + 1 violated
        self.assertEqual(self.m_activities.call_count, 3)

        self.update_expenses(self.get_expenses(resources))
        self.assign_resources(resources, pool['id'], self.employee_id)
        self.create_pool_constraints([pool['id']])
        # constraint hit after pool change
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 4)
        meta = {'violations': [
            ANY for _ in range(0, len(constraints) * len(self.instances))]}
        self.m_activities.assert_has_calls([call(
            self.org_id, auth_users[0]['user_id'], 'user',
            'constraint_violated', meta, 'alert.violation.constraint_violated')])

    def test_pool_constraint_cross_ownership(self):
        _, pool1 = self.client.pool_create(self.org_id, {
            'name': 'sub1', 'parent_id': self.org['pool_id']})
        _, pool2 = self.client.pool_create(self.org_id, {
            'name': 'sub2', 'parent_id': self.org['pool_id']})

        employee = {
            'name': 'Second Employee', 'auth_user_id': self.gen_id()
        }
        _, employee = self.client.employee_create(
            self.org_id, employee)

        employee['organization_id'] = pool1['id']
        auth_users = self.get_auth_users(
            [employee, self.employee])

        self.m_recipients.return_value = auth_users
        # initial
        resources = self.discover_and_process_violations()

        org_employee_rss = []
        unit_employee_rss = []
        for i, rss in enumerate(resources):
            if i % 2 == 0:
                org_employee_rss.append(rss)
            else:
                unit_employee_rss.append(rss)
        self.assign_resources(
            org_employee_rss, pool1['id'], self.employee['id'])
        self.assign_resources(
            unit_employee_rss, pool2['id'], employee['id'])
        self.update_expenses(self.get_expenses(org_employee_rss), extend=True)
        self.update_expenses(self.get_expenses(unit_employee_rss), extend=True)
        constraints = self.create_pool_constraints(
            [pool1['id'], pool2['id']])
        # constraint hit. Expect:
        # - 4 alerts for employee as resource owner
        # - 4 alerts for employee2 as resource owner
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        # 2 pools created, 1 deactivated rule + 2 violated
        self.assertEqual(self.m_activities.call_count, 5)
        meta = {'violations': [ANY for _ in range(0, len(constraints))]}
        calls = []
        for auth_user in auth_users:
            calls.append(call(self.org_id, auth_user['user_id'],
                              'user', 'constraint_violated', meta,
                              'alert.violation.constraint_violated'))
        self.m_activities.assert_has_calls(calls, any_order=True)

    def test_resource_infinity_constraint(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        resources = self.discover_and_process_violations()
        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_resource_constraints(resources, limit=0)
        # constraint hits
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 1)

    def test_pool_constraint_with_zero_limit(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        now = int(datetime.utcnow().timestamp())
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            resources = self.discover_and_process_violations()

        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_pool_constraints([self.pool_id], limit=0)
        # constraint hits
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME * 2 - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 1)

    def test_owner_constraint_activities_task(self):
        slack_user_id = self.gen_id()
        valid_slack_employee = {
            'name': 'Slack user', 'auth_user_id': slack_user_id
        }
        _, slack_employee = self.client.employee_create(
            self.org_id, valid_slack_employee)

        self.m_recipients.return_value = self.get_auth_users(
            [self.employee, slack_employee])

        # initial
        resources = self.discover_and_process_violations()
        self.assign_resources(resources, self.pool_id,
                              slack_employee['id'])
        self.update_expenses(self.get_expenses(resources))
        constraints = self.create_resource_constraints(resources)
        # constraint hits
        now = int(datetime.utcnow().timestamp())

        self.m_activities.reset_mock()
        with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
            self.discover_and_process_violations()
        self.assertEqual(self.m_activities.call_count, 1)
        meta = {'violations': ANY}
        self.m_activities.assert_called_once_with(
            self.org_id, slack_user_id, 'user', 'constraint_violated', meta,
            'alert.violation.constraint_violated')

    def test_disable_enable_constraint_types(self):
        self.m_recipients.return_value = self.get_auth_users([self.employee])
        # initial
        resources = self.discover_and_process_violations()
        self.assign_resources(
            resources, self.pool_id, self.employee_id)
        self.update_expenses(self.get_expenses(resources))
        self.create_resource_constraints(resources)
        # constraint hits
        now = int(datetime.utcnow().timestamp())
        call_count = 1
        for constraint_type in ConstraintTypes:
            call_count += 1
            self.m_supported_constraint_types.return_value = [constraint_type]
            with freeze_time(datetime.fromtimestamp(now + REDISCOVER_TIME - 1)):
                self.discover_and_process_violations()
            self.assertEqual(self.m_activities.call_count, call_count)
