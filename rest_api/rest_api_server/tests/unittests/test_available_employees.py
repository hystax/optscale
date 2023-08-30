from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestAvailablePoolsApi(TestApiBase):
    AUTHORIZE_USER_LIST = ('rest_api.rest_api_server.controllers.assignment'
                           '.AssignmentController._authorize_user_list')

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "root"})
        self.org_id = self.org['id']
        self.organization_map = {'name': self.org['name'],
                                 'id': self.org['pool_id'],
                                 'parent_id': None,
                                 'children': [
                                     {
                                         'name': 'pool1',
                                         'children': []
                                     }
                                 ]}
        self.organization_name_id_map = {}
        self.total = 1
        self._create_children(self.organization_map)
        self.user_id = self.gen_id()
        self.user2_id = self.gen_id()
        self.user3_id = self.gen_id()
        self.employee = self._create_employee(self.user_id, self.org_id)
        self.employee2 = self._create_employee(self.user2_id, self.org_id)
        self.employee3 = self._create_employee(self.user3_id, self.org_id)
        self._mock_auth_user(self.user_id)

    def _create_pool(self, name, parent_id=None):
        code, resp = self.client.pool_create(self.org_id, {
            'name': name,
            'parent_id': parent_id
        })
        self.assertEqual(code, 201)
        return resp

    def _create_children(self, parent):
        for child in parent['children']:
            organization = self._create_pool(child['name'],
                                             parent_id=parent['id'])
            self.total += 1
            self.organization_name_id_map[child['name']] = organization
            child['id'] = organization['id']
            child['parent_id'] = parent['id']
            self._create_children(child)

    def _create_employee(self, user_id, organization_id):
        valid_employee = {
            'name': 'TestUser_%s' % self.gen_id()[:8],
            'auth_user_id': user_id,
        }
        code, employee = self.client.employee_create(organization_id,
                                                     valid_employee)
        self.assertEqual(code, 201)
        return employee

    def _get_pool_employees(self, pool_id, exclude_myself=False):
        code, resp = self.client.pool_employees_get(
            pool_id, exclude_myself=exclude_myself)
        self.assertEqual(code, 200)
        return resp['employees']

    @staticmethod
    def _configure_authorize_users_response(authorized_empls=None,
                                            restricted_empls=None):
        if authorized_empls:
            authorized = [empl['auth_user_id'] for empl in authorized_empls]
        else:
            authorized = []
        if restricted_empls:
            restricted = [empl['auth_user_id'] for empl in restricted_empls]
        else:
            restricted = []
        return authorized, restricted

    @patch(AUTHORIZE_USER_LIST)
    def test_get_pool_employees(self, p_authorize):
        """
        Basic get available employees for bu budges flow.
        Steps:
           - 1. Configure authorize response for 2 employees.
           - 2. Get available employees for bu pool.
           - 3. Verify employees in response. Count shout be 2. Employees should
             be from authorized list.
           - 4. Add the third employee to authorize response
           - 5. Get available employees.
           - 6. Verify employees in response. Count shout be 3. Employees should
             be from authorized list.
           - 7. Repeat step 6 with exclude myself param.
           - 8. Verify no current user in response.

        """
        authorized_empls = [self.employee, self.employee2]
        p_authorize.return_value = self._configure_authorize_users_response(
            authorized_empls=authorized_empls,
            restricted_empls=[self.employee3])
        target_pool_id = self.organization_name_id_map['pool1']['id']
        employees = self._get_pool_employees(target_pool_id)
        self.assertEqual(len(employees), 2)
        self.assertEqual(set([empl['id'] for empl in authorized_empls]),
                         set([empl['id'] for empl in employees]))
        authorized_empls = [self.employee, self.employee2, self.employee3]
        p_authorize.return_value = self._configure_authorize_users_response(
            authorized_empls=authorized_empls)
        employees = self._get_pool_employees(target_pool_id)
        self.assertEqual(len(employees), 3)
        self.assertEqual(set([empl['id'] for empl in authorized_empls]),
                         set([empl['id'] for empl in employees]))
        employees = self._get_pool_employees(target_pool_id,
                                             exclude_myself=True)
        self.assertEqual(len(employees), 2)
        for employee in employees:
            self.assertTrue(employee['id'], employee['id'])

    def test_get_pool_not_exist_employees(self):
        """
        Test to get employees for pool that doesn't exist.
        Steps:
           - 1. Request available employees with random pool id.
           - 2. Verify 404 code. Localized code is E0002.

        """
        code, resp = self.client.pool_employees_get(self.gen_id())
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], "OE0002")

    def test_get_pool_employee_in_other_org(self):
        """
        Test available employees if user is not a member in organization.
        Steps:
           - 1. Configure current user as unknown user i.e. from another org.
           - 2. Request available employees for valid pool id.
           - 3. Verify 403 code. Localized code is E0378.

        """
        target_pool_name = 'pool1'
        target_pool = self.organization_name_id_map[target_pool_name]

        self._mock_auth_user(self.gen_id())
        code, resp = self.client.pool_employees_get(target_pool['id'])
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], "OE0378")

    @patch(AUTHORIZE_USER_LIST)
    def test_get_pool_employee_employee_from_another_org(self, p_authorize):
        """
        Basic get available employees for bu budges flow.
        Steps:
           - 1. Create another org. Create employee for this org.
           - 2. Configure authorize response for 3 employees including empl from
             another org.
           - 3. Get available employees for bu pool from original org.
           - 4. Verify employees in response. Count shout be 2. Response
             shouldn't contain empl from another org.

        """
        _, new_org = self.client.organization_create(
            {'name': "new_root"})
        new_org_id = new_org['id']
        new_user_id = self.gen_id()
        new_empl = self._create_employee(new_user_id, new_org_id)
        authorized_empls = [self.employee, self.employee2, new_empl]
        p_authorize.return_value = self._configure_authorize_users_response(
            authorized_empls=authorized_empls,
            restricted_empls=[self.employee3])
        target_pool_name = 'pool1'
        target_pool = self.organization_name_id_map[target_pool_name]
        employees = self._get_pool_employees(target_pool['id'])
        self.assertEqual(len(employees), 2)
        for employee in employees:
            self.assertTrue(employee['id'], new_empl['id'])
