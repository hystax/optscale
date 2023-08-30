import uuid
from copy import deepcopy
import datetime
from unittest.mock import patch

from freezegun import freeze_time

from rest_api.rest_api_server.models.enums import ConstraintTypes
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import ConstraintLimitHit
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestMyTasksApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        code, self.org = self.client.organization_create(
            {'name': "organization"})
        self.client.pool_update(self.org['pool_id'], {'limit': 100})
        self.assertEqual(code, 201)
        self.org_id = self.org['id']
        self.user_id = self.gen_id()
        code, self.employee = self.client.employee_create(
            self.org_id, {'name': 'John Smith', 'auth_user_id': self.user_id})
        self.assertEqual(code, 201)

        cloud_acc_tmp = {
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report',
            }
        }
        patch('rest_api.rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        patch('tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        patch('rest_api.rest_api_server.controllers.pool.'
              'PoolController._get_assignments_actions_by_token',
              return_value={
                  'MANAGE_RESOURCES': [
                      ['organization', self.org_id]
                  ],
                  'MANAGE_OWN_RESOURCES': [
                      ['organization', self.org_id]
                  ]
              }).start()
        cloud_acc1 = deepcopy(cloud_acc_tmp)
        cloud_acc1['name'] = 'cloud_acc1'
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        code, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.user_id)
        self.assertEqual(code, 201)

        cloud_acc2 = deepcopy(cloud_acc_tmp)
        cloud_acc2['name'] = 'cloud_acc2'
        code, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc2)
        self.assertEqual(code, 201)

        self.user2_id = self.gen_id()
        code, self.employee2 = self.client.employee_create(self.org_id, {
            'name': 'Another Guy', 'auth_user_id': self.user2_id,
        })
        self.assertEqual(code, 201)
        code, self.parent_pool = self.client.pool_get(self.org['pool_id'])

        code, self.sub_pool = self.client.pool_create(self.org_id, {
            'name': "sub", "parent_id": self.org['pool_id'], 'limit': 20})
        self.assertEqual(code, 201)

        code, self.sub_pool2 = self.client.pool_create(self.org_id, {
            'parent_id': self.sub_pool['id'], 'limit': 10, 'name': 'sub2'
        })
        self.assertEqual(code, 201)

        self._mock_auth_user(self.user_id)
        patch('rest_api.rest_api_server.handlers.v2.my_tasks.MyTasksAsyncHandler.'
              'check_cluster_secret', return_value=False).start()
        patch('rest_api.rest_api_server.controllers.assignment.AssignmentController.'
              '_authorize_action_for_pool', return_value=True).start()

    def test_get_my_tasks_no_types(self):
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

    def add_report_imports(self):
        code, scheduled = self.client.schedule_import(1)
        self.assertEqual(code, 201)
        return [x['id'] for x in scheduled['report_imports']]

    def set_active_flag(self, resource_ids):
        self.resources_collection.update_one(
            filter={
                '_id': {'$in': resource_ids}
            },
            update={'$set': {
                'last_seen': int(datetime.datetime.utcnow().timestamp() - 1),
                'active': True
            }}
        )

    def add_assigned_resource(self, owner_id=None, active=False, pool_id=None,
                              no_name=False, cloud_account_id=None,
                              is_cluster_resource=False):
        if not pool_id:
            pool_id = self.org['pool_id']
        if not owner_id:
            owner_id = self.employee['id']
        resource_dict = {
            'name': 'r1',
            'cloud_resource_id': self.gen_id(),
            'resource_type': 'r_type',
            'pool_id': pool_id,
            'employee_id': owner_id,
        }
        if no_name:
            del resource_dict['name']
        if cloud_account_id is None:
            cloud_account_id = self.cloud_acc1['id']
        if is_cluster_resource:
            resource_dict['tags'] = {'tn': 'tv'}
        code, resource1 = self.cloud_resource_create(
            cloud_account_id, resource_dict)
        self.assertEqual(code, 201)
        if active:
            self.set_active_flag([resource1['id']])
        return resource1['id']

    def add_incoming_assignment_request(self, resource_id=None):
        self._mock_auth_user(self.user2_id)
        if not resource_id:
            resource_id = self.add_assigned_resource(self.employee2['id'],
                                                     pool_id=self.sub_pool['id'])
        code, request = self.client.assignment_request_create(self.org_id, {
            'resource_id': resource_id,
            'approver_id': self.employee['id'],
        })
        self._mock_auth_user(self.user_id)
        self.assertEqual(code, 201)
        return request

    def add_outgoing_assignment_request(self, resource_id=None):
        if not resource_id:
            resource_id = self.add_assigned_resource(self.employee['id'],
                                                     pool_id=self.sub_pool2['id'])

        code, request = self.client.assignment_request_create(self.org_id, {
            'resource_id': resource_id,
            'approver_id': self.employee2['id'],
        })
        self.assertEqual(code, 201)
        return request

    def add_expense_records(self, pool_id=None, cost=1, date=None, owner_id=None):
        if not date:
            date = datetime.datetime.utcnow()
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        if not owner_id:
            owner_id = self.employee['id']
        if not pool_id:
            pool_id = self.org['pool_id']
        resource = {
            '_id': self.gen_id(),
            'cloud_account_id': self.cloud_acc1['id'],
            'cloud_resource_id': self.gen_id(),
            'pool_id': pool_id,
            'employee_id': owner_id,
            'name': 'name',
            'resource_type': 'Instance',
            'first_seen': int(date.timestamp()),
            'last_seen': int(date.timestamp())
        }
        self.resources_collection.insert_one(resource)
        self.expenses.append({
            'resource_id': resource['_id'],
            'cost': cost,
            'date': date,
            'cloud_account_id': self.cloud_acc1['id'],
            'sign': 1
        })

    def test_get_my_tasks_no_types_inc_requests_present(self):
        request1 = self.add_incoming_assignment_request()

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('incoming_assignment_requests', tasks)
        self.assertEqual(tasks['incoming_assignment_requests']['count'], 1)

        request2 = self.add_incoming_assignment_request()
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('incoming_assignment_requests', tasks)
        self.assertEqual(tasks['incoming_assignment_requests']['count'], 2)

        code, _ = self.client.assignment_request_decline(request1['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.assignment_request_accept(
            request2['id'], {'pool_id': self.sub_pool['id']})
        self.assertEqual(code, 204)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

    def test_get_my_tasks_no_types_out_requests_present(self):
        request1 = self.add_outgoing_assignment_request()

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 1)

        request2 = self.add_outgoing_assignment_request()
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 2)

        self._mock_auth_user(self.user2_id)
        code, _ = self.client.assignment_request_decline(request1['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.assignment_request_accept(
            request2['id'], {'pool_id': self.sub_pool['id']})
        self.assertEqual(code, 204)
        self._mock_auth_user(self.user_id)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

    @freeze_time("2020-04-30 17:34:00")
    def test_get_my_tasks_no_types_exceeded_pools(self):
        code, _ = self.client.pool_update(self.org['pool_id'],
                                          {'limit': 100})
        self.assertEqual(code, 200)

        pool_id = self.sub_pool['id']
        code, _ = self.client.pool_update(pool_id, {'limit': 10})
        self.assertEqual(code, 200)

        # subunit limit exceeded
        self.add_expense_records(pool_id, 11)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('exceeded_pools', tasks)
        self.assertEqual(tasks['exceeded_pools']['count'], 1)

        # subunit limit increased, so it's not shown in tasks anymore
        code, _ = self.client.pool_update(pool_id, {'limit': 40})
        self.assertEqual(code, 200)
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

        # adding more expenses to exceed both sub and unit pools
        self.add_expense_records(pool_id, 101)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('exceeded_pools', tasks)
        self.assertEqual(tasks['exceeded_pools']['count'], 2)

    @freeze_time("2020-01-15 17:34:00")
    def test_get_my_tasks_no_types_exceeded_forecasts(self):
        code, _ = self.client.pool_update(self.org['pool_id'],
                                          {'limit': 500})
        self.assertEqual(code, 200)

        pool_id = self.sub_pool['id']
        code, _ = self.client.pool_update(pool_id, {'limit': 10})
        self.assertEqual(code, 200)

        self.add_expense_records(pool_id, 9, datetime.datetime(2020, 1, 1))

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('exceeded_pool_forecasts', tasks)
        self.assertEqual(tasks['exceeded_pool_forecasts']['count'], 1)

        code, _ = self.client.pool_update(pool_id, {'limit': 300})
        self.assertEqual(code, 200)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

    @freeze_time("2020-04-15 17:34:00")
    def test_no_types_all_present(self):
        self.add_incoming_assignment_request()
        self.add_outgoing_assignment_request()
        self.add_expense_records(self.sub_pool2['id'], 5)
        self.add_expense_records(self.sub_pool['id'], 9)

        code, _ = self.client.pool_update(self.org['pool_id'],
                                          {'limit': 25})
        self.assertEqual(code, 200)
        self.add_expense_records(self.org['pool_id'], 15)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIn('incoming_assignment_requests', tasks)
        self.assertEqual(tasks['incoming_assignment_requests']['count'], 1)
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 1)
        self.assertIn('exceeded_pools', tasks)
        self.assertEqual(tasks['exceeded_pools']['count'], 1)
        self.assertIn('exceeded_pool_forecasts', tasks)
        self.assertEqual(tasks['exceeded_pool_forecasts']['count'], 2)

    def test_imports_type_no_imports(self):
        code, tasks = self.client.my_tasks_get(self.org_id,
                                               types=['report_imports'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks, {})

    def test_requests_type(self):
        # verify that tasks added when type specified
        in_request1 = self.add_incoming_assignment_request()
        out_request1 = self.add_outgoing_assignment_request()
        code, tasks = self.client.my_tasks_get(
            self.org_id, types=['incoming_assignment_requests'])
        self.assertEqual(code, 200)
        self.assertIn('incoming_assignment_requests', tasks)
        self.assertEqual(tasks['incoming_assignment_requests']['count'], 1)
        self.assertIn('tasks', tasks['incoming_assignment_requests'])
        self.assertEqual(tasks['incoming_assignment_requests']['count'],
                         len(tasks['incoming_assignment_requests']['tasks']))
        # verify that response is correct
        _, resource = self.client.cloud_resource_get(in_request1['resource_id'])
        self.assertEqual(
            tasks['incoming_assignment_requests']['tasks'][0],
            {
                'assignment_request_id': in_request1['id'],
                'resource_id': in_request1['resource_id'],
                'source_pool_id': self.sub_pool['id'],
                'requester_id': self.employee2['id'],
                'message': '',
                'resource_type': resource['resource_type'],
                'source_pool_purpose': 'budget',
                'source_pool_name': self.sub_pool['name'],
                'requester_name': self.employee2['name'],
                'resource_name': resource['name'],
                'cloud_resource_id': resource['cloud_resource_id']
            })

        # verify outgoing count
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 1)
        self.assertNotIn('tasks', tasks['outgoing_assignment_requests'])

        # verify outgoing tasks
        code, tasks = self.client.my_tasks_get(
            self.org_id, types=['outgoing_assignment_requests'])
        self.assertEqual(code, 200)
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 1)
        self.assertIn('tasks', tasks['outgoing_assignment_requests'])
        # verify outgoing response
        _, resource = self.client.cloud_resource_get(out_request1['resource_id'])
        self.assertEqual(
            tasks['outgoing_assignment_requests']['tasks'][0],
            {
                'assignment_request_id': out_request1['id'],
                'resource_id': out_request1['resource_id'],
                'source_pool_id': self.sub_pool2['id'],
                'approver_id': self.employee2['id'],
                'message': '',
                'resource_type': resource['resource_type'],
                'source_pool_purpose': 'budget',
                'source_pool_name': self.sub_pool2['name'],
                'approver_name': self.employee2['name'],
                'resource_name': resource['name'],
                'cloud_resource_id': resource['cloud_resource_id']
            })

        # replace in request with one using employee pool
        self.client.assignment_request_decline(in_request1['id'])
        in_request2 = self.add_incoming_assignment_request()

        # verify both with details
        code, tasks = self.client.my_tasks_get(
            self.org_id, types=['incoming_assignment_requests',
                                'outgoing_assignment_requests'])
        self.assertEqual(code, 200)
        self.assertIn('incoming_assignment_requests', tasks)
        self.assertIn('outgoing_assignment_requests', tasks)
        self.assertEqual(tasks['incoming_assignment_requests']['count'], 1)
        self.assertEqual(tasks['outgoing_assignment_requests']['count'], 1)
        self.assertIn('tasks', tasks['incoming_assignment_requests'])
        self.assertIn('tasks', tasks['outgoing_assignment_requests'])

        # verify request with employee source pool
        self.assertEqual(tasks['incoming_assignment_requests']['tasks'][0][
                             'source_pool_purpose'], 'budget')
        self.assertEqual(tasks['incoming_assignment_requests']['tasks'][0][
                             'source_pool_name'], self.sub_pool['name'])

    @freeze_time("2020-04-15 17:34:00")
    def test_pool_types(self):
        code, _ = self.client.pool_update(self.org['pool_id'],
                                          {'limit': 100})
        self.assertEqual(code, 200)

        pool_id = self.sub_pool['id']
        code, _ = self.client.pool_update(pool_id, {'limit': 10,
                                                    'purpose': 'team'})
        self.assertEqual(code, 200)

        self.add_expense_records(pool_id, 90)

        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'exceeded_pools', 'exceeded_pool_forecasts'])
        self.assertEqual(code, 200)
        self.assertIn('exceeded_pools', tasks)
        self.assertEqual(tasks['exceeded_pools']['count'], 1)
        self.assertIn('exceeded_pool_forecasts', tasks)
        self.assertEqual(tasks['exceeded_pool_forecasts']['count'], 1)
        self.assertIn('tasks', tasks['exceeded_pools'])
        self.assertIn('tasks', tasks['exceeded_pool_forecasts'])

        self.assertEqual(
            tasks['exceeded_pools']['tasks'][0],
            {
                'pool_id': self.sub_pool['id'],
                'pool_name': self.sub_pool['name'],
                'pool_purpose': 'team',
                'limit': 10,
                'total_expenses': 90,
                'forecast': 1530,
            })

        self.assertEqual(
            tasks['exceeded_pool_forecasts']['tasks'][0],
            {
                'pool_id': self.org['pool_id'],
                'pool_name': self.org['name'],
                'pool_purpose': 'business_unit',
                'limit': 100,
                'total_expenses': 90,
                'forecast': 1530,
            })

    def test_get_my_tasks_exceeded_pools_several_expenses(self):
        self.add_expense_records(
            self.org['pool_id'], 96, datetime.datetime(2020, 1, 5))
        self.add_expense_records(
            self.org['pool_id'], 14, datetime.datetime(2020, 1, 14))
        with freeze_time(datetime.datetime(2020, 1, 15)):
            code, tasks = self.client.my_tasks_get(self.org_id)
            self.assertEqual(code, 200)
            self.assertIn('exceeded_pools', tasks)
            self.assertEqual(tasks['exceeded_pools']['count'], 1)

            code, tasks = self.client.my_tasks_get(self.org_id, types=[
                'exceeded_pools', 'exceeded_pool_forecasts'])
            self.assertIn('exceeded_pools', tasks)
            self.assertEqual(tasks['exceeded_pools']['count'], 1)
            self.assertEqual(
                tasks['exceeded_pools']['tasks'][0]['total_expenses'], 110)
            self.assertEqual(
                tasks['exceeded_pools']['tasks'][0]['forecast'], 297)

    def _create_resource_constraint(self, resource_id, limit=40,
                                    type='total_expense_limit'):
        params = {
            'limit': limit,
            'type': type
        }
        code, constraint = self.client.resource_constraint_create(
            resource_id, params)
        return code, constraint

    def _create_pool_policy(self, pool_id, limit=50,
                            type='total_expense_limit'):
        params = {
            'limit': limit,
            'type': type
        }
        code, policy = self.client.pool_policy_create(pool_id, params)
        return code, policy

    def _add_constraint_limit_hit(
            self, resource_id, constraint_type=ConstraintTypes.TOTAL_EXPENSE_LIMIT,
            pool_id=None, constraint_limit=50, hit_value=55):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        ttl_value = hit_value if constraint_type == ConstraintTypes.TTL else None
        expense_value = hit_value if constraint_type != ConstraintTypes.TTL else None
        limit_hit = ConstraintLimitHit(
            id=str(uuid.uuid4()),
            pool_id=pool_id,
            resource_id=resource_id,
            type=constraint_type,
            constraint_limit=constraint_limit,
            ttl_value=ttl_value,
            expense_value=expense_value,
            organization_id=self.org_id,
        )
        session.add(limit_hit)
        session.commit()

    def test_get_my_tasks_constraints(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        res_2_id = self.add_assigned_resource(self.employee['id'], active=True,
                                              pool_id=self.sub_pool2['id'])
        res_3_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(self.org['pool_id'])
        self.assertEqual(code, 201)
        code, policy2 = self._create_pool_policy(
            self.org['pool_id'], type='ttl')
        self.assertEqual(code, 201)

        now = int(datetime.datetime.utcnow().timestamp())
        code, constr_1 = self._create_resource_constraint(
            res_1_id, type='ttl', limit=now + 3600)
        self.assertEqual(code, 201)
        code, constr_1_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        code, constr_2 = self._create_resource_constraint(
            res_2_id)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 2)
        self._add_constraint_limit_hit(res_3_id)
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))
        self._add_constraint_limit_hit(
            res_2_id, ConstraintTypes.TTL, constraint_limit=now, hit_value=now + 3600)
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))
        self._add_constraint_limit_hit(res_2_id, ConstraintTypes.TOTAL_EXPENSE_LIMIT)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        violated_constraint = tasks['violated_constraints']['tasks'][0]
        differ_constraints = tasks['differ_constraints']['tasks']
        self.assertEqual(len(differ_constraints), 2)
        for diff_const in differ_constraints:
            self.assertEqual(diff_const['resource_name'], 'r1')
            self.assertEqual(diff_const['policy']['pool_name'], 'organization')
            self.assertIsNotNone(diff_const['cloud_resource_id'])
            self.assertEqual(diff_const['resource_type'], 'r_type')
            self.assertEqual(diff_const['owner_id'], self.employee['id'])
            self.assertEqual(diff_const['owner_name'], self.employee['name'])
            self.assertEqual(diff_const['pool_id'], self.parent_pool['id'])
            self.assertEqual(diff_const['pool_name'], self.parent_pool['name'])
        self.assertEqual(violated_constraint['resource_name'], 'r1')
        self.assertEqual(violated_constraint['resource_id'], res_2_id)
        self.assertIsNotNone(violated_constraint['cloud_resource_id'])
        self.assertEqual(violated_constraint['resource_type'], 'r_type')
        self.assertEqual(violated_constraint['pool_id'],
                         self.sub_pool2['id'])
        self.assertEqual(violated_constraint['type'], 'total_expense_limit')
        self._add_constraint_limit_hit(
            res_1_id, ConstraintTypes.TTL,
            constraint_limit=now + 3600, hit_value=now + 3601)
        self._add_constraint_limit_hit(
            res_1_id, ConstraintTypes.TTL,
            constraint_limit=now + 3600, hit_value=now + 3601)
        self._add_constraint_limit_hit(
            res_1_id, ConstraintTypes.TOTAL_EXPENSE_LIMIT)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 3)
        for task in tasks['violated_constraints']['tasks']:
            self.assertTrue(task['resource_id'] in [res_1_id, res_2_id])

    @freeze_time("2020-04-15 17:34:00")
    def test_diff_constraints_cluster(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        self.add_assigned_resource(is_cluster_resource=True)
        cluster_id = list(self.resources_collection.find(
            {"cloud_resource_id": {"$exists": True}}))[0]['_id']
        self.set_active_flag([cluster_id])
        self.client.assignment_create(
            self.org_id,
            {'resource_id': cluster_id,
             'pool_id': self.org['pool_id'],
             'owner_id': self.employee['id']})

        code, policy = self._create_pool_policy(self.org['pool_id'])
        self.assertEqual(code, 201)

        code, constr = self._create_resource_constraint(cluster_id)
        self.assertEqual(code, 201)

        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 1)
        self._add_constraint_limit_hit(cluster_id)
        code, tasks = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 1)
        self.assertEqual(tasks['violated_constraints']['count'], 1)

        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        violated_constraints = tasks['violated_constraints']['tasks']
        differ_constraints = tasks['differ_constraints']['tasks']
        for constraints in [violated_constraints, differ_constraints]:
            for constraint in constraints:
                self.assertEqual(cluster_id, constraint['resource_id'])

    def test_diff_constraints_with_same_value(self):
        res_1_id = self.add_assigned_resource(
            self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'])
        self.assertEqual(code, 201)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 1)
        self.client.resource_constraint_update(
            constr_1['id'], {'limit': policy1['limit']})
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('differ_constraints'))

    def test_diff_constraints_removed_policy(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'])
        self.assertEqual(code, 201)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 1)
        self.client.pool_policy_delete(policy1['id'])
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('differ_constraints'))

    def test_constraints_inactive_resource(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'], type='total_expense_limit')
        self.assertEqual(code, 201)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_1_id)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        self.assertEqual(tasks['differ_constraints']['count'], 1)

        self.resources_collection.update_many(
            filter={}, update={'$unset': {'active': ''}})

        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))
        self.assertIsNone(tasks.get('differ_constraints'))

    def test_add_constraint_after_policy_hit(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'], type='total_expense_limit')
        self._add_constraint_limit_hit(
            res_1_id, pool_id=self.org['pool_id'])
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_id'],
            self.org['pool_id'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['resource_id'], res_1_id)
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['resource_name'], 'r1')
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_name'],
            self.org['name'])

        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertIsNone(tasks.get('violated_constraints'))

    def test_get_constraint_with_deleted_cloud_account(self):
        res_1_id = self.add_assigned_resource(
            self.employee['id'], active=True,
            cloud_account_id=self.cloud_acc1['id'])
        res_2_id = self.add_assigned_resource(
            self.employee['id'], active=True,
            cloud_account_id=self.cloud_acc2['id'])
        code, policy1 = self._create_pool_policy(self.org['pool_id'])
        self._add_constraint_limit_hit(
            res_1_id, pool_id=self.org['pool_id'])
        self._add_constraint_limit_hit(
            res_2_id, pool_id=self.org['pool_id'])
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(tasks['violated_constraints']['count'], 2)
        code, _ = self.client.cloud_account_delete(self.cloud_acc1['id'])
        self.assertEqual(code, 204)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(tasks['violated_constraints']['count'], 1)

    def test_remove_constraint_after_hit(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_1_id)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        code, _ = self.client.resource_constraint_delete(constr_1['id'])
        self.assertEqual(code, 204)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertIsNone(tasks.get('violated_constraints'))

    def test_remove_constraint_with_policy_after_hit(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        code, policy1 = self._create_pool_policy(self.org['pool_id'])
        self._add_constraint_limit_hit(res_1_id)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(tasks['violated_constraints']['tasks'][0]['pool_id'],
                         self.org['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        code, _ = self.client.resource_constraint_delete(constr_1['id'])
        self.assertEqual(code, 204)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertIsNone(tasks.get('violated_constraints'))
        created_at = datetime.datetime.utcnow().timestamp()
        with freeze_time(datetime.datetime.fromtimestamp(created_at + 1)):
            self._add_constraint_limit_hit(
                res_1_id, pool_id=self.org['pool_id'])
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_id'],
            self.org['pool_id'])

    def test_change_constraint_after_hit(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, constr_1 = self._create_resource_constraint(res_1_id)
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_1_id)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)

        code, resp = self.client.resource_constraint_update(
            constr_1['id'], {'limit': 200})
        self.assertEqual(code, 200)
        self.assertEqual(resp['limit'], 200)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))

    def test_constraints_another_employee(self):
        res_id = self.add_assigned_resource(
            self.employee2['id'], active=True)
        code, constr_1 = self._create_resource_constraint(res_id)
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_id)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['owner_id'],
            self.employee2['id'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['owner_name'],
            self.employee2['name'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_id'],
            self.org['pool_id'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_name'],
            self.org['name'])
        self.assertEqual(
            tasks['violated_constraints']['tasks'][0]['pool_purpose'],
            'business_unit')

    def test_constraints_another_employee_resource_no_name(self):
        res_id = self.add_assigned_resource(
            self.employee2['id'], active=True, no_name=True)
        code, constr_1 = self._create_resource_constraint(res_id)
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_id)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)

    def test_policy_another_employee(self):
        res_id = self.add_assigned_resource(
            self.employee2['id'], active=True,
            pool_id=self.sub_pool2['id'])
        code, constr_1 = self._create_pool_policy(self.org['pool_id'])
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(
            res_id, pool_id=self.org['pool_id'])
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)

    def test_constraints_only_own(self):
        patch('rest_api.rest_api_server.controllers.pool.'
              'PoolController._get_assignments_actions_by_token',
              return_value={
                  'MANAGE_RESOURCES': [
                  ],
                  'MANAGE_OWN_RESOURCES': [
                      ['organization', self.org_id]
                  ]
              }).start()
        res_id = self.add_assigned_resource(
            self.employee2['id'], active=True,
            pool_id=self.sub_pool2['id'])
        code, constr_1 = self._create_pool_policy(self.org['pool_id'])
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(
            res_id, pool_id=self.org['pool_id'])
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))

    def test_infinity_constraint(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'], type='total_expense_limit')
        self.assertEqual(code, 201)
        code, constr_1 = self._create_resource_constraint(res_1_id, limit=0)
        self.assertEqual(code, 201)
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['differ_constraints']['count'], 1)

        self.resources_collection.update_many(
            filter={}, update={'$unset': {'active': ''}})
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints', 'differ_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))
        self.assertIsNone(tasks.get('differ_constraints'))

    def test_infinity_to_noninfinity_policy(self):
        res_1_id = self.add_assigned_resource(self.employee['id'], active=True)
        code, policy1 = self._create_pool_policy(
            self.org['pool_id'], type='total_expense_limit')
        self.assertEqual(code, 201)
        self._add_constraint_limit_hit(res_1_id, pool_id=self.org['pool_id'])
        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints'])
        self.assertEqual(code, 200)
        self.assertEqual(tasks['violated_constraints']['count'], 1)

        code, resp = self.client.pool_policy_update(
            policy1['id'], {'limit': 0})
        self.assertEqual(code, 200)
        self.assertEqual(resp['limit'], 0)

        code, tasks = self.client.my_tasks_get(self.org_id, types=[
            'violated_constraints'])
        self.assertEqual(code, 200)
        self.assertIsNone(tasks.get('violated_constraints'))

    def test_cluster_type_id_in_response(self):
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': 'c_type', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        _ = self.add_assigned_resource(is_cluster_resource=True)
        cluster_resource = list(self.resources_collection.find(
            {"cloud_resource_id": {"$exists": True}}))[0]
        self.assertEqual(ct['id'], cluster_resource['cluster_type_id'])

        code, _ = self.client.assignment_create(self.org_id, {
            'resource_id': cluster_resource['_id'],
            'owner_id': self.employee['id'],
            'pool_id': self.org['pool_id']
        })
        self.assertEqual(code, 201)
        _ = self.add_outgoing_assignment_request(
            resource_id=cluster_resource['_id'])
        code, tasks = self.client.my_tasks_get(
            self.org_id, types=['outgoing_assignment_requests'])
        self.assertEqual(code, 200)
        out_requests = tasks['outgoing_assignment_requests']['tasks']
        self.assertEqual(len(out_requests), 1)
        self.assertEqual(ct['id'], out_requests[0]['cluster_type_id'])

        code, _ = self.client.assignment_create(self.org_id, {
            'resource_id': cluster_resource['_id'],
            'owner_id': self.employee2['id'],
            'pool_id': self.org['pool_id']
        })
        self.assertEqual(code, 201)
        _ = self.add_incoming_assignment_request(
            resource_id=cluster_resource['_id'])
        code, tasks = self.client.my_tasks_get(
            self.org_id, types=['incoming_assignment_requests'])
        self.assertEqual(code, 200)
        in_requests = tasks['incoming_assignment_requests']['tasks']
        self.assertEqual(len(in_requests), 1)
        self.assertEqual(ct['id'], in_requests[0]['cluster_type_id'])

    def test_organization_constraints(self):
        self.create_org_limit_hit(self.org_id, self.org['pool_id'])
        code, resp = self.client.my_tasks_get(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp['violated_organization_constraints']['count'], 1)

    def test_organization_constraints_details(self):
        constr = self.create_org_constraint(self.org_id, self.org['pool_id'])
        hit = self.create_org_limit_hit(self.org_id, self.org['pool_id'],
                                        constraint_id=constr['id'])
        code, resp = self.client.my_tasks_get(
            self.org_id, type='violated_organization_constraints')
        self.assertEqual(code, 200)
        self.assertEqual(resp['violated_organization_constraints']['count'], 1)
        for f in ['name', 'type', 'last_run', 'definition']:
            hit[f] = constr[f]
        hit['filters'] = {'pool': [{'id': self.org['pool_id'],
                                    'purpose': 'business_unit',
                                    'name': self.org['name']}]}
        self.assertDictEqual(
            resp['violated_organization_constraints']['tasks'][0], hit)
