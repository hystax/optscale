import json

from auth.auth_server.models.models import (
    Type, User, Action, Role, Assignment, ActionGroup, UserOption)
from auth.auth_server.models.models import gen_salt
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password


class TestUserOptionsApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.partner_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.customer1_scope_id = '19a00828-fbff-4318-8291-4b6c14a8066d'
        self.customer2_scope_id = '6cfea3e7-a037-4529-9a14-dd9c5151b1f5'
        self.group11_scope_id = 'be7b4d5e-33b6-40aa-bc6a-00c7d822606f'
        self.hierarchy = (
            {'partner': {
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
                '843f42c4-76b5-467f-b5e3-f7370b1235d6': {'customer': {}}}})
        admin_user = self.create_root_user()
        session = self.db_session
        type_partner = Type(id_=10, name='partner', parent=admin_user.type)
        type_customer = Type(id_=20, name='customer', parent=type_partner)
        type_group = Type(id_=30, name='group', parent=type_customer)
        self.user_type_id = int(type_group.id)
        salt = gen_salt()
        self.user_partner_email = 'partner@domain.com'
        self.user_partner_password = 'passwd!!!111'
        user_partner = User(
            self.user_partner_email, type_=type_partner,
            password=hash_password(
                self.user_partner_password, salt),
            display_name='Partner user', scope_id=self.partner_scope_id,
            salt=salt, type_id=type_partner.id)
        self.user_customer_password = 'p@sswRD!'
        user_customer = User(
            'customer@domain.com', type_=type_customer,
            salt=salt,
            display_name='Customer user',
            password=hash_password(
                self.user_customer_password, salt),
            scope_id=self.customer1_scope_id, type_id=type_customer.id)
        customer2_salt = gen_salt()
        self.user_customer2_password = 'p4$$w0rddd'
        self.user_customer2 = User(
            'customer2@domain.com', type_=type_customer,
            salt=customer2_salt,
            display_name='user customer2',
            password=hash_password(self.user_customer2_password,
                                   customer2_salt),
            scope_id=self.customer2_scope_id, type_id=type_customer.id)

        user_action_group = ActionGroup(name='Manage users and assignments')
        # admin action has type=root
        action_list_users = Action(name='LIST_USERS', type_=type_customer,
                                   action_group=user_action_group)
        action_edit_user_info = Action(name='EDIT_USER_INFO',
                                       type_=type_customer,
                                       action_group=user_action_group)
        admin_role = Role(name='ADMIN', type_=type_customer,
                          lvl=type_customer, scope_id=self.customer1_scope_id,
                          description='Admin')
        partner1_nodelete_role = Role(name='P1 No delete', type_=type_partner,
                                      lvl=type_customer,
                                      scope_id=self.partner_scope_id)
        partner1_delete_role = Role(name='P1 User Deleter', type_=type_partner,
                                    lvl=type_customer)
        session.add(type_partner)
        session.add(type_customer)
        session.add(type_group)
        session.add(user_partner)
        session.add(user_customer)
        session.add(self.user_customer2)
        session.add(action_list_users)
        session.add(action_edit_user_info)
        session.add(admin_role)
        session.add(partner1_nodelete_role)
        session.add(partner1_delete_role)
        admin_role.assign_action(action_list_users)
        admin_role.assign_action(action_edit_user_info)
        partner1_nodelete_role.assign_action(action_list_users)
        assignment = Assignment(user_customer, admin_role,
                                type_customer, self.customer1_scope_id)
        assignment_p_c1 = Assignment(user_partner, partner1_nodelete_role,
                                     type_customer, self.customer1_scope_id)
        assignment_p_c1_del = Assignment(user_partner, partner1_delete_role,
                                         type_partner, self.partner_scope_id)

        session.add(assignment)
        session.add(assignment_p_c1)
        session.add(assignment_p_c1_del)
        session.commit()
        self.client.token = self.get_token(user_customer.email,
                                           self.user_customer_password)

        self.user_id1 = user_customer.id
        self.user_id2 = self.user_customer2.id
        self.user_value1 = json.dumps({'key1': 'value1'})
        self.value1 = {'value': self.user_value1}
        self.name1 = 'default_option'
        self.user_value2 = json.dumps({'key2': 'value2'})
        self.value2 = {'value': self.user_value2}
        self.name2 = 'new_option'
        self.user_option_1 = UserOption(user_id=self.user_id1, name=self.name1,
                                        value=self.user_value1)
        self.user_option_2 = UserOption(user_id=self.user_id2, name=self.name2,
                                        value=self.user_value2)
        session.add(self.user_option_1)
        session.add(self.user_option_2)
        session.commit()

    def test_create_user_option(self):
        code, resp = self.client.user_options_create(
            self.user_id1, self.name2, self.value1)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value1)
        # trying to create an option with the same keys should result
        # in the record being updated
        code, resp = self.client.user_options_create(
            self.user_id1, self.name2, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)

        code, resp = self.client.user_options_create(
            self.user_id1, self.name1, {'value': 'some_str_not_json'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0046')

        code, resp = self.client.user_options_create(
            self.user_id1, self.name1, {'value': 123})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0046')

        code, resp = self.client.user_options_create(
            self.user_id1, self.name1, {'value': True})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0046')

        code, resp = self.client.user_options_create(
            self.user_id1, self.name1, {'value': 1.23})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0046')

        code, _ = self.client.user_options_create(
            'abcd', self.name1, self.value1)
        self.assertEqual(code, 404)

    def test_update_user_option(self):
        code, resp = self.client.user_options_update(
            self.user_id1, self.name1, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)
        # trying to update an option with nonexistent keys should result
        # in a record being created
        code, resp = self.client.user_options_update(
            self.user_id2, self.name1, self.value2)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value2)

        code, resp = self.client.user_options_update(
            self.user_id2, self.name1, {'value': 'some_str_not_json'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0046')

        code, resp = self.client.user_options_update(
            'abcd', self.name1, self.value1)
        self.assertEqual(code, 404)

    def test_get_user_option(self):
        code, resp = self.client.user_options_get(
            self.user_id1, self.name1)
        self.assertEqual(code, 200)
        self.assertEqual(resp, self.value1)
        code, resp = self.client.user_options_get(
            self.user_id1, self.name2)
        self.assertEqual(code, 200)
        self.assertEqual(resp.get('value'), '{}')
        code, _ = self.client.user_options_get('abcd', self.name1)
        self.assertEqual(code, 404)

    def test_query_access_token_rejected(self):
        # the token is only accepted in the Authorization header; passing
        # it as an access_token query argument must not authenticate and
        # must not let the caller reach another user's options
        base = '/auth/v2/users/%s/options/%s?access_token=%s'
        resp = self.fetch(base % (self.user_id2, self.name2,
                                  self.client.token))
        self.assertEqual(resp.code, 401)
        resp = self.fetch(base % (self.user_id2, self.name2,
                                  self.client.token), method='DELETE')
        self.assertEqual(resp.code, 401)
        # header auth still works for the caller's own options
        code, resp = self.client.user_options_get(self.user_id1, self.name1)
        self.assertEqual(code, 200)

    def test_list_user_option(self):
        code, resp = self.client.user_options_list(self.user_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 1)
        _, _ = self.client.user_options_create(
            self.user_id1, self.name2, self.value2)

        code, resp = self.client.user_options_list(self.user_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 2)
        self.assertEqual(resp['options'], ['default_option', 'new_option'])

        for invalid_value in [1234, 'invalid']:
            code, resp = self.client.user_options_list(
                self.user_id1, with_values=invalid_value)
            self.assertEqual(code, 400)
            self.assertEqual(resp['error']['error_code'], 'OA0063')

        code, resp = self.client.user_options_list(
            self.user_id1, with_values=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 2)
        self.assertEqual(resp['options'], [{
            'name': 'default_option',
            'value': '{"key1": "value1"}'
        }, {
            'name': 'new_option',
            'value': '{"key2": "value2"}'
        }])

        _, _ = self.client.user_options_delete(self.user_id2, self.name2)
        code, resp = self.client.user_options_list(self.user_id2)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 0)
        code, _ = self.client.user_options_list('abcd')
        self.assertEqual(code, 404)

    def test_delete_user_option(self):
        code, _ = self.client.user_options_delete(
            self.user_id1, self.name1)
        self.assertEqual(code, 204)
        code, resp = self.client.user_options_list(self.user_id1)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp.get('options')), 0)
        code, _ = self.client.user_options_delete(
            self.user_id1, self.name1)
        self.assertEqual(code, 404)
        code, _ = self.client.user_options_delete(
            'abcd', self.name1)
        self.assertEqual(code, 404)
