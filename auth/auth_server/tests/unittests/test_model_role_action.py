from auth.auth_server.tests.unittests.test_model_base import TestModelBase
from auth.auth_server.models.models import *


class TestType(TestModelBase):

    def setUp(self):
        super().setUp()

    def test_role_action_assign(self):
        session = self.db_session
        type_name_root = 'root'
        action_name_create_customer = 'CREATE_CUSTOMER'
        action_name_run_cs = 'RUN_CS'
        role_name = 'admin'
        type_root = Type(id=0, name=type_name_root)
        admin_action_group = ActionGroup(name='admin')
        cs_action_group = ActionGroup(name='cloudsite')
        action_create_customer = Action(name=action_name_create_customer,
                                        type=type_root,
                                        action_group=admin_action_group)
        action_run_cs = Action(name=action_name_run_cs, type=type_root,
                               action_group=cs_action_group)
        role_admin = Role(name=role_name, type=type_root, lvl=type_root,
                          scope_id=str(uuid.uuid4()),
                          description="Some admin action")
        session.add(type_root)
        session.add(admin_action_group)
        session.add(cs_action_group)
        session.add(action_create_customer)
        session.add(role_admin)
        session.add(action_run_cs)
        role_admin.assign_action(action_create_customer)
        role_admin.assign_action(action_run_cs)
        session.commit()
        self.assertTrue(all(map(
            lambda x: x.name in [action_name_create_customer, action_name_run_cs],
            role_admin.actions)))
        role_admin.remove_action(action_create_customer)
        session.add(role_admin)
        session.commit()
        self.assertTrue(all(map(lambda x: x.name in [action_name_run_cs],
                                role_admin.actions)))
