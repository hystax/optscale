from datetime import datetime
from freezegun import freeze_time
from unittest.mock import patch

from rest_api.rest_api_server.models.enums import AssignmentRequestTypes as ReqTypes
from rest_api.rest_api_server.tests.unittests.test_assignment_api import (
    TestAssignmentApiBase, AUTHORIZE_ACTION_METHOD)


class TestAssignmentApiBulk(TestAssignmentApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.root_assigned_resources = []
        self.root_assigned_resource_ids = []
        for _ in range(4):
            resource = self._create_resource(pool_id=self.org_pool_id,
                                             employee_id=self.employee['id'])
            self.root_assigned_resources.append(resource)
            self.root_assigned_resource_ids.append(resource['id'])

    def _add_expense(self, resource, date, cost=100):
        self.expenses.append({
            'resource_id': resource['id'],
            'cost': cost,
            'date': date,
            'cloud_account_id': resource['cloud_account_id'],
            'sign': 1
        })

    @staticmethod
    def _prepare_assign_bulk_body(resource_ids, pool_id, owner_id=None):
        return {'resource_ids': resource_ids,
                'pool_id': pool_id,
                'owner_id': owner_id}

    @staticmethod
    def _configure_auth_mocks(check_pool, check_owner, check_resources=None):
        responses_for_resources = check_resources if check_resources else []
        return [check_pool, check_owner] + responses_for_resources

    def _create_bulk_assignments(self, ids, owner_id=None, pool_id=None):
        if pool_id is None:
            pool_id = self.org_pool_id
        if owner_id is None:
            owner_id = self.employee['id']
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=ids,
            pool_id=pool_id,
            owner_id=owner_id)
        code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['succeeded']), len(ids))
        self.assertEqual(set(resp['succeeded']), set(ids))
        self.assertEqual(len(resp['failed']), 0)

    def test_params_create_assignment_bulk(self):
        """
        Test required parameters for bulk creation assignment.
        Steps:
           - 1. Verify bulk requests without param:
             - resource_ids
             - pool_id
           - 2. Verify requests with param, but entity doesn't exist:
             - pool_id
             - owner_id

        """
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            pool_id=self.org_pool_id)
        self._test_params(
            self.client.assignment_bulk, bulk_body, self.org_id,
            required_parameters=['resource_ids', 'pool_id'],
            entities_should_exist=['pool_id', 'owner_id']
        )

    def test_employee_not_in_org_bulk(self):
        """
        Verify bulk(assignment) if current employee not a member in provided org
        Steps:
           - 1. Make valid bulk request from user without employee in org.
           - 2. Verify response code is 403 Forbidden.
           - 3. Verify localized code. Should be E0378

        """

        user_id = self.gen_id()
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            pool_id=self.org_pool_id)
        with self.switch_user(user_id):
            code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 403)
        self.verify_error_code(resp, 'OE0378')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk(self, p_authorize):
        """
        Basic bulk assignment creation flow.
        Steps:
           - 1. Create 5 root assigned resources (including cluster dependent).
           - 2. Request bulk assignment API without owner, with valid pool
             for created resources.
           - 3. Response code should be 201.
           - 4. Verify no failed assignments.
           - 5. Verify 5 succeeded assignments.
           - 6. Request assignments for current user. It should be 5.
             - Verify count of assignments is 5.
             - Verify resources in assignments. It should be 5 created resources
               in step 1.
             - Verify pool_id in resource assignments is correct

        """
        p_authorize.return_value = True
        root_assigned_resource_ids = self.root_assigned_resource_ids
        clustered_resource = self._create_resource(tags={'tn': 'tv'})
        root_assigned_resource_ids.append(clustered_resource['cluster_id'])
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 5)
        self._create_bulk_assignments(root_assigned_resource_ids,
                                      pool_id=self.sub_pools[0]['id'])
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 5)
        for assignment in assignments:
            self.assertTrue(
                assignment['resource_id'] in root_assigned_resource_ids)
            self.assertEqual(assignment['pool_id'], self.sub_pools[0]['id'])

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_idempotency(self, p_authorize):
        """
        Check idempotency of assignment bulk creation.
        Steps:
           - 1. Create 4 root assigned resources.
           - 2. Assign two resources to employee2.
           - 3. Assign other two resources to current user.
           - 4. Verify no failed assignments.
           - 5. Verify 2 assignments for current user.
           - 6. Repeat step 3 for all 4 resources.
           - 7. Verify count of assignments for current user. It should be 4.
             Only two new assignments.
           - 8. Repeat step 6
           - 9. Verify count of assignments for current user. It should be 4.
             No new assignments.

        """
        now = int(datetime.utcnow().timestamp())
        p_authorize.return_value = True
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 0)
        target_resource_ids = self.root_assigned_resource_ids[:2]
        with freeze_time(datetime.fromtimestamp(now + 1)):
            self._create_bulk_assignments(target_resource_ids,
                                          owner_id=self.employee2['id'])
        target_resource_ids2 = self.root_assigned_resource_ids[2:]
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 2)
        with freeze_time(datetime.fromtimestamp(now + 2)):
            self._create_bulk_assignments(target_resource_ids2)
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 2)
        with freeze_time(datetime.fromtimestamp(now + 3)):
            self._create_bulk_assignments(self.root_assigned_resource_ids)
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        with freeze_time(datetime.fromtimestamp(now + 4)):
            self._create_bulk_assignments(self.root_assigned_resource_ids)
        self.assertEqual(len(assignments), 4)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_with_owner(self, p_authorize):
        """
        Basic bulk assignment creation flow.
        Steps:
           - 1. Create 4 root assigned resources.
           - 2. Request bulk assignment API with valid owner not current user,
             pool and created resources.
           - 3. Response code should be 201.
           - 4. Verify no failed assignments.
           - 5. Verify 4 succeeded assignments.
           - 6. Request assignments for target user. It should be 4.
             - Verify count of assignments is 4.
             - Verify resources in assignments. It should be 4 created resources
               in step 1.

        """
        p_authorize.return_value = True
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 0)
        self._create_bulk_assignments(self.root_assigned_resource_ids,
                                      owner_id=self.employee2['id'])
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        for assignment in assignments:
            self.assertTrue(
                assignment['resource_id'] in self.root_assigned_resource_ids)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_deleted_unknown_resources(self,
                                                              p_authorize):
        """
        Basic bulk assignment creation flow.
        Steps:
           - 1. Create 4 root assigned resources.
           - 2. Delete all these resources.
           - 3. Request bulk assignment API with valid owner,
             pool and deleted resources plus 2 unknown resources.
           - 4. Response code should be 201.
           - 5. Verify 4 failed assignments.
           - 6. Verify 0 succeeded assignments.
           - 7. Request assignments for current user. It should be 0.
        """
        p_authorize.return_value = True
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        for resource in self.root_assigned_resources:
            self.client.cloud_resource_delete(resource['id'])
        target_resource_ids = [self.root_assigned_resource_ids, 4 * [self.gen_id()]]
        for res_ids in target_resource_ids:
            bulk_body = self._prepare_assign_bulk_body(
                resource_ids=res_ids,
                pool_id=self.org_pool_id,
                owner_id=self.employee2['id'])
            code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
            self.assertEqual(code, 201)
            self.assertEqual(len(resp['succeeded']), 0)
            self.assertEqual(len(resp['failed']), 4)
            for item in resp['failed']:
                self.assertEqual(item['code'], 'OE0002')
            self.assertEqual(set([res['id'] for res in resp['failed']]),
                             set(res_ids))
            with self.switch_user(self.user2_id):
                assignments = self._get_assignments()
            self.assertEqual(len(assignments), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_subresources(self, p_authorize):
        """
        Basic bulk assignment creation flow.
        Steps:
           - 1. Create cluster dependent resource.
           - 2. Request bulk assignment API with valid owner,
             pool and cluster dependent resource.
           - 3. Response code should be 201.
           - 4. Verify 1 failed assignment.
           - 5. Verify 0 succeeded assignments.
           - 6. Request assignments for current user. It should be 0.

        """
        p_authorize.return_value = True
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 0)
        clustered_resource = self._create_resource(tags={'tn': 'tv'})
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=[clustered_resource['id']],
            pool_id=self.org_pool_id)
        code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['succeeded']), 0)
        self.assertEqual(len(resp['failed']), 1)
        for item in resp['failed']:
            self.assertEqual(item['code'], 'OE0464')
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_manageable_restricted(self, p_authorize):
        """
        Basic bulk assignment creation flow for resources where owner is another
        employee.
        Steps:
           - 1. Create 4 resources for employee2.
           - 2. Request bulk assignment API with valid owner,
             pool and created resources.
           - 3. Configure auth mock in such way that first two authorize are
             success, the next two requests are fail. So two manageable, and two
             restricted resources.
           - 4. Response code should be 201.
           - 5. Verify 2 failed assignments.
             - localized code should be E0381.
           - 6. Verify 2 succeeded assignments.
           - 7. Request assignments for current user. It should be 2.

        """
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
        self.assertEqual(len(assignments), 0)
        resources = []
        for i in range(4):
            code, resp = self.client.pool_create(
                self.org_id,
                {'name': "pool_%d" % i,
                 'parent_id': self.org_pool_id})
            self.assertEqual(code, 201)
            resources.append(self._create_resource(
                employee_id=self.employee2['id'],
                pool_id=resp['id']))
        resource_ids = [res['id'] for res in resources]
        p_authorize.side_effect = self._configure_auth_mocks(
            check_pool=True, check_owner=True,
            check_resources=[True, True, False, False])
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=resource_ids,
            pool_id=self.org_pool_id)
        code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['succeeded']), 2)
        self.assertEqual(len(resp['failed']), 2)
        for item in resp['failed']:
            self.assertEqual(item['code'], 'OE0381')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignments_bulk_no_permissions_pool(self, p_authorize):
        """
        Test creation bulk assignments for resources without permissions on
        target pool.
        Steps:
           - 1. Verify count of assignments for current user. Should be 0.
           - 2. Try to create bulk assignment for resources if current
             user doesn't have permission on the target pool.
           - 3. Verify response code is 403 Forbidden.
           - 4. Verify no new assignments for target user.

        """
        with self.switch_user(self.user2_id):
            requests = self._get_assignments()
            self.assertEqual(len(requests), 0)
            new_request = self._prepare_assign_bulk_body(
                resource_ids=self.root_assigned_resource_ids,
                pool_id=self.org_pool_id)
            p_authorize.side_effect = self._configure_auth_mocks(
                check_pool=False, check_owner=True)
            code, resp = self.client.assignment_bulk(self.org_id,
                                                     new_request)
            self.assertEqual(code, 403)
            self.verify_error_code(resp, 'OE0380')
            assignments = self._get_assignments()
            self.assertEqual(len(assignments), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignments_no_permissions_owner(self,
                                                     p_authorize):
        """
        Test creation bulk assignment for resources if target owner doesn't have
        permissions in target pool.
        Steps:
           - 1. Verify count of assignments for current user. Should be 0.
           - 2. Try to create bulk assignment for resource if target owner
             doesn't have permission on the target pool.
           - 3. Verify response code is 403 Forbidden.
           - 4. Verify no new assignments for target user.

        """
        with self.switch_user(self.user2_id):
            requests = self._get_assignments()
            self.assertEqual(len(requests), 0)
            new_request = self._prepare_assign_bulk_body(
                resource_ids=self.root_assigned_resource_ids,
                pool_id=self.org_pool_id)
            p_authorize.side_effect = self._configure_auth_mocks(
                check_pool=True, check_owner=False)
            code, resp = self.client.assignment_bulk(self.org_id,
                                                     new_request)
            self.assertEqual(code, 403)
            self.verify_error_code(resp, 'OE0379')
            assignments = self._get_assignments()
            self.assertEqual(len(assignments), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_expenses_after_create_assignment_bulk(self, p_authorize):
        """
        Test expenses are updated after bulk operation.
        Steps:
           - 1. Create additional pool2
           - 1. Create 4 root assigned resources, 1 assigned and 1 cluster
           dependent resources.
           - 2. Create 6 expenses one per resource.
           - 3. Get all expenses.
             - Verify total count should be 6 (6 created).
           - 4. Create bulk assignment for all resources for organization pool
             and without an owner.
           - 5. Verify no failed assignments in response.
           - 6. Verify 6 succeeded assignments in response.
           - 7. Get all expenses.
             - Verify total count should be the same as before bulk assignment.
        """
        day_in_past = datetime(2020, 1, 14)
        code, resp = self.client.pool_create(
            self.org_id,
            {'name': "sub-pool",
             'parent_id': self.org_pool_id})
        self.assertEqual(code, 201)
        pool2_id = resp['id']
        extra_resource = self._create_resource(employee_id=self.employee2['id'],
                                               pool_id=pool2_id)
        clustered_resource = self._create_resource(tags={'tn': 'tv'})
        all_resources = self.root_assigned_resources + [
            extra_resource, clustered_resource]
        all_res_ids = self.root_assigned_resource_ids + [
            extra_resource['id'], clustered_resource['cluster_id']]
        for resource in all_resources:
            self._add_expense(resource, day_in_past)
        code, resp = self.client.clean_expenses_get(
            self.org_id, int(day_in_past.timestamp()),
            int(datetime.utcnow().timestamp()))
        self.assertEqual(code, 200)
        expenses = resp['clean_expenses']
        self.assertEqual(len(expenses), len(all_resources))
        p_authorize.return_value = True
        assignments = self._get_assignments()
        # 5 resources assigned to root pool owner, 1 resource assigned to pool2
        self.assertEqual(len(assignments), 5)
        self._create_bulk_assignments(all_res_ids)
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), len(all_resources))
        for assignment in assignments:
            self.assertTrue(
                assignment['resource_id'] in all_res_ids)
        code, resp = self.client.clean_expenses_get(
            self.org_id, int(day_in_past.timestamp()),
            int(datetime.utcnow().timestamp()))
        expenses = resp['clean_expenses']
        self.assertEqual(len(expenses), len(all_resources))

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_history_rewrite_failed_not_rewritten(self, p_authorize):
        """
        Test that failed assignment doesn't rewrite history
        Steps:
           - 1. Assign 4 root assigned resources to employee2 into different
             pools.
           - 2. Request bulk assignment API with valid owner,
           - 3. Configure auth mock in such way that first two authorize are
             success, the next 3 requests are fail. So two resources was
             assigned, another 3 failed.
           - 4. Response code should be 201.
           - 5. Verify 3 failed assignments.
             - localized code should be E0381.
           - 6. Verify 1 succeeded assignments.
           - 7. Check current assignments for employee2. Should be 3.
           - 8. Check current assignments for employee1. Should be 1.

        """
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        pool_ids = []
        for i in range(4):
            code, resp = self.client.pool_create(
                self.org_id,
                {'name': "sub_pool_%d" % i,
                 'parent_id': self.org_pool_id})
            self.assertEqual(code, 201)
            code, resp1 = self.client.pool_create(
                self.org_id,
                {'name': "sub_pool1_%d" % i,
                 'parent_id': self.org_pool_id})
            self.assertEqual(code, 201)
            self._create_bulk_assignments([self.root_assigned_resource_ids[i]],
                                          owner_id=self.employee2['id'],
                                          pool_id=resp['id'])
            self._create_bulk_assignments([self.root_assigned_resource_ids[i]],
                                          owner_id=self.employee2['id'],
                                          pool_id=resp1['id'])
            pool_ids.append(resp1['id'])
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
            self.assertEqual(len(assignments), 4)
            for assignment in assignments:
                self.assertTrue(assignment['pool_id'] in pool_ids)
        p_authorize.side_effect = self._configure_auth_mocks(
            check_pool=True, check_owner=True,
            check_resources=[True, False, False, False])
        bulk_body = self._prepare_assign_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            pool_id=self.org_pool_id)
        code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['succeeded']), 1)
        self.assertEqual(len(resp['failed']), 3)
        for item in resp['failed']:
            self.assertEqual(item['code'], 'OE0381')
        with self.switch_user(self.user2_id):
            assignments = self._get_assignments()
            self.assertEqual(len(assignments), 3)
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 1)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_requests_invalidation(self, p_authorize):
        """
        Test invalidation existing assignment request for resources in case of
        new assignment via bulk assignments
        Steps:
           - 1. Create 4 resources for org pool.
             - 2 should be assigned to current user
             - 2 should be assigned to another user
           - 2. Create assignment requests for all created resources to current
             user in org pool.
           - 3. Get all assignments for current user. Should be 2.
           - 4. Verify count of incoming assignment requests for current user.
             Should be 4.
           - 5. Do bulk direct assignment into org pool, to current user.
             - in that case 2 assignments will be new, and 2 other are
               idempotent.
           - 6. Verify assignments for current user. Should be 4.
             - existing assignments should include 2 assignments from step 3
           - 7. Verify count of incoming assignment requests. Should be 0.

        """
        p_authorize.return_value = True
        resources_for_empl_ids = self.root_assigned_resource_ids[:2]
        resources_for_empl2_ids = self.root_assigned_resource_ids[2:]
        self._create_bulk_assignments(resources_for_empl_ids)
        self._create_bulk_assignments(resources_for_empl2_ids,
                                      owner_id=self.employee2['id'])
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 2)
        empl_ids_before = {assignment['owner_id'] for assignment in assignments}

        bulk_body = TestAssignmentRequestApiBulk._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee2['id'])
        code, resp = self.client.assignment_request_bulk(self.org_id,
                                                         bulk_body)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['succeeded']), 4)
        self.assertEqual(len(resp['failed']), 0)

        with self.switch_user(self.user2_id):
            requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 4)

        self._create_bulk_assignments(self.root_assigned_resource_ids)

        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        empl_ids_after = {assignment['owner_id'] for assignment in assignments}
        self.assertTrue(empl_ids_before <= empl_ids_after)

        requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_assignment_bulk_events(self, p_authorize):
        p_authorize.return_value = True
        user_info = {
            'display_name': 'John Smth', 'id': self._user_id,
            'email': 'example@hystax.com'
        }
        self.p_get_user_info.return_value = user_info
        p_publish_activity = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()

        self._create_bulk_assignments(self.root_assigned_resource_ids)
        assignments = self._get_assignments()
        self.assertEqual(len(assignments), 4)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, self.organization['pool_id'], 'pool',
            'resource_assigned', {
                'total_count': len(assignments),
                'employee_name': self.employee['name'],
                'employee_id': self.employee['id'],
                'object_name': self.organization['name']
            })
        p_publish_activity.assert_called_once_with(*activity_param_tuples,
                                                   add_token=True)


class TestAssignmentRequestApiBulk(TestAssignmentApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.root_assigned_resources = []
        self.root_assigned_resource_ids = []
        for _ in range(4):
            resource = self._create_resource()
            self.root_assigned_resources.append(resource)
            self.root_assigned_resource_ids.append(resource['id'])
        self.employee_resources = []
        self.employee_resource_ids = []
        for _ in range(2):
            resource = self._create_resource(employee_id=self.employee['id'],
                                             pool_id=self.org_pool_id)
            self.employee_resources.append(resource)
            self.employee_resource_ids.append(resource['id'])
        self.employee2_resources = []
        self.employee2_resource_ids = []
        for _ in range(2):
            resource = self._create_resource(employee_id=self.employee2['id'],
                                             pool_id=self.org_pool_id)
            self.employee2_resources.append(resource)
            self.employee2_resource_ids.append(resource['id'])

    @staticmethod
    def _prepare_assign_req_bulk_body(resource_ids, approver_id, message=None):
        return {'resource_ids': resource_ids,
                'approver_id': approver_id,
                'message': message}

    def test_params_create_assignment_requests_bulk(self):
        """
        Test required parameters for bulk creation assignment requests.
        Steps:
           - 1. Verify bulk requests without param:
             - resource_ids
             - approver_id
           - 2. Verify requests with param, but entity doesn't exist:
             - approver_id

        """
        bulk_body = self._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee2['id'])
        self._test_params(
            self.client.assignment_request_bulk, bulk_body, self.org_id,
            required_parameters=['resource_ids', 'approver_id'],
            entities_should_exist=['approver_id']
        )

    def test_employee_not_in_org_bulk(self):
        """
        Verify bulk(assignment_requests) if current employee not a member in
        provided org
        Steps:
           - 1. Make valid bulk assignment request from user without
             employee in org.
           - 2. Verify response code is 403 Forbidden.
           - 3. Verify localized code. Should be E0378

        """
        user_id = self.gen_id()
        bulk_body = self._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee2['id'])
        with self.switch_user(user_id):
            code, resp = self.client.assignment_request_bulk(self.org_id,
                                                             bulk_body)
            self.assertEqual(code, 403)
            self.verify_error_code(resp, 'OE0378')

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_assignment_req_bulk_deleted_unknown_resources(self, p_authorize):
        """
        Test create assignment request via bulk API with deleted/unknown
        resources
        Steps:
           - 1. Create 4 root_assigned resources.
           - 2. Delete all these resources.
           - 3. Request bulk assignment requests API with valid approver and
             deleted resources.
           - 4. Response code should be 200.
           - 5. Verify 4 failed assignments.
           - 6. Verify 0 succeeded assignments.
           - 7. Verify outgoing assignments for current user. It should be 0.
           - 8. Verify incoming assignments for target user. It should be 0.
           - 9. Repeat steps 3-7 with 4 unknown resources.

        """
        p_authorize.return_value = True
        requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 0)
        for resource in self.root_assigned_resources:
            self.client.cloud_resource_delete(resource['id'])
        target_resource_ids = [self.root_assigned_resource_ids, 4 * [self.gen_id()]]
        for res_ids in target_resource_ids:
            bulk_body = self._prepare_assign_req_bulk_body(
                resource_ids=res_ids,
                approver_id=self.employee2['id'])
            code, resp = self.client.assignment_request_bulk(self.org_id,
                                                             bulk_body)
            self.assertEqual(code, 200)
            self.assertEqual(len(resp['succeeded']), 0)
            self.assertEqual(len(resp['failed']), 4)
            for item in resp['failed']:
                self.assertEqual(item['code'], 'OE0002')
            self.assertEqual(set([res['id'] for res in resp['failed']]),
                             set(res_ids))
            requests = self._get_outgoing_assignment_requests()
            self.assertEqual(len(requests), 0)
            with self.switch_user(self.user2_id):
                requests = self._get_incoming_assignment_requests()
                self.assertEqual(len(requests), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_assignment_req_bulk_manageable_restricted(self, p_authorize):
        """
        Basic bulk assignment requests creation flow for resources where owner
        is another employee.
        Steps:
           - 1. Create 4 resources for employee2.
           - 2. Request bulk assignment requests API with valid approver
             and created resources.
           - 3. Configure auth mock in such way that first two authorize are
             success, the next two requests are fail. So two manageable, and two
             restricted resources.
           - 4. Response code should be 200.
           - 5. Verify 2 failed assignments.
             - localized code should be E0381.
           - 6. Verify 2 succeeded assignments.
           - 7. Verify outgoing assignments for current user. It should be 2.
           - 8. Verify incoming assignments for target user. It should be 2.

        """
        requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 0)
        resources = []
        for i in range(5):
            code, resp = self.client.pool_create(
                self.org_id,
                {'name': "sub_pool_%d" % i,
                 'parent_id': self.org_pool_id})
            self.assertEqual(code, 201)
            resources.append(self._create_resource(
                employee_id=self.employee2['id'],
                pool_id=resp['id'], tags=None if i < 4 else {'tn': 'tv'}))
            if i == 4:
                body = self._prepare_assign_body(
                    resource_id=resources[4]['cluster_id'],
                    pool_id=resp['id'],
                    owner_id=self.employee2['id'])
                self.client.assignment_create(self.org_id, body)
        resource_ids = [res.get('cluster_id', res['id']) for res in resources]
        p_authorize.side_effect = [True, True, False, False, True]
        bulk_body = self._prepare_assign_req_bulk_body(
            resource_ids=resource_ids,
            approver_id=self.employee2['id'])
        code, resp = self.client.assignment_request_bulk(self.org_id,
                                                         bulk_body)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['succeeded']), 3)
        self.assertEqual(len(resp['failed']), 2)
        for item in resp['failed']:
            self.assertEqual(item['code'], 'OE0381')
        requests = self._get_outgoing_assignment_requests()
        self.assertEqual(len(requests), 3)
        with self.switch_user(self.user2_id):
            requests = self._get_incoming_assignment_requests()
            self.assertEqual(len(requests), 3)

    def test_assignment_req_bulk_employee_in_diff_org(self):
        """
        Test bulk assignment requests creation, if the target user in diff org
        Steps:
           - 1. Crate another organization.
           - 2. Create an employee in this org. Empl2.
           - 3. Request bulk assignment requests API for root assigned resources,
             with created employee as approver.
           - 5. Verify error code. Should be
           - 7. Verify count of outgoing assignment requests for curr user is 0.
           - 7. Verify count of incoming assignment requests for Empl2 is 0.

        """
        code, org2_bu = self.client.organization_create({'name': "org2"})
        self.assertEqual(code, 201)
        org2_bu_id = org2_bu['id']
        new_user_id = self.gen_id()
        empl2 = self._create_employee(new_user_id, org2_bu_id)
        requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 0)
        bulk_body = self._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=empl2['id'])
        code, resp = self.client.assignment_request_bulk(self.org_id,
                                                         bulk_body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0005')
        requests = self._get_outgoing_assignment_requests()
        self.assertEqual(len(requests), 0)
        with self.switch_user(new_user_id):
            code, requests = self.client.assignment_request_list(
                organization_id=org2_bu_id, req_type=ReqTypes.INCOMING.value)
            self.assertEqual(code, 200)
            count = requests['assignment_requests'][ReqTypes.INCOMING.value]
            self.assertEqual(len(count), 0)

    @patch(AUTHORIZE_ACTION_METHOD)
    def test_create_assignment_bulk_requests_invalidation(self, p_authorize):
        """
        Test invalidation existing assignment request for resources in case of
        new assignment via bulk assignments
        Steps:
           - 1. Create 4 resources for org pool and current user.
           - 2. Create assignment requests for all created resources to current
             user in org pool.
           - 3. Verify count of incoming assignment requests for current user.
             Should be 4.
           - 4. Do bulk creation assignment request into org pool, to current
             user.
           - 5. Verify count of incoming assignment requests. Should be 4.
           - 6. Verify that all assignment requests are new.

        """
        p_authorize.return_value = True
        bulk_body = TestAssignmentApiBulk._prepare_assign_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            pool_id=self.org_pool_id)
        code, resp = self.client.assignment_bulk(self.org_id, bulk_body)
        self.assertEqual(code, 201)
        self.assertEqual(len(resp['succeeded']), 4)

        bulk_body = TestAssignmentRequestApiBulk._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee2['id'])
        code, resp = self.client.assignment_request_bulk(self.org_id,
                                                         bulk_body)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['succeeded']), 4)
        self.assertEqual(len(resp['failed']), 0)

        with self.switch_user(self.user2_id):
            requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 4)
        requests_ids_before = {req['id'] for req in requests}

        bulk_body = TestAssignmentRequestApiBulk._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee2['id'])
        code, resp = self.client.assignment_request_bulk(self.org_id,
                                                         bulk_body)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['succeeded']), 4)
        self.assertEqual(len(resp['failed']), 0)

        with self.switch_user(self.user2_id):
            requests = self._get_incoming_assignment_requests()
        self.assertEqual(len(requests), 4)
        requests_ids_after = {req['id'] for req in requests}
        for req_id in requests_ids_after:
            self.assertTrue(req_id not in requests_ids_before)

    def test_create_assignment_request_bulk_for_the_same_user(self):
        bulk_body = TestAssignmentRequestApiBulk._prepare_assign_req_bulk_body(
            resource_ids=self.root_assigned_resource_ids,
            approver_id=self.employee['id'])
        code, response = self.client.assignment_request_bulk(self.org_id,
                                                             bulk_body)
        self.assertEqual(code, 403)
        self.verify_error_code(response, 'OE0424')
