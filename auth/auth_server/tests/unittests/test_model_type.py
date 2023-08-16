from auth.auth_server.tests.unittests.test_model_base import TestModelBase
from auth.auth_server.models.models import *

from auth.auth_server.models.exceptions import InvalidTreeException


class TestType(TestModelBase):

    def setUp(self):
        super().setUp()

    def test_type_create(self):
        session = self.db_session
        name = 'root'
        type_root = Type(name=name)
        session.add(type_root)
        session.commit()
        types = session.query(Type).all()
        self.assertEqual(len(types), 1)
        self.assertEqual(types[0].name, name)

    def test_type_create_1_lvl_tree(self):
        session = self.db_session
        name_root = 'root'
        name_partner = 'partner'
        type_root = Type(name=name_root)
        type_partner = Type(name=name_partner, parent=type_root)
        session.add(type_root)
        session.add(type_partner)
        session.commit()
        self.assertEquals(type_partner.parent, type_root)
        self.assertEquals(type_root.children[0], type_partner)
        types = session.query(Type).all()
        self.assertEquals(len(types), 2)

    def test_type_create_3_lvl_tree(self):
        session = self.db_session
        name_root = 'root'
        name_partner = 'partner'
        name_customer = 'customer'
        name_group = 'group'
        type_root = Type(name=name_root)
        type_partner = Type(name=name_partner, parent=type_root)
        type_customer = Type(name=name_customer, parent=type_partner)
        type_group = Type(name=name_group, parent=type_customer)
        session.add(type_root)
        session.add(type_partner)
        session.add(type_customer)
        session.add(type_group)
        session.commit()
        self.assertEqual(len(type_root.child_tree), 3)
        self.assertTrue(all(map(lambda x: x.name in [
            name_partner, name_customer, name_group], type_root.child_tree)))
        self.assertTrue(all(map(lambda x: x.name in [
            name_partner, name_root, name_customer], type_group.parent_tree)))
        self.assertEqual(len(type_customer.parent_tree), 2)
        self.assertEqual(len(type_group.child_tree), 0)
        self.assertEqual(len(type_root.parent_tree), 0)

    def test_type_children_invalid_tree(self):
        """
        Test invalid tree case
        :return:
        """
        session = self.db_session
        name_root = 'root'
        name_partner = 'partner'
        name_invalid = 'invalid'
        type_root = Type(name=name_root)
        type_partner = Type(name=name_partner, parent=type_root)
        type_invalid = Type(name=name_invalid, parent=type_root)
        session.add(type_root)
        session.add(type_partner)
        session.add(type_invalid)
        session.commit()
        with self.assertRaises(InvalidTreeException):
            _ = type_root.child_tree
