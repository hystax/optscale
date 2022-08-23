from unittest.mock import patch
from requests import HTTPError
from unittest import mock

from auth_server.models.models import (Type, User, Action, Role, Assignment,
                                       ActionGroup, gen_id)
from auth_server.models.models import gen_salt
from auth_server.tests.unittests.test_api_base import TestAuthBase
from auth_server.utils import hash_password

GET_CONTEXT = "auth_server.controllers.base.BaseController.get_context"


class TestAllowedActionsApi(TestAuthBase):
    def _create_user(self, name):
        salt = gen_salt()
        password = 'pass'
        user = User(
            '%s@test.com' % name, type=self.type_org,
            password=hash_password(password, salt),
            display_name=name, salt=salt, type_id=self.type_org.id)
        return user, password

    def get_allowed_actions(self, payload):
        return self.client.allowed_action_get(payload)

    def _mock_context_response(self, res_id):
        return {res_id: self.upper_hierarchy[res_id]}

    def setUp(self, version="v2"):
        super().setUp(version=version)
        self.root_res_id = gen_id()
        self.sub_res1_lvl1 = gen_id()
        self.sub_res2_lvl1 = gen_id()
        self.sub_res1_lvl2 = gen_id()
        self.sub_res2_lvl2 = gen_id()
        self.upper_hierarchy = {
            self.root_res_id: [self.root_res_id],
            self.sub_res1_lvl1: [
                self.root_res_id, self.sub_res1_lvl1
            ],
            self.sub_res2_lvl1: [
                self.root_res_id, self.sub_res2_lvl1
            ],
            self.sub_res1_lvl2: [
                self.root_res_id, self.sub_res1_lvl1, self.sub_res1_lvl2
            ],
            self.sub_res2_lvl2: [
                self.root_res_id, self.sub_res2_lvl1, self.sub_res2_lvl2
            ],
        }
        admin_user = self.create_root_user()
        session = self.db_session
        self.type_org = Type(id=10, name='partner', parent=admin_user.type)
        self.user1, self.pass1 = self._create_user('user1')
        self.user2, self.pass2 = self._create_user('user2')
        self.user3, self.pass3 = self._create_user('user3')
        action_group = ActionGroup(name='TEST_ACTION_GROUP')
        self.action1 = Action(name='ACTION1', type=self.type_org,
                              action_group=action_group)
        self.action2 = Action(name='ACTION2', type=self.type_org,
                              action_group=action_group)
        self.action3 = Action(name='ACTION3', type=self.type_org,
                              action_group=action_group)
        self.action4 = Action(name='ACTION4', type=self.type_org,
                              action_group=action_group)
        self.role1 = Role(
            name='ROLE1', type=self.type_org, lvl=self.type_org,
            description='ROLE1')
        self.role2 = Role(
            name='ROLE2', type=self.type_org, lvl=self.type_org,
            description='ROLE2')
        self.role3 = Role(
            name='ROLE3', type=self.type_org, lvl=self.type_org,
            description='ROLE3')
        session.add(self.type_org)
        session.add(self.user1)
        session.add(self.user2)
        session.add(self.action1)
        session.add(self.action2)
        session.add(self.action3)
        session.add(self.action4)
        session.add(self.role1)
        session.add(self.role2)
        session.add(self.role3)
        self.role1.assign_action(self.action1)
        self.role1.assign_action(self.action2)
        self.role2.assign_action(self.action3)
        self.role3.assign_action(self.action4)
        self.assignment_org = Assignment(
            self.user1, self.role1, self.type_org,
            self.root_res_id)
        self.assignment_lvl1 = Assignment(
            self.user1, self.role2, self.type_org,
            self.sub_res1_lvl1)
        self.assignment_lvl2 = Assignment(
            self.user1, self.role3, self.type_org,
            self.sub_res1_lvl2)
        self.assignment_lvl2_user2 = Assignment(
            self.user2, self.role3, self.type_org,
            self.sub_res1_lvl2)
        session.add(self.assignment_org)
        session.commit()
        self.client.token = self.get_token(self.user1.email, self.pass1)

    @patch(GET_CONTEXT)
    def test_allowed_actions_root_in_hierarchy(self, p_hierarchy):
        target_res = self.root_res_id
        p_hierarchy.return_value = self._mock_context_response(target_res)
        payload = (('partner', target_res), )
        code, allowed_actions = self.get_allowed_actions(payload)
        self.assertEqual(code, 200)
        self.assertEqual(len(allowed_actions), 1)
        self.assertEqual(set(allowed_actions[target_res]),
                         {self.action1.name, self.action2.name})

    @patch(GET_CONTEXT)
    def test_allowed_actions_lvl1_in_hierarchy(self, p_hierarchy):
        target_res = self.sub_res1_lvl1
        p_hierarchy.return_value = self._mock_context_response(target_res)
        payload = (('partner', target_res), )
        code, allowed_actions = self.get_allowed_actions(payload)
        self.assertEqual(code, 200)
        self.assertEqual(len(allowed_actions), 1)
        self.assertEqual(set(allowed_actions[target_res]),
                         {self.action1.name, self.action2.name,
                          self.action3.name})

    @patch(GET_CONTEXT)
    def test_allowed_actions_lvl2_in_hierarchy(self, p_hierarchy):
        target_res = self.sub_res1_lvl2
        p_hierarchy.return_value = self._mock_context_response(target_res)
        payload = (('partner', target_res), )
        code, allowed_actions = self.get_allowed_actions(payload)
        self.assertEqual(code, 200)
        self.assertEqual(len(allowed_actions), 1)
        self.assertEqual(set(allowed_actions[target_res]),
                         {self.action1.name, self.action2.name,
                          self.action3.name, self.action4.name})

    @patch(GET_CONTEXT)
    def test_allowed_actions_another_user(self, p_hierarchy):
        self.client.token = self.get_token(self.user2.email, self.pass2)
        target_res = self.sub_res1_lvl2
        p_hierarchy.return_value = self._mock_context_response(target_res)
        payload = (('partner', target_res), )
        code, allowed_actions = self.get_allowed_actions(payload)
        self.assertEqual(code, 200)
        self.assertEqual(len(allowed_actions), 1)
        self.assertEqual(set(allowed_actions[target_res]),
                         {self.action4.name})

    def test_allowed_actions_user_without_assignments(self):
        self.client.token = self.get_token(self.user3.email, self.pass3)
        target_res = self.sub_res1_lvl2
        payload = (('partner', target_res), )
        code, allowed_actions = self.get_allowed_actions(payload)
        self.assertEqual(code, 200)
        self.assertEqual(len(allowed_actions), 1)
        self.assertEqual(set(allowed_actions[target_res]), set())

    @patch(GET_CONTEXT)
    def test_allowed_actions_invalid_payload(self, p_get_context):
        err = HTTPError(mock.MagicMock(), 'bad request')
        err.response = mock.MagicMock(status_code=400, localized='OA0000')
        p_get_context.side_effect = err
        bad_uuid = '1234'
        payload = (('bad_type', bad_uuid), )
        code, resp = self.get_allowed_actions(payload)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0020')
        err.response = mock.Mock(status_code=404, localized='OA0000')
        payload = (('partner', bad_uuid), )
        code, resp = self.get_allowed_actions(payload)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0028')
        err.response = mock.MagicMock(status_code=400, localized='OA0000')
        err.response.json()['error'] = mock.MagicMock()
        exc = {
            'error_code': 'OE0472',
            'params': [
                payload[0][0], payload[0][1], 'pool', '1234'
            ]
        }
        err.response.json()['error'].__getitem__.side_effect = exc.__getitem__
        code, resp = self.get_allowed_actions(payload)
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0066')
