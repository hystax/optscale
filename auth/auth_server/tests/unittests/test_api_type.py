from auth_server.models.models import Type
from auth_server.tests.unittests.test_api_base import TestAuthBase


class TestTypeApi(TestAuthBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        self.admin_user_password = 'toor'
        self.admin_user = self.create_root_user(
            password=self.admin_user_password)
        session = self.db_session
        name_partner = 'partner'
        name_customer = 'customer'
        name_group = 'group'
        self.type_partner = Type(name=name_partner,
                                 parent=self.admin_user.type)
        self.type_customer = Type(name=name_customer, parent=self.type_partner)
        self.type_group = Type(name=name_group, parent=self.type_customer)
        session.add(self.admin_user)
        session.add(self.type_partner)
        session.add(self.type_customer)
        session.add(self.type_group)
        session.commit()

        self.client.token = self.get_token(self.admin_user.email,
                                           self.admin_user_password)

    def test_type_get(self):
        _, types = self.client.type_list()
        for type in types:
            type_id = type.get('id')
            type_name = type.get('name')
            code, type = self.client.type_get(type_id)
            self.assertEqual(code, 200)
            self.assertEqual(type_id, type.get('id'))
            self.assertEqual(type_name, type.get('name'))

    def test_type_list(self):
        code, types = self.client.type_list()
        self.assertEqual(code, 200)
        self.assertEqual(len(types), 4)
