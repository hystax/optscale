import uuid
from auth.auth_server.auth_token.token_store import TokenStore
from auth.auth_server.models.models import (Action, ActionGroup, Assignment,
                                            Type, Role, User)
from auth.auth_server.tests.unittests.test_model_base import TestModelBase


class TestActionResources(TestModelBase):

    def setUp(self):
        super().setUp()

        self.partner_scope_id = 'f9e3319d-ce9a-4fe3-b14c-b128f2229941'
        self.customer_scope_id = 'c2ee4829-f64c-4fa8-b147-bea6f65e4fee'

        session = self.db_session
        action_name_list_users = 'LIST_USERS'
        action_name_create_users = 'CREATE_USER'

        role_name = 'Manager'
        type_root = Type(name='root')
        type_partner = Type(name='partner')
        type_customer = Type(name='customer')
        user_action_group = ActionGroup(name='Manage users and assignments')

        self.user_partner = User(
            'partner@allcom.com', type_=type_partner, password='passwd',
            display_name='Partner user', scope_id=self.partner_scope_id,
            type_id=type_partner.id)
        self.user_customer = User(
            'customer@domain.com', type_=type_customer,
            display_name='Customer user', password='passwd',
            scope_id=self.customer_scope_id, type_id=type_customer.id)

        action_list_users = Action(name=action_name_list_users,
                                   type_=type_partner,
                                   action_group=user_action_group)

        action_create_users = Action(name=action_name_create_users,
                                     type_=type_customer,
                                     action_group=user_action_group)
        manager_role = Role(name=role_name, type_=type_partner,
                            lvl=type_partner,
                            scope_id=str(uuid.uuid4()),
                            description="Some manager action")

        assigment_partner_manager = Assignment(self.user_partner, manager_role,
                                               type_customer,
                                               self.user_partner.scope_id)
        assignment_customer_manager = Assignment(self.user_customer,
                                                 manager_role,
                                                 type_customer,
                                                 self.user_customer.scope_id)
        session.add(type_root)
        session.add(type_partner)
        session.add(type_customer)
        session.add(user_action_group)
        session.add(self.user_partner)
        session.add(self.user_customer)
        session.add(action_list_users)
        session.add(action_create_users)
        session.add(manager_role)
        manager_role.assign_action(action_create_users)
        manager_role.assign_action(action_list_users)
        session.add(assigment_partner_manager)
        session.add(assignment_customer_manager)
        session.commit()

    def test_action_resources_p1(self):
        action_resources = TokenStore(self.db_session).action_resources(
            self.user_partner, ['LIST_USERS', 'CREATE_USER'])
        self.assertEqual(len(action_resources), 2)
        self.assertEqual(len(list(filter(lambda x: x[0] in [
            self.partner_scope_id], action_resources))), 2)
