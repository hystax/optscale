from unittest.mock import patch
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestAvailablePoolsApi(TestApiBase):
    GET_ASSIGNMENTS_METHOD = (
        'rest_api_server.controllers.pool'
        '.PoolController._get_assignments_actions_by_token')

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "root"})
        self.org_id = self.org['id']
        self.organization_name_id_map = {}
        self.total = 1
        self.user_id = self.gen_id()
        self.user2_id = self.gen_id()
        self.employee = self._create_employee(self.user_id, self.org_id)
        self.employee2 = self._create_employee(self.user2_id, self.org_id)

        self.organization_map = {'name': self.org['name'],
                                 'id': self.org['pool_id'],
                                 'parent_id': None,
                                 'children': [
                                     {
                                         'name': 'pool1',
                                         'children': [
                                             {
                                                 'name': 'pool1.1',
                                                 'default_owner_id':
                                                     self.employee['id'],
                                                 'children': [],
                                             },
                                             {
                                                 'default_owner_id':
                                                     self.employee2['id'],
                                                 'name': 'pool1.2',
                                                 'children': []
                                             },
                                         ]
                                     },
                                     {
                                         'name': 'pool2',
                                         'children': [
                                             {
                                                 'name': 'pool2.1',
                                                 'children': [
                                                     {
                                                         'name': 'pool2.1.1',
                                                         'children': []
                                                     },
                                                     {
                                                         'name': 'pool2.1.2',
                                                         'children': []
                                                     },
                                                 ]
                                             },
                                             {
                                                 'name': 'pool2.2',
                                                 'children': []
                                             },
                                         ]
                                     },
                                 ]}
        self._create_children_pools(self.organization_map)
        self._mock_auth_user(self.user_id)

    def _create_pool(self, name, parent_id=None, default_owner_id=None):
        code, resp = self.client.pool_create(self.org_id, {
            'name': name,
            'parent_id': parent_id,
            'default_owner_id': default_owner_id
        })
        self.assertEqual(code, 201)
        return resp

    def _create_children_pools(self, parent):
        for child in parent['children']:
            pool = self._create_pool(
                child['name'], parent_id=parent['id'],
                default_owner_id=child.get('default_owner_id'))
            self.total += 1
            self.organization_name_id_map[child['name']] = pool
            child['id'] = pool['id']
            child['parent_id'] = parent['id']
            self._create_children_pools(child)

    def _create_employee(self, user_id, organization_id):
        valid_employee = {
            'name': 'TestUser_%s' % self.gen_id()[:8],
            'auth_user_id': user_id,
        }
        code, employee = self.client.employee_create(organization_id,
                                                     valid_employee)
        self.assertEqual(code, 201)
        return employee

    def _get_available_pools(self, permissions=None, condition=None):
        code, resp = self.client.pools_get(
            self.org_id, permission=permissions, condition=condition)
        self.assertEqual(code, 200)
        return resp['pools']

    def _configure_assignments_response(self, assignment_config):
        resp = {}
        for permission, resource_ids in assignment_config.items():
            if permission not in resp:
                resp[permission] = []
            for resource_id in resource_ids:
                type_name = 'organization' if resource_id == self.org_id else 'pool'
                resp[permission].append([type_name, resource_id])
        return resp

    def _set_manage_resources_config(self, manage_resource_ids=None,
                                     manage_own_resource_ids=None):
        if manage_resource_ids is None:
            manage_resource_ids = []
        if manage_own_resource_ids is None:
            manage_own_resource_ids = []
        assignment_config = {
            'MANAGE_RESOURCES': manage_resource_ids,
            'MANAGE_OWN_RESOURCES': manage_own_resource_ids,
        }
        return self._configure_assignments_response(assignment_config)

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_available_pools_manager(self, p_assignments):
        """
        Basic get available pools flow. Manager permissions.
        Steps:
           - 1. Configure manager permissions for organization bu.
           - 2. Get available pools
           - 3. Check count of available pools. Should be equal total count of
             created BUs
           - 4. Configure manager permissions for bu in the middle of tree.
           - 5. Verify count of available pools.
           - 6. Configure manager permissions for terminal bu without subunits.
           - 7. Check count of available pools. Should be 1.

        """
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), self.total)
        target_bu_name = 'pool2'
        target_bu_id = self.organization_name_id_map[target_bu_name]['id']
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[target_bu_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), 5)
        for pool in pools:
            self.assertTrue(pool['name'].startswith(target_bu_name))
        target_bu_name = 'pool2.1.1'
        target_bu_id = self.organization_name_id_map[target_bu_name]['id']
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[target_bu_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), 1)
        for pool in pools:
            self.assertTrue(pool['name'].startswith(target_bu_name))

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_available_pools_policies(self, p_assignments):
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), self.total)
        bp = {
            'limit': 150,
            'type': 'ttl'
        }
        for pool in pools:
            self.assertTrue(isinstance(pool.get('policies'), list))
            self.client.pool_policy_create(
                pool['id'], bp)
        pools = self._get_available_pools()
        self.assertEqual(len(pools), self.total)
        for pool in pools:
            self.assertEqual(len(pool.get('policies', [])), 1)
            for policy in pool.get('policies', []):
                self.assertEqual(pool['id'], policy['pool_id'])
                for k in bp.keys():
                    self.assertEqual(bp[k], policy[k])

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_available_pools_engineer(self, p_assignments):
        """
        Basic get available pools flow. Engineer permissions.
        Steps:
           - 1. Configure engineer permissions for organization bu.
           - 2. Get available pools
           - 3. Check count of available pools. Should be equal total count of
             created BUs
           - 4. Configure engineer permissions for bu in the middle of tree.
           - 5. Verify count of available pools.
           - 6. Configure engineer permissions for terminal bu without subunits.
           - 7. Check count of available pools. Should be 1.

        """
        p_assignments.return_value = self._set_manage_resources_config(
            manage_own_resource_ids=[self.org_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), self.total)
        target_bu_name = 'pool2'
        target_bu_id = self.organization_name_id_map[target_bu_name]['id']
        p_assignments.return_value = self._set_manage_resources_config(
            manage_own_resource_ids=[target_bu_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), 5)
        for pool in pools:
            self.assertTrue(pool['name'].startswith(target_bu_name))
        target_bu_name = 'pool2.1.1'
        target_bu_id = self.organization_name_id_map[target_bu_name]['id']
        p_assignments.return_value = self._set_manage_resources_config(
            manage_own_resource_ids=[target_bu_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), 1)
        for pool in pools:
            self.assertTrue(pool['name'].startswith(target_bu_name))

    def test_get_available_pools_organization_not_found(self):
        """
        Check error code if provide organization that doesn't exist.
        Steps:
           - 1. Request available pools with random organization bu id.
           - 2. Verify 404 code. Localized code is E0002.

        """
        code, resp = self.client.pools_get(self.gen_id())
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_invalid_permission(self, p_assignments):
        p_assignments.return_value = self._configure_assignments_response(
            {'INVALID': []})
        pools = self._get_available_pools(permissions=['INVALID'])
        self.assertEqual(len(pools), 0)

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_invalid_condition(self, p_assignments):
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org_id],
            manage_own_resource_ids=[self.org_id])
        code, resp = self.client.pools_get(self.org_id, condition='ll')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0217')

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_and_condition(self, p_assignments):
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org['pool_id']],
            manage_own_resource_ids=[self.org['pool_id']])
        pools = self._get_available_pools(condition='and')
        self.assertEqual(len(pools), 9)

        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org['pool_id']])
        pools = self._get_available_pools(condition='and')
        self.assertEqual(len(pools), 0)

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_or_condition(self, p_assignments):
        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org['pool_id']],
            manage_own_resource_ids=[self.org['pool_id']])
        pools = self._get_available_pools(condition='or')
        self.assertEqual(len(pools), 9)

        p_assignments.return_value = self._set_manage_resources_config(
            manage_resource_ids=[self.org['pool_id']])
        pools = self._get_available_pools(condition='or')
        self.assertEqual(len(pools), 9)

    @patch(GET_ASSIGNMENTS_METHOD)
    def test_get_default_owner_id(self, p_assignments):
        p_assignments.return_value = self._set_manage_resources_config(
            manage_own_resource_ids=[self.org_id])
        pools = self._get_available_pools()
        self.assertEqual(len(pools), 9)
        code, employees_list = self.client.employee_list(self.org_id)
        self.assertEqual(code, 200)
        root_owner = [x for x in employees_list['employees'] if x[
            'auth_user_id'] == self._user_id][0]
        pool_owner_map = {
            'root': (root_owner['id'], root_owner['name']),
            'pool1.1': (self.employee['id'], self.employee['name']),
            'pool1.2': (self.employee2['id'], self.employee2['name'])
        }
        for pool in pools:
            pool_name = pool['name']
            if pool_name not in pool_owner_map:
                self.assertIsNone(pool['default_owner_id'])
                self.assertIsNone(pool['default_owner_name'])
            else:
                owner_id, owner_name = pool_owner_map[pool_name]
                self.assertEqual(owner_id, pool['default_owner_id'])
                self.assertEqual(owner_name, pool['default_owner_name'])
