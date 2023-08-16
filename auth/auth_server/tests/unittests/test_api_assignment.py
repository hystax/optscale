from unittest.mock import patch

from auth.auth_server.models.models import (Type, User, Action, Role, Assignment,
                                            ActionGroup)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password


class TestAssignment(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version=version)
        self.partner1_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.customer2_scope_id = '6cfea3e7-a037-4529-9a14-dd9c5151b1f5'
        self.partner2_scope_id = '843f42c4-76b5-467f-b5e3-f7370b1235d6'
        self.customer2_1_scope_id = '70e552f4-032f-4989-bdbb-50a9d66920a2'
        self.hierarchy = (
            {'root': {'null': {'partner': {
                'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d':
                    {'customer': {
                        '19a00828-fbff-4318-8291-4b6c14a8066d':
                            {'group': ['be7b4d5e-33b6-40aa-bc6a-00c7d822606f']
                             },
                        '6cfea3e7-a037-4529-9a14-dd9c5151b1f5':
                            {'group': ['e8b8b4e9-a92d-40b5-a5db-b38bf5314ef9',
                                       '42667dde-0427-49be-9541-8e99362ee96e']
                             },
                    }},
                '843f42c4-76b5-467f-b5e3-f7370b1235d6':
                    {'customer': {
                        '70e552f4-032f-4989-bdbb-50a9d66920a2':
                            {'group': ['18559e53-fde8-4d73-81ef-57146bb0dde9']}
                    }}}}}})
        admin_user = self.create_root_user()
        session = self.db_session
        self.type_partner = Type(id=10, name='partner', parent=admin_user.type)
        self.type_customer = Type(id=20, name='customer',
                                  parent=self.type_partner)
        self.type_group = Type(id=30, name='group', parent=self.type_customer)
        user_partner_salt = gen_salt()
        self.user_partner_password = 'passwd!!111'
        # first partner user
        self.user_partner1 = User(email='partner@company.com',
                                  password=hash_password(
                                      self.user_partner_password,
                                      user_partner_salt),
                                  display_name='Partner user',
                                  scope_id=self.partner1_scope_id,
                                  salt=user_partner_salt,
                                  type_id=self.type_partner.id)

        user_customer1_salt = gen_salt()
        self.user_customer1_password = 'p@sswRD!'
        self.user_customer1 = User(
            'customer@example.com', type=self.type_customer,
            salt=user_customer1_salt,
            display_name='Customer user',
            password=hash_password(
                self.user_customer1_password, user_customer1_salt),
            scope_id=self.customer1_scope_id, type_id=self.type_customer.id)

        user_action_group = ActionGroup(name='MANAGE_USERS')
        roles_action_group = ActionGroup(name='MANAGE_ROLES')
        action_list_users = Action(name='LIST_USERS', type=self.type_customer,
                                   action_group=user_action_group)
        action_create_user = Action(name='CREATE_USER',
                                    type=self.type_customer,
                                    action_group=user_action_group)
        action_create_role = Action(name='CREATE_ROLE',
                                    type=self.type_customer,
                                    action_group=roles_action_group)
        action_update_own_roles = Action(name='EDIT_OWN_ROLES',
                                         type=self.type_customer,
                                         action_group=roles_action_group)
        action_list_roles = Action(name='LIST_ROLES', type=self.type_customer,
                                   action_group=roles_action_group)
        action_assign_user_self = Action(name='ASSIGN_SELF',
                                         type=self.type_customer,
                                         action_group=user_action_group)
        action_assign_user = Action(name='ASSIGN_USER',
                                    type=self.type_customer,
                                    action_group=user_action_group)

        self.admin_role = Role(name='ADMIN', type=self.type_partner,
                               lvl=self.type_partner,
                               scope_id=self.partner1_scope_id,
                               description='Admin')
        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)

        session.add(self.user_partner1)
        session.add(self.user_customer1)

        session.add(self.admin_role)
        self.admin_role.assign_action(action_list_users)
        self.admin_role.assign_action(action_list_roles)
        self.admin_role.assign_action(action_assign_user_self)
        self.admin_role.assign_action(action_assign_user)
        self.admin_role.assign_action(action_create_user)
        self.admin_role.assign_action(action_create_role)
        self.admin_role.assign_action(action_update_own_roles)
        self.assignment = Assignment(self.user_partner1, self.admin_role,
                                     self.type_partner,
                                     self.partner1_scope_id)
        session.add(self.assignment)
        session.commit()
        self.client.token = self.get_token(self.user_partner1.email,
                                           self.user_partner_password)
        patch('auth.auth_server.controllers.user.UserController.'
              'domain_blacklist').start()

    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    def _create_role(self, p_get_context, name, lvl_id, type_id, context,
                     scope_id=None, is_active=True, shared=False,
                     description=None):
        """
        Wraps create role API
        :param p_get_context:
        :param name:
        :param lvl_id:
        :param type_id:
        :param context:
        :param scope_id:
        :param is_active:
        :param shared:
        :param description:
        :return:
        """
        p_get_context.return_value = context
        return self.client.role_create(name=name, type_id=type_id,
                                       lvl_id=lvl_id, is_active=is_active,
                                       scope_id=scope_id, shared=shared,
                                       description=description)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    def test_basic_assignment_list(self, p_res_info):
        p_res_info.return_value = {
            self.partner1_scope_id: {
                'name': 'some_org_name',
                'type': 'organization'
            }
        }
        code, response = self.client.assignment_list(self.user_partner1.id)
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(len(list(filter(lambda x: x['role_id'] in [
            self.admin_role.id], response))), 1)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_baisc_assignment_get(self, p_hierarchy, p_res_info):
        resource_partner_name = 'Partner1'
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {
            self.partner1_scope_id: {
                'name': resource_partner_name, 'type': 'partner'}
        }
        code, response = self.client.assignment_get(
            self.assignment.id, self.user_partner1.id)
        self.assertEqual(code, 200)
        self.assertEqual(response['scope_name'], resource_partner_name)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_basic_assignment_delete_by_token(self, p_hierarchy, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        self.client.secret = None
        code, response = self.client.assignment_delete(
            self.assignment.id, self.user_partner1.id)
        self.assertEqual(code, 204)
        code, response = self.client.assignment_get(self.assignment.id,
                                                    self.user_partner1.id)
        self.assertEqual(code, 404)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_basic_assignment_delete_by_secret(self, p_hierarchy, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        code, response = self.client.assignment_delete(
            self.assignment.id, self.user_partner1.id)
        self.assertEqual(code, 204)
        code, response = self.client.assignment_get(self.assignment.id,
                                                    self.user_partner1.id)
        self.assertEqual(code, 404)

    @patch(
        "auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_partner_assign_self(self, p_hierarchy, p_context, p_res_info):
        """
        try to create partner assignment for self
        :param p_hierarchy:
        :param p_context:
        :param p_res_info:
        :return:
        """
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id}
        p_context.return_value = context
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_partner.id,
                                    type_id=self.type_partner.id,
                                    context=context,
                                    scope_id=self.partner1_scope_id)
        self.client.role_update(
            self.admin_role.id,
            actions={'MANAGE_USERS': {'ASSIGN_SELF': False}})
        code, response = self.client.assignment_create(
            self.user_partner1.id, role['id'], self.type_partner.id,
            self.partner1_scope_id)
        self.assertEqual(code, 403)
        self.client.role_update(
            self.admin_role.id,
            actions={'MANAGE_USERS': {'ASSIGN_SELF': True}})
        code, response = self.client.assignment_create(
            self.user_partner1.id, role['id'], self.type_partner.id,
            self.partner1_scope_id)
        self.assertEqual(code, 201)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assign_role_another_resource(self, p_hierarchy, p_context,
                                              p_res_info):
        """
        create user, role and try to assign role to another
        (not from our context) resource, will raise 403
        :param p_hierarchy:
        :param p_context:
        :param p_res_info:
        :return:
        """
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_partner.id,
            scope_id=self.partner1_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_customer.id,
                                    type_id=self.type_partner.id,
                                    context=context,
                                    scope_id=self.partner1_scope_id)
        code, response = self.client.assignment_create(
            user['id'], role['id'], self.type_partner.id,
            self.partner2_scope_id)
        self.assertEqual(code, 403)
        code, response = self.client.assignment_create(
            user['id'], role['id'], self.type_partner.id,
            self.customer2_1_scope_id)
        self.assertEqual(code, 403)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assignment_create_with_immutable(
            self, p_hierarchy, p_context, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id,
                   'customer': self.customer1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_customer.id,
            scope_id=self.customer1_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_customer.id,
                                    type_id=self.type_customer.id,
                                    context=context,
                                    scope_id=self.customer1_scope_id)
        for immutable_param in ['id', 'created_at', 'deleted_at']:
            body = {
                "role_id": role['id'],
                "type_id": self.type_customer.id,
                "resource_id": self.customer1_scope_id,
                immutable_param: "value"
            }
            code, response = self.client.post(
                'users/%s/assignments' % user['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Parameter "%s" is immutable' % immutable_param)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assignment_create_with_unexpected_param(
            self, p_hierarchy, p_context, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id,
                   'customer': self.customer1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_customer.id,
            scope_id=self.customer1_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_customer.id,
                                    type_id=self.type_customer.id,
                                    context=context,
                                    scope_id=self.customer1_scope_id)
        for unexpected_param in ['param', 6, '', 'user_id']:
            body = {
                "role_id": role['id'],
                "type_id": self.type_customer.id,
                "resource_id": self.customer1_scope_id,
                unexpected_param: "value"
            }
            code, response = self.client.post(
                'users/%s/assignments' % user['id'], body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Unexpected parameters: %s' % unexpected_param)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assignment_create_with_invalid_parameters(
            self, p_hierarchy, p_context, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id,
                   'customer': self.customer1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_customer.id,
            scope_id=self.customer1_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_customer.id,
                                    type_id=self.type_customer.id,
                                    context=context,
                                    scope_id=self.customer1_scope_id)
        code, response = self.client.assignment_create(
            user['id'], str(role['id']), self.type_customer.id,
            self.customer1_scope_id)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'role_id should be integer')

        code, response = self.client.assignment_create(
            user['id'], None, self.type_customer.id,
            self.customer1_scope_id)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'role_id is required')

        code, response = self.client.assignment_create(
            user['id'], role['id'], None,
            self.customer1_scope_id)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'type_id is required')

        code, response = self.client.assignment_create(
            user['id'], role['id'], str(self.type_customer.id),
            self.customer1_scope_id)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'type_id should be integer')

    @patch(
        "auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assign_role_higher_lvl(self, p_hierarchy, p_context,
                                        p_res_info):
        """
        create user, role and assign role to another user from same level
        :param p_hierarchy:
        :param p_context:
        :param p_res_info:
        :return:
        """
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password',
            display_name='User',
            type_id=self.type_partner.id,
            scope_id=self.partner1_scope_id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_partner.id,
                                    type_id=self.type_partner.id,
                                    context=context,
                                    scope_id=self.partner1_scope_id)
        code, response = self.client.assignment_create(
            user['id'], role['id'], self.type_customer.id,
            self.customer1_scope_id)
        self.assertEqual(code, 403)

    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def _create_user(self, p_hierarchy, email, password, display_name,
                     type_id=None, scope_id=None, is_active=True):
        p_hierarchy.return_value = self.hierarchy
        return self.client.user_create(email, password,
                                       display_name=display_name,
                                       is_active=is_active)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_self_assignment_list(self, p_hierarchy, p_res_info):
        partner_resource_name = 'Partner'
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {
            self.partner1_scope_id: {
                'name': partner_resource_name,
                'type': 'partner'
            }
        }
        code, response = self.client.my_assignment_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        self.assertEqual(len(list(filter(lambda x: x['role_id'] in [
            self.admin_role.id], response))), 1)

    @patch("auth.auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth.auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth.auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_api_assignment_create_registration(
            self, p_hierarchy, p_context, p_res_info):
        p_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        context = {'partner': self.partner1_scope_id,
                   'customer': self.customer1_scope_id}
        p_context.return_value = context
        _, user = self._create_user(
            email='user@email.com', password='password', display_name='User',
            type_id=self.type_partner.id)
        _, role = self._create_role(name='User Role',
                                    lvl_id=self.type_partner.id,
                                    type_id=self.type_partner.id,
                                    context=context)
        code, assignment = self.client.assignment_register(
            user['id'], role['id'],
            self.type_partner.id, self.partner1_scope_id)
        self.assertEqual(code, 201)
        self.assertEqual(assignment['role_id'], role['id'])
        self.assertEqual(assignment['user_id'], user['id'])
        self.assertEqual(assignment['type_id'], self.type_partner.id)
        self.assertEqual(assignment['resource_id'], self.partner1_scope_id)
        self.client.secret = 'bad_secret'
        code, response = self.client.assignment_register(
            user['id'], role['id'],
            self.type_partner.id, self.partner1_scope_id)
        self.assertEqual(code, 403)
        self.client.secret = None
        code, response = self.client.assignment_register(
            user['id'], role['id'],
            self.type_partner.id, self.partner1_scope_id)
        self.assertEqual(code, 401)
