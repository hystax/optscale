import uuid
import datetime

import random
import string
from unittest.mock import patch
from auth_server.tests.unittests.test_api_base import TestAuthBase
from auth_server.models.models import (Type, User, Action, Role, Assignment,
                                       ActionGroup)
from auth_server.models.models import gen_salt
from auth_server.utils import hash_password


class TestRole(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.partner_1_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.partner_2_scope_id = '23dbde7f-e619-413a-b137-5369145e6359'
        self.customer_1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.customer_2_scope_id = '8970e5f4-c9d8-4a5d-87c5-b1cdc0269682'
        self.customer_3_scope_id = 'fcee7ceb-fbba-4072-9880-761789b0de0f'
        self.group_scope_id = 'be7b4d5e-33b6-40aa-bc6a-00c7d822606f'
        self.context = {
            "partner": self.partner_1_scope_id,
            "customer": self.customer_1_scope_id,
            "group": self.group_scope_id
        }
        self.hierarchy = (
            {'root': {'null': {'partner': {
                self.partner_1_scope_id:
                    {'customer': {
                        self.customer_1_scope_id:
                            {'group': [self.group_scope_id]},
                        self.customer_2_scope_id:
                            {'group': [self.group_scope_id]}
                    }},
                self.partner_2_scope_id:
                    {'customer': {
                        self.customer_3_scope_id:
                            {'group': [self.group_scope_id]}
                    }},
            }
            }}})
        admin_user = self.create_root_user()
        session = self.db_session
        self.type_partner = Type(id=10, name='partner', parent=admin_user.type)
        self.type_customer = Type(id=20, name='customer',
                                  parent=self.type_partner)
        self.type_group = Type(id=30, name='group', parent=self.type_customer)

        self.roles_action_group = ActionGroup(name='ag_roles')
        self.cloud_sites_action_group = ActionGroup(name='ag_cloud_sites')
        super_admin_action_group = ActionGroup(name='ag_super_admin')

        # admin action has type=root
        self.list_css_action = Action(
            name='LIST_CSS', type=self.type_customer,
            action_group=self.cloud_sites_action_group)
        create_cs_action = Action(name='CREATE_CS', type=self.type_customer,
                                  action_group=self.cloud_sites_action_group)
        edit_cs_action = Action(name='EDIT_CS', type=self.type_customer,
                                action_group=self.cloud_sites_action_group)
        delete_cs_action = Action(name='DELETE_CS', type=self.type_customer,
                                  action_group=self.cloud_sites_action_group)
        super_admin_action = Action(name='ADMIN', type=admin_user.type,
                                    action_group=super_admin_action_group)
        self.cs_admin_role = Role(name='CS ADMIN', type=self.type_customer,
                                  lvl=self.type_customer,
                                  scope_id=self.customer_1_scope_id,
                                  description='Cloud Sites Admin')
        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)
        session.add(self.roles_action_group)
        session.add(self.cloud_sites_action_group)
        session.add(self.list_css_action)
        session.add(create_cs_action)
        session.add(edit_cs_action)
        session.add(delete_cs_action)
        session.add(super_admin_action)
        session.add(self.cs_admin_role)
        self.cs_admin_role.assign_action(self.list_css_action)
        self.cs_admin_role.assign_action(create_cs_action)
        self.cs_admin_role.assign_action(edit_cs_action)
        session.commit()

    @patch("auth_server.controllers.base.BaseController.get_context")
    def _create_role(self, p_get_context, name="testRole",
                     lvl_id=20, is_active=True, type_id=None, scope_id=None,
                     shared=False, description=None):
        p_get_context.return_value = self.context
        return self.client.role_create(name=name, type_id=type_id,
                                       lvl_id=lvl_id, is_active=is_active,
                                       scope_id=scope_id, shared=shared,
                                       description=description)

    def _assign_role_action(self, role, action_name, action_group,
                            action_type=None):
        if not action_type:
            action_type = self.type_customer
        action = self.db_session.query(Action).filter_by(
            name=action_name).one_or_none()
        if not action:
            action = Action(name=action_name,
                            type=action_type,
                            action_group=action_group)
            self.db_session.add(action)
        role.assign_action(action)
        self.db_session.add(role)
        self.db_session.commit()

    def _create_test_assignment(self, user, role, type, scope_id):
        assignment = Assignment(user, role, type, scope_id)
        self.db_session.add(assignment)
        self.db_session.commit()
        return assignment

    def _create_test_role(self, name, type, scope_id, shared=False, lvl=None):
        if lvl is None:
            lvl = type
        role = Role(name=name,
                    type=type,
                    lvl=lvl,
                    shared=shared,
                    scope_id=scope_id,
                    description='test role')
        self.db_session.add(role)
        self.db_session.commit()
        return role

    def _create_test_user_with_role(self, type, scope_id):
        user = self._create_test_user(type, scope_id)
        role = Role(name='ROLE ADMIN',
                    type=type,
                    lvl=type,
                    scope_id=scope_id,
                    description='Roles Admin')
        assignment = Assignment(user, role, type, scope_id)
        self.db_session.add(role)
        self.db_session.add(assignment)
        self.db_session.commit()

        return user, role

    def _create_test_user(self, type, scope_id, email="user@domain.com"):
        salt = gen_salt()
        password = 'passwd'
        user = User(
            email, type=type,
            display_name='Some user',
            password=hash_password(password, salt),
            salt=salt,
            scope_id=scope_id, type_id=type.id)
        self.db_session.add(user)
        self.db_session.commit()
        self.client.token = self.get_token(user.email, password)
        return user

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    def test_get_self_role(self, p_res_info):
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        code, response = self.client.role_get(role.id)
        actions = response['actions']
        self.assertEqual(actions['ag_cloud_sites']['LIST_CSS'], False)
        self.assertEqual(actions['ag_cloud_sites']['CREATE_CS'], False)
        self.assertEqual(actions['ag_cloud_sites']['EDIT_CS'], False)
        self.assertTrue('ag_super_admin' not in actions)
        self.assertEqual(code, 200)

    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_another_role(self, p_get_hierarchy, p_get_context):
        p_get_context.return_value = self.context
        p_get_hierarchy.return_value = self.hierarchy
        self._create_test_user_with_role(self.type_customer,
                                         self.customer_1_scope_id)
        code, response = self.client.role_get(self.cs_admin_role.id)
        self.assertEqual(code, 403)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_roles_with_list_action(self, p_get_hierarchy, p_get_context,
                                        p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_get_context.return_value = self.context
        resource_name = 'Customer Name'
        p_res_info.return_value = {
            '19a00828-fbff-4318-8291-4b6c14a8066d': {
                'name': resource_name, 'type': 'customer'}}
        user, role = self._create_test_user_with_role(self.type_partner,
                                                      self.partner_1_scope_id)
        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)
        test_role2 = self._create_test_role("test_role2", self.type_customer,
                                            self.customer_2_scope_id)
        code, response = self.client.role_get(test_role1.id)
        self.assertEqual(code, 403)
        code, response = self.client.role_get(test_role2.id)
        self.assertEqual(code, 403)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        code, response = self.client.role_get(test_role1.id)
        self.assertEqual(response['description'], 'test role')
        self.assertEqual(response['shared'], False)
        self.assertEqual(response['scope_name'], resource_name)
        self.assertEqual(code, 200)
        code, response = self.client.role_get(test_role2.id)
        self.assertEqual(code, 200)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_roles_deleted_agrp(self, p_get_hierarchy, p_get_context,
                                    p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        p_get_context.return_value = self.context
        user, role = self._create_test_user_with_role(self.type_partner,
                                                      self.partner_1_scope_id)

        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)

        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        _, response = self.client.role_get(test_role1.id)
        self.assertIsNotNone(response['actions'].get(
            self.roles_action_group.name))
        session = self.db_session
        self.roles_action_group.deleted_at = int(
            datetime.datetime.utcnow().timestamp())
        session.add(self.roles_action_group)
        session.commit()
        _, response = self.client.role_get(test_role1.id)
        self.assertIsNone(response['actions'].get(
            self.roles_action_group.name))

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_roles_deleted_action(self, p_get_hierarchy, p_get_context,
                                      p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        p_get_context.return_value = self.context
        user, role = self._create_test_user_with_role(self.type_partner,
                                                      self.partner_1_scope_id)

        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)

        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        _, response = self.client.role_get(test_role1.id)
        self.assertIsNotNone(response['actions'][
            self.cloud_sites_action_group.name].get(
            self.list_css_action.name))
        session = self.db_session
        self.list_css_action.deleted_at = int(
            datetime.datetime.utcnow().timestamp())
        session.add(self.list_css_action)
        session.commit()
        _, response = self.client.role_get(test_role1.id)
        self.assertIsNone(response['actions'][
            self.cloud_sites_action_group.name].get(
            self.list_css_action.name))

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_shared_role(self, p_get_hierarchy, p_get_context,
                             p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        user = self._create_test_user(self.type_partner,
                                      self.partner_1_scope_id)
        shared_role = self._create_test_role("shared_role", self.type_partner,
                                             self.partner_1_scope_id,
                                             shared=True)
        shared_role2 = self._create_test_role("shared_role2",
                                              self.type_partner,
                                              self.partner_1_scope_id,
                                              shared=True,
                                              lvl=self.type_customer)
        self._create_test_assignment(user, shared_role,
                                     self.type_partner,
                                     self.partner_1_scope_id)
        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)
        self._assign_role_action(test_role1, "LIST_ROLES",
                                 self.roles_action_group)

        p_get_context.return_value = {
            "partner": self.partner_1_scope_id,
            "customer": self.customer_1_scope_id,
            "group": self.group_scope_id
        }
        user1 = self._create_test_user(self.type_customer,
                                       self.customer_1_scope_id,
                                       email="customer1@domain.com")
        self._create_test_assignment(user1, test_role1, self.type_customer,
                                     self.customer_1_scope_id)
        code, response = self.client.role_get(shared_role2.id)
        self.assertEqual(code, 200)
        code, _ = self.client.role_get(shared_role.id)
        self.assertEqual(code, 403)
        p_get_context.return_value = {
            "partner": self.partner_1_scope_id,
            "customer": self.customer_2_scope_id,
            "group": self.group_scope_id
        }
        user2 = self._create_test_user(self.type_customer,
                                       self.customer_2_scope_id,
                                       email="customer2@domain.com")
        self._create_test_assignment(user2, test_role1, self.type_customer,
                                     self.customer_2_scope_id)
        code, response = self.client.role_get(shared_role2.id)
        self.assertEqual(code, 200)

    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_get_shared_role_from_another_partner(self, p_get_hierarchy,
                                                  p_get_context):
        p_get_hierarchy.return_value = self.hierarchy
        p_get_context.return_value = {
            "partner": self.partner_2_scope_id,
            "customer": self.customer_3_scope_id,
            "group": self.group_scope_id
        }
        user = self._create_test_user(self.type_partner,
                                      self.partner_1_scope_id)
        shared_role = self._create_test_role("shared_role", self.type_partner,
                                             self.partner_1_scope_id,
                                             shared=True)
        self._create_test_assignment(user, shared_role,
                                     self.type_partner,
                                     self.partner_1_scope_id)
        self._create_test_user(self.type_customer, self.customer_3_scope_id,
                               email="customer3@domain.com")
        code, response = self.client.role_get(shared_role.id)
        self.assertEqual(code, 403)

    def test_create_role(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20,
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='MyDesc')
        self.assertEqual(code, 201)
        self.assertEqual(response['shared'], True)
        self.assertEqual(response['description'], 'MyDesc')

    def test_create_role_with_whitespace(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20,
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='       ')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'description should not contain only whitespaces')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_with_whitespace(self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=role.id,
                                                 actions=actions,
                                                 name='     ')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'name should not contain only whitespaces')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_own_role_with_edit_own_action(self, p_get_hierarchy,
                                                  p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        self._assign_role_action(role, "CREATE_CS",
                                 self.cloud_sites_action_group)
        code, response = self.client.role_get(role.id)
        response['actions']['ag_cloud_sites']['DELETE_CS'] = True
        response['actions']['ag_cloud_sites']['CREATE_CS'] = False
        code, response = self.client.role_update(id=role.id,
                                                 name="New role name",
                                                 actions=response['actions'])
        self.assertEqual(code, 200)
        self.assertEqual(response['actions']['ag_cloud_sites']['DELETE_CS'],
                         True)
        self.assertEqual(response['actions']['ag_cloud_sites']['CREATE_CS'],
                         False)
        self.assertEqual(response['name'], "New role name")

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_own_role_without_edit_own_action(self, p_get_hierarchy,
                                                     p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=role.id,
                                                 actions=actions)
        self.assertEqual(code, 403)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_with_edit_own_action(self, p_get_hierarchy,
                                              p_res_info):
        p_res_info.return_value = {}
        p_get_hierarchy.return_value = self.hierarchy
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=self.cs_admin_role.id,
                                                 actions=actions)
        self.assertEqual(code, 403)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_with_edit_role_action(self, p_get_hierarchy,
                                               p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_ROLES", self.roles_action_group)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=self.cs_admin_role.id,
                                                 actions=actions,
                                                 description='Test Desc')
        self.assertEqual(code, 200)
        self.assertEqual(response['description'], 'Test Desc')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_with_edit_sublevel_role_action(
            self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "EDIT_SUBLEVEL_ROLES",
                                 self.roles_action_group,
                                 action_type=self.type_partner)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=self.cs_admin_role.id,
                                                 actions=actions)
        self.assertEqual(code, 200)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_own_role_with_edit_sublevel_role_action(
            self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "EDIT_SUBLEVEL_ROLES",
                                 self.roles_action_group,
                                 action_type=self.type_partner)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        code, response = self.client.role_update(id=role.id,
                                                 actions=actions)
        self.assertEqual(code, 403)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_invalid_action(self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        actions = {'ag_super_admin': {}}
        actions['ag_super_admin']['ADMIN'] = True
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        code, response = self.client.role_update(id=role.id,
                                                 actions=actions)
        self.assertEqual(code, 400)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_delete_role(self, p_get_context, p_res_info):
        p_get_context.return_value = self.context
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        self._assign_role_action(role, "DELETE_ROLE", self.roles_action_group)
        _, role = self._create_role(type_id=self.type_customer.id,
                                    scope_id=self.customer_1_scope_id)
        code, _ = self.client.role_delete(role['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.role_get(role['id'])
        self.assertEqual(code, 404)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_list_roles_customer_lvl(self, p_get_hierarchy, p_get_context,
                                     p_res_info):
        p_res_info.return_value = {}
        p_get_hierarchy.return_value = self.hierarchy
        p_get_context.return_value = self.context
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        _, role = self._create_role(type_id=self.type_customer.id,
                                    scope_id=self.customer_1_scope_id)
        role_id = role['id']
        code, roles = self.client.role_list()
        self.assertEqual(code, 200)
        self.assertTrue(list(filter(lambda x: x.get('id') in [role_id],
                                    roles)))
        self.assertTrue(len(roles) == 3)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_list_roles_roles_with_shared_role(self, p_get_hierarchy,
                                               p_get_context, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        p_get_context.return_value = self.context
        partner, role = self._create_test_user_with_role(
            self.type_partner, self.partner_1_scope_id)
        user = self._create_test_user(self.type_customer,
                                      self.customer_1_scope_id,
                                      email="customer1@domain.com")
        shared_role = self._create_test_role("shared_role", self.type_customer,
                                             self.customer_1_scope_id,
                                             shared=True)
        self._create_test_assignment(partner, shared_role,
                                     self.type_partner,
                                     self.partner_1_scope_id)

        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)
        self._assign_role_action(test_role1, "LIST_ROLES",
                                 self.roles_action_group)

        self._create_test_assignment(user, test_role1,
                                     self.type_customer,
                                     self.customer_1_scope_id)
        code, roles = self.client.role_list()
        self.assertEqual(code, 200)
        self.assertTrue(shared_role.id in [x["id"] for x in roles])
        self.assertTrue(len(roles) == 3)

        test_role2 = self._create_test_role("test_role2", self.type_customer,
                                            self.customer_3_scope_id)
        self._assign_role_action(test_role2, "LIST_ROLES",
                                 self.roles_action_group)
        user = self._create_test_user(self.type_customer,
                                      self.customer_3_scope_id,
                                      email="customer3@domain.com")
        self._create_test_assignment(user, test_role2,
                                     self.type_customer,
                                     self.customer_3_scope_id)
        p_get_context.return_value = {
            "partner": self.partner_2_scope_id,
            "customer": self.customer_3_scope_id,
            "group": self.group_scope_id
        }
        code, roles = self.client.role_list()
        self.assertEqual(code, 200)
        self.assertFalse(shared_role.id in [x["id"] for x in roles])
        self.assertTrue(len(roles) == 1)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_list_roles_group_lvl(self, p_get_hierarchy, p_get_context,
                                  p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_get_context.return_value = self.context
        resource_name = 'Group1'
        p_res_info.return_value = {
            'be7b4d5e-33b6-40aa-bc6a-00c7d822606f': {
                'name': resource_name, 'type': 'group'}
        }
        _, role = self._create_test_user_with_role(self.type_group,
                                                   self.group_scope_id)
        self._assign_role_action(role, "CREATE_ROLE",
                                 self.roles_action_group, self.type_group)
        self._assign_role_action(role, "LIST_ROLES",
                                 self.roles_action_group, self.type_group)
        _, role = self._create_role(type_id=self.type_group.id,
                                    scope_id=self.group_scope_id,
                                    lvl_id=30)
        role_id = role['id']
        code, roles = self.client.role_list()
        self.assertEqual(code, 200)
        self.assertTrue(list(filter(lambda x: x.get('id') in [role_id],
                                    roles)))
        self.assertEqual(len(list(filter(
            lambda x: x.get('scope_name') in [resource_name], roles))), 2)
        self.assertTrue(len(roles) == 2)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_list_roles_assignable_to_user(self, p_get_hierarchy,
                                           p_get_context, p_res_info):
        p_res_info.return_value = {}
        p_get_hierarchy.side_effect = [self.hierarchy,
                                       self.hierarchy,
                                       {
                                           "customer": {
                                               self.customer_1_scope_id: {
                                                   "group": self.group_scope_id
                                               }
                                           }
                                       },
                                       self.hierarchy,
                                       {
                                           "customer": {
                                               self.customer_3_scope_id: {
                                                   "group": self.group_scope_id
                                               }
                                           }
                                       }]
        p_get_context.return_value = self.context

        test_role1 = self._create_test_role("test_role1", self.type_customer,
                                            self.customer_1_scope_id)
        user1 = self._create_test_user(self.type_customer,
                                       self.customer_1_scope_id,
                                       email="customer1@domain.com")
        partner, role = self._create_test_user_with_role(
            self.type_partner, self.partner_1_scope_id)
        self._assign_role_action(role, "LIST_ROLES",
                                 self.roles_action_group)

        code, roles = self.client.role_list(assignable_to_user_id=user1.id)
        self.assertEqual(code, 200)
        self.assertEqual(len(roles), 0)

        self._assign_role_action(role, "LIST_USERS",
                                 self.roles_action_group)
        shared_role = self._create_test_role("shared_role", self.type_partner,
                                             self.partner_1_scope_id,
                                             shared=True)
        self._create_test_assignment(partner, shared_role,
                                     self.type_partner,
                                     self.partner_1_scope_id)
        code, roles = self.client.role_list(assignable_to_user_id=partner.id)
        self.assertEqual(code, 200)
        self.assertTrue(shared_role.id in [x["id"] for x in roles])
        self.assertTrue(test_role1.id in [x["id"] for x in roles])
        self.assertTrue(len(roles) == 3)

        test_role2 = self._create_test_role("test_role2", self.type_customer,
                                            self.customer_3_scope_id)
        p_get_context.return_value = {
            "partner": self.partner_2_scope_id,
            "customer": self.customer_3_scope_id
        }
        code, roles = self.client.role_list(assignable_to_user_id=user1.id)
        self.assertEqual(code, 200)
        self.assertTrue(test_role2.id in [x["id"] for x in roles])
        self.assertTrue(len(roles) == 1)

    def test_create_duplicate_role(self):
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE",
                                 self.roles_action_group, self.type_partner)
        role_name = 'Role'
        _, response = self._create_role(name=role_name, lvl_id=20, type_id=20,
                                        scope_id=self.partner_1_scope_id)
        code, response = self._create_role(name=role_name, lvl_id=20,
                                           type_id=20,
                                           scope_id=self.partner_1_scope_id)
        self.assertEqual(code, 409)
        self.assertEqual(response['error']['reason'],
                         'Role %s already exists' % role_name)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_recreate_deleted_role(self, p_context, p_res_info):
        p_context.return_value = {'partner': self.partner_1_scope_id}
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        self._assign_role_action(role, "DELETE_ROLE", self.roles_action_group)

        role_name = 'Role'
        _, response = self._create_role(name=role_name, lvl_id=20, type_id=20,
                                        scope_id=self.partner_1_scope_id)
        code, _ = self.client.role_delete(response['id'])
        code, response = self._create_role(name=role_name, lvl_id=20,
                                           type_id=20,
                                           scope_id=self.partner_1_scope_id)
        self.assertEqual(code, 201)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def delete_role_forbidden(self, p_context, p_res_info):
        p_context.return_value = {}
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        self._assign_role_action(role, "DELETE_ROLE", self.roles_action_group)
        _, response = self._create_role(name='RoleRole', lvl_id=20, type_id=20,
                                        scope_id=self.partner_1_scope_id)
        code, _ = self.client.role_delete(response['id'])
        self.assertEqual(code, 403)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_same_name(self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        role_name = 'Role-Role'
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        self._assign_role_action(role, "EDIT_ROLES", self.roles_action_group)
        _, response = self._create_role(name='RoleRole', lvl_id=20, type_id=20,
                                        scope_id=self.customer_1_scope_id)
        code, response = self.client.role_update(response['id'],
                                                 name=role_name,
                                                 actions={})
        self.assertEqual(code, 200)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_invalid_lvl_id(self, p_context, p_res_info):
        p_context.return_value = {'partner': self.partner_1_scope_id}
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_partner,
                                                   self.partner_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        self._assign_role_action(role, "LIST_ROLES", self.roles_action_group)
        self._assign_role_action(role, "DELETE_ROLE", self.roles_action_group)

        role_name = 'Role'
        lvl_id = 10
        code, response = self._create_role(
            name=role_name, lvl_id=lvl_id, type_id=20,
            scope_id=self.partner_1_scope_id, is_active=True, shared=False)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Cannot create role with given lvl for customer')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_with_immutables(self, p_get_context, p_get_hierarchy,
                                         p_res_info):
        p_get_context.return_value = self.context
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        for immutable_param in ['id', 'created_at', 'deleted_at']:
            body = {
                'name': 'name_%s' % immutable_param,
                'type_id': 20,
                'lvl_id': 20,
                'is_active': True,
                'scope_id': self.customer_1_scope_id,
                'shared': False,
                immutable_param: 'value'
            }
            code, response = self.client.post('roles', body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Parameter "%s" is immutable' % immutable_param)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_with_unexpected_params(self, p_get_context,
                                                p_get_hierarchy, p_res_info):
        p_get_context.return_value = self.context
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        for unexpected_param in ['param', 2, '']:
            body = {
                'name': 'name_%s' % unexpected_param,
                'type_id': 20,
                'lvl_id': 20,
                'is_active': True,
                'scope_id': self.customer_1_scope_id,
                'shared': False,
                unexpected_param: 'value'
            }
            code, response = self.client.post('roles', body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Unexpected parameters: %s' % unexpected_param)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_update_role_with_immutables(self, p_get_context, p_get_hierarchy,
                                         p_res_info):
        p_get_context.return_value = self.context
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        for immutable_param in ['id', 'created_at', 'deleted_at', 'lvl_id',
                                'type_id', 'scope_id']:
            body = {
                'actions': {},
                immutable_param: 'value'
            }
            code, response = self.client.patch('roles/%s' % role.id, body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Parameter "%s" is immutable' % immutable_param)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_update_role_with_unexpected_params(self, p_get_context,
                                                p_get_hierarchy, p_res_info):
        p_get_context.return_value = self.context
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        for unexpected_param in ['param', 2, '']:
            body = {
                'actions': {},
                unexpected_param: 'value'
            }
            code, response = self.client.patch('roles/%s' % role.id, body)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['reason'],
                             'Unexpected parameters: %s' % unexpected_param)

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_own_role_with_invalid_action_group(self, p_get_hierarchy,
                                                       p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        self._assign_role_action(role, "CREATE_CS",
                                 self.cloud_sites_action_group)
        code, response = self.client.role_get(role.id)
        response['actions']['invalid'] = {'DELETE_CS': True,
                                          'CREATE_CS': False}
        code, response = self.client.role_update(id=role.id,
                                                 name="New role name",
                                                 actions=response['actions'])
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Action group "invalid" cannot be assigned')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_invalid_name(self, p_get_hierarchy, p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        self._assign_role_action(role, "CREATE_CS",
                                 self.cloud_sites_action_group)
        code, response = self.client.role_update(id=role.id,
                                                 name=123)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'name should be a string')

        long_name = "".join(
            random.choice(string.ascii_lowercase) for _ in range(256))
        code, response = self.client.role_update(id=role.id,
                                                 name=long_name)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'name should contain 1-255 characters')

    def test_create_role_invalid_name(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20, name=1234,
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='MyDesc')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'name should be a string')

        long_name = "".join(
            random.choice(string.ascii_lowercase) for _ in range(256))
        code, response = self._create_role(type_id=20, name=long_name,
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='MyDesc')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'name should contain 1-255 characters')

    def test_create_role_invalid_lvl_id_string(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20, name='name',
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='MyDesc',
                                           lvl_id='str')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'lvl_id should be integer')

    def test_create_role_invalid_type_id_string(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id='20', name='name',
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='MyDesc')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'type_id should be integer')

    def test_create_role_invalid_description(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20, name='name',
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description=123)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'description should be a string')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_invalid_description(self, p_get_hierarchy,
                                             p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_OWN_ROLES",
                                 self.roles_action_group)
        self._assign_role_action(role, "CREATE_CS",
                                 self.cloud_sites_action_group)
        code, response = self.client.role_get(role.id)
        response['actions']['invalid'] = {'DELETE_CS': True,
                                          'CREATE_CS': False}
        code, response = self.client.role_update(role.id, description=123)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'description should be a string')

    def test_create_role_empty_description(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20, name='name',
                                           scope_id=self.customer_1_scope_id,
                                           shared=True, description='')
        self.assertEqual(code, 201)
        self.assertEqual(response['description'], '')

    def test_create_role_with_number_scope_id(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        code, response = self._create_role(type_id=20, name='name',
                                           scope_id=12345,
                                           shared=True, description='')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OA0033')
        self.assertEqual(response['error']['params'], ['scope_id'])

    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_without_is_active(self, p_get_context):
        p_get_context.return_value = self.context

        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 20,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': '19a00828-fbff-4318-8291-4b6c14a8066d',
                'lvl_id': 20}
        code, response = self.client.post('roles', body)
        self.assertEqual(code, 201)
        self.assertTrue(response['is_active'])

    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_without_required_params(self, p_get_context):
        p_get_context.return_value = self.context

        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 20,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': '19a00828-fbff-4318-8291-4b6c14a8066d',
                'lvl_id': 20}
        for param in ['name', 'lvl_id', 'type_id']:
            request_body = body.copy()
            request_body.pop(param)
            code, response = self.client.post('roles', request_body)
            self.assertEqual(code, 400)
            self.assertTrue(response['error']['reason'],
                            '%s is required' % param)

    def test_create_role_empty_scope_id(self):
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 20,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': '',
                'lvl_id': 20}
        code, response = self.client.post('roles', body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'], 'Invalid scope_id')

    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_root_with_null_scope_id(self, p_get_context):
        p_get_context.return_value = self.context
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 0,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': None,
                'lvl_id': 0}
        code, response = self.client.post('roles', body)
        self.assertEqual(code, 201)

    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_with_not_existing_type_id(self, p_get_context):
        p_get_context.return_value = self.context

        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 123,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': '19a00828-fbff-4318-8291-4b6c14a8066d',
                'lvl_id': 20}
        code, response = self.client.post('roles', body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'Invalid type with id %s' % 123)

    @patch("auth_server.controllers.base.BaseController.get_context")
    def test_create_role_with_invalid_scope_id(self, p_get_context):
        p_get_context.return_value = self.context

        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "CREATE_ROLE", self.roles_action_group)
        body = {'type_id': 0,
                'shared': True,
                'name': 'testRole',
                'description': 'MyDesc',
                'scope_id': 'invalid',
                'lvl_id': 20}
        code, response = self.client.post('roles', body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'], 'Invalid scope_id')

    @patch("auth_server.controllers.base.BaseController.get_resources_info")
    @patch(
        "auth_server.controllers.base.BaseController.get_downward_hierarchy")
    def test_update_role_without_actions(self, p_get_hierarchy,
                                         p_res_info):
        p_get_hierarchy.return_value = self.hierarchy
        p_res_info.return_value = {}
        _, role = self._create_test_user_with_role(self.type_customer,
                                                   self.customer_1_scope_id)
        self._assign_role_action(role, "EDIT_ROLES", self.roles_action_group)
        actions = {'ag_cloud_sites': {}}
        actions['ag_cloud_sites']['DELETE_CS'] = True
        body = {
            'description': 'Test Desc'
        }
        url = 'roles/%s' % self.cs_admin_role.id

        code, response = self.client.patch(url, body)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'], 'actions is required')

    def test_purposed_roles(self):
        code, response = self.client.get_purposed_role('')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'], 'purpose is required')

        code, response = self.client.get_purposed_role('some')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         'some is not a valid purpose')

        code, response = self.client.get_purposed_role('optscale_manager')
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'],
                         'Role with purpose optscale_manager not found')

        secret = self.client.secret
        self.client.secret = 'bad_secret'
        code, response = self.client.get_purposed_role('optscale_manager')
        self.assertEqual(code, 403)
        self.assertEqual(response['error']['reason'], 'Bad secret')
        self.client.secret = None
        code, response = self.client.get_purposed_role('optscale_manager')
        self.assertEqual(code, 401)
        self.client.secret = secret

        role = Role(name='some name', type=self.type_partner,
                    lvl=self.type_partner, scope_id=self.partner_1_scope_id,
                    description='asd', purpose='optscale_manager')
        session = self.db_session
        session.add(role)
        session.commit()
        code, response = self.client.get_purposed_role('optscale_manager')
        self.assertEqual(code, 200)
        self.assertEqual(response['id'], role.id)
        self.assertEqual(response['purpose'], role.purpose.value)
