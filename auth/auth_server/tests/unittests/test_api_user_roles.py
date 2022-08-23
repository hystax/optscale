from auth_server.models.models import Type, User, Role, Assignment
from auth_server.models.models import gen_salt
from auth_server.tests.unittests.test_api_base import TestAuthBase
from auth_server.utils import hash_password


class TestUSerRolesApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)

        user_partner_salt = gen_salt()
        admin_user = self.create_root_user()
        self.partner1_scope_id = 'a5cb80ad-891d-4ec2-99de-ba4f20ba2c5d'
        self.partner2_scope_id = '640bae1c-2876-41e3-b6c3-1acb358dc387'
        session = self.db_session
        self.type_partner = Type(id=10, name='partner', parent=admin_user.type)
        self.user_partner_password = 'passwd!!111'
        self.user_partner1 = User(email='partner@company.com',
                                  password=hash_password(
                                      self.user_partner_password,
                                      user_partner_salt),
                                  display_name='Partner user',
                                  scope_id=self.partner1_scope_id,
                                  salt=user_partner_salt,
                                  type_id=self.type_partner.id)
        self.manager_role = Role(name='Manager', type=self.type_partner,
                                 lvl=self.type_partner,
                                 scope_id=self.partner1_scope_id,
                                 purpose='optscale_manager',
                                 description='Manager role')
        session.add(self.manager_role)
        self.assignment_manager = Assignment(self.user_partner1,
                                             self.manager_role,
                                             self.type_partner,
                                             self.partner1_scope_id)
        session.add(self.assignment_manager)
        self.user_partner2 = User(email='partner2@company.com',
                                  password=hash_password(
                                      self.user_partner_password,
                                      user_partner_salt),
                                  display_name='Partner2 user',
                                  scope_id=self.partner2_scope_id,
                                  salt=user_partner_salt,
                                  type_id=self.type_partner.id)
        self.engineer_role = Role(name='Engineer', type=self.type_partner,
                                  lvl=self.type_partner,
                                  purpose='optscale_engineer',
                                  scope_id=self.partner2_scope_id,
                                  description='Engineer role')
        session.add(self.engineer_role)
        self.assignment_engineer = Assignment(self.user_partner2,
                                              self.engineer_role,
                                              self.type_partner,
                                              self.partner2_scope_id)
        session.add(self.engineer_role)
        session.commit()

    def test_get_user_roles_base(self):
        code, resp = self.client.user_roles_get([self.user_partner1.id])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp), 1)
        obj = resp[0]
        self.assertEqual(obj['user_display_name'],
                         self.user_partner1.display_name)
        self.assertEqual(obj['assignment_type_id'],
                         self.assignment_manager.type_id)
        self.assertEqual(obj['user_email'], self.user_partner1.email)
        self.assertEqual(obj['role_name'], self.manager_role.name)
        self.assertEqual(obj['role_id'], self.manager_role.id)
        self.assertEqual(obj['role_purpose'], self.manager_role.purpose.value)
        self.assertEqual(obj['assignment_resource_id'],
                         self.assignment_manager.resource_id)
        self.assertEqual(obj['user_id'], self.user_partner1.id)
        self.assertEqual(obj['role_scope_id'], self.manager_role.scope_id)

    def test_get_user_roles_again(self):
        code, resp = self.client.user_roles_get([self.user_partner1.id,
                                                 self.user_partner2.id])
        self.assertEqual(code, 200)
        self.assertEqual(len(resp), 2)
        self.assertEqual(sorted(list(map(lambda x: x['user_id'], resp))),
                         sorted([self.user_partner1.id,
                                self.user_partner2.id]))
        self.assertEqual(sorted(list(map(lambda x: x['assignment_id'], resp))),
                         sorted([self.assignment_manager.id,
                                self.assignment_engineer.id]))
        self.assertEqual(sorted(list(map(lambda x: x['assignment_resource_id'],
                                         resp))),
                         sorted([self.assignment_manager.resource_id,
                                self.assignment_engineer.resource_id]))

    def test_get_all_user_roles(self):
        code, response = self.client.user_roles_get()
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 2)

    def test_get_user_roles_by_role_purpose(self):
        code, response = self.client.user_roles_get(
            role_purposes=[self.manager_role.purpose.value])
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        obj = response[0]
        self.assertEqual(obj['assignment_id'],
                         self.assignment_manager.id)

    def test_get_user_roles_complex(self):
        code, response = self.client.user_roles_get(
            role_purposes=[self.manager_role.purpose.value,
                           self.engineer_role.purpose.value],
            scope_ids=[self.partner2_scope_id]
        )
        self.assertEqual(code, 200)
        self.assertEqual(len(response), 1)
        obj = response[0]
        self.assertEqual(obj['assignment_id'],
                         self.assignment_engineer.id)
