import uuid
from unittest.mock import patch

from auth.auth_server.controllers.auth_policy import AuthPolicyController
from auth.auth_server.models.models import (
    Action, ActionGroup, Assignment, AuthPolicy, Role, Type, User, gen_salt)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password

CONTEXT_URL = 'auth.auth_server.controllers.base.BaseController.get_context'
RES_INFO_URL = ('auth.auth_server.controllers.base.'
                'BaseController.get_resources_info')
PASSWORD = 'pass'


class TestAuthPolicies(TestAuthBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        self.org_id = str(uuid.uuid4())
        self.org2_id = str(uuid.uuid4())
        self.org3_id = str(uuid.uuid4())
        self.known_orgs = {self.org_id, self.org2_id, self.org3_id}
        session = self.db_session
        root_type = self.create_root_type()
        self.type_org = Type(id_=10, name='organization', parent=root_type)
        group = ActionGroup(name='organization')
        info_action = Action(name='INFO_ORGANIZATION', type_=self.type_org,
                             action_group=group)
        edit_action = Action(name='EDIT_PARTNER', type_=self.type_org,
                             action_group=group)
        self.member_role = Role(name='Member', type_=self.type_org,
                                lvl=self.type_org, description='member')
        self.manager_role = Role(name='Manager', type_=self.type_org,
                                 lvl=self.type_org, description='manager')
        for obj in [self.type_org, group, info_action, edit_action,
                    self.member_role, self.manager_role]:
            session.add(obj)
        self.member_role.assign_action(info_action)
        self.manager_role.assign_action(info_action)
        self.manager_role.assign_action(edit_action)
        session.commit()

        self.manager = self._create_user('manager@example.com')
        self.member = self._create_user('member@example.com')
        self._assign(self.manager, self.manager_role, self.org_id)
        self._assign(self.member, self.member_role, self.org_id)

        self.context_mock = patch(CONTEXT_URL).start()
        self.context_mock.side_effect = lambda res_type, uuid_: {
            'organization': uuid_}
        self.res_info_mock = patch(RES_INFO_URL).start()
        self.res_info_mock.side_effect = lambda payload: {
            res_id: {'name': 'org', 'type': res_type}
            for res_type, res_id in payload if res_id in self.known_orgs}

    def _create_user(self, email):
        salt = gen_salt()
        user = User(email, type_=self.type_org,
                    password=hash_password(PASSWORD, salt), salt=salt,
                    display_name=email, scope_id=self.org_id)
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def _assign(self, user, role, org_id, type_=None):
        assignment = Assignment(user, role, type_ or self.type_org, org_id)
        self.db_session.add(assignment)
        self.db_session.commit()
        return assignment

    def _login(self, user):
        # cluster secret issuance: a password login of a member of an
        # enforcing organization would return an MFA challenge instead
        self.client.token = None
        self.client.secret = self.cluster_secret
        code, token = self.client.token_get_user_id(user.id)
        self.assertEqual(code, 201)
        self.client.token = token['token']
        self.client.secret = None

    def _use_secret(self):
        self.client.token = None
        self.client.secret = self.cluster_secret

    def _create_policy(self, org_id=None, purpose='mfa',
                       scope_type='organization'):
        return self.client.post(self.client.auth_policies_url(), {
            'scope_type': scope_type,
            'scope_id': org_id or self.org_id,
            'purpose': purpose,
        })

    def _list_policies(self, org_id=None, scope_type='organization'):
        return self.client.get(self.client.auth_policies_url(), {
            'scope_type': scope_type, 'scope_id': org_id or self.org_id})

    # --- create ---

    def test_create_by_manager(self):
        self._login(self.manager)
        code, resp = self._create_policy()
        self.assertEqual(code, 201)
        self.assertEqual(resp['scope_type'], 'organization')
        self.assertEqual(resp['scope_id'], self.org_id)
        self.assertEqual(resp['purpose'], 'mfa')
        self.assertEqual(resp['deleted_at'], 0)
        self.assertIn('id', resp)

    def test_create_by_member_forbidden(self):
        self._login(self.member)
        code, resp = self._create_policy()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_create_other_organization_forbidden(self):
        self._login(self.manager)
        code, resp = self._create_policy(org_id=self.org2_id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_create_by_cluster_secret(self):
        self._use_secret()
        code, resp = self._create_policy()
        self.assertEqual(code, 201)
        self.assertEqual(resp['scope_id'], self.org_id)

    def test_create_bad_secret(self):
        self.client.token = None
        self.client.secret = 'wrong'
        code, resp = self._create_policy()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0006')

    def test_create_without_auth(self):
        self.client.token = None
        self.client.secret = None
        code, resp = self._create_policy()
        self.assertEqual(code, 401)
        self.assertEqual(resp['error']['error_code'], 'OA0062')

    def test_create_duplicate(self):
        self._use_secret()
        code, _ = self._create_policy()
        self.assertEqual(code, 201)
        code, resp = self._create_policy()
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OA0081')

    def test_create_after_delete(self):
        self._use_secret()
        _, policy = self._create_policy()
        code, _ = self.client.delete(
            self.client.auth_policies_url(policy['id']))
        self.assertEqual(code, 204)
        code, resp = self._create_policy()
        self.assertEqual(code, 201)
        self.assertNotEqual(resp['id'], policy['id'])

    def test_create_unknown_organization(self):
        self._use_secret()
        code, resp = self._create_policy(org_id=str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0028')

    def test_create_invalid_params(self):
        self._use_secret()
        for body, error_code in [
            ({'scope_id': self.org_id, 'purpose': 'mfa'}, 'OA0032'),
            ({'scope_type': 'organization', 'purpose': 'mfa'}, 'OA0032'),
            ({'scope_type': 'organization', 'scope_id': self.org_id},
             'OA0032'),
            ({'scope_type': 'organization', 'scope_id': self.org_id,
              'purpose': 'unknown'}, 'OA0060'),
            ({'scope_type': 'domain', 'scope_id': 'example.com',
              'purpose': 'mfa'}, 'OA0060'),
            ({'scope_type': 'organization', 'scope_id': 123,
              'purpose': 'mfa'}, 'OA0033'),
            ({'scope_type': 'organization', 'scope_id': self.org_id,
              'purpose': 'mfa', 'extra': 1}, 'OA0022'),
        ]:
            code, resp = self.client.post(
                self.client.auth_policies_url(), body)
            self.assertEqual(code, 400, body)
            self.assertEqual(resp['error']['error_code'], error_code, body)

    # --- list ---

    def test_list_by_member(self):
        self._use_secret()
        self._create_policy()
        self._create_policy(org_id=self.org2_id)
        self._login(self.member)
        code, resp = self._list_policies()
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['auth_policies']), 1)
        self.assertEqual(resp['auth_policies'][0]['scope_id'], self.org_id)

    def test_list_empty(self):
        self._login(self.member)
        code, resp = self._list_policies()
        self.assertEqual(code, 200)
        self.assertEqual(resp['auth_policies'], [])

    def test_list_other_organization_forbidden(self):
        self._login(self.member)
        code, resp = self._list_policies(org_id=self.org2_id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_list_by_cluster_secret(self):
        self._use_secret()
        self._create_policy(org_id=self.org2_id)
        code, resp = self._list_policies(org_id=self.org2_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['auth_policies']), 1)

    def test_list_excludes_deleted(self):
        self._use_secret()
        _, policy = self._create_policy()
        self.client.delete(self.client.auth_policies_url(policy['id']))
        code, resp = self._list_policies()
        self.assertEqual(code, 200)
        self.assertEqual(resp['auth_policies'], [])

    def test_list_invalid_params(self):
        self._use_secret()
        code, resp = self.client.get(self.client.auth_policies_url(),
                                     {'scope_type': 'organization'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0032')
        code, resp = self._list_policies(scope_type='domain')
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0060')

    # --- delete ---

    def test_delete_by_manager(self):
        self._use_secret()
        _, policy = self._create_policy()
        self._login(self.manager)
        code, _ = self.client.delete(
            self.client.auth_policies_url(policy['id']))
        self.assertEqual(code, 204)
        db_policy = self.db_session.query(AuthPolicy).get(policy['id'])
        self.db_session.refresh(db_policy)
        self.assertNotEqual(db_policy.deleted_at, 0)

    def test_delete_by_member_forbidden(self):
        self._use_secret()
        _, policy = self._create_policy()
        self._login(self.member)
        code, resp = self.client.delete(
            self.client.auth_policies_url(policy['id']))
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_delete_not_found(self):
        self._use_secret()
        code, resp = self.client.delete(
            self.client.auth_policies_url(str(uuid.uuid4())))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')

    def test_delete_twice(self):
        self._use_secret()
        _, policy = self._create_policy()
        url = self.client.auth_policies_url(policy['id'])
        code, _ = self.client.delete(url)
        self.assertEqual(code, 204)
        code, _ = self.client.delete(url)
        self.assertEqual(code, 404)

    def test_item_methods_not_allowed(self):
        self._use_secret()
        _, policy = self._create_policy()
        url = self.client.auth_policies_url(policy['id'])
        code, _ = self.client.get(url)
        self.assertEqual(code, 405)
        code, _ = self.client.patch(url, {'purpose': 'sso'})
        self.assertEqual(code, 405)

    # --- enforcement helpers ---

    @property
    def controller(self):
        return AuthPolicyController(self.db_session)

    def test_not_enforced_without_policy(self):
        self.assertFalse(self.controller.is_mfa_enforced_for_user(
            self.member.id))
        self.assertEqual(self.controller.get_enforcing_organizations(
            self.member.id), [])

    def test_multi_org_user_enforced_by_one(self):
        user = self._create_user('multi@example.com')
        self._assign(user, self.member_role, self.org_id)
        self._assign(user, self.member_role, self.org2_id)
        self._assign(user, self.manager_role, self.org3_id)
        self._use_secret()
        self._create_policy(org_id=self.org2_id)
        self.assertTrue(self.controller.is_mfa_enforced_for_user(user.id))
        self.assertEqual(self.controller.get_enforcing_organizations(
            user.id), [self.org2_id])
        # member is only in org_id, which does not enforce
        self.assertFalse(self.controller.is_mfa_enforced_for_user(
            self.member.id))

    def test_multiple_enforcing_organizations(self):
        user = self._create_user('multi@example.com')
        self._assign(user, self.member_role, self.org_id)
        self._assign(user, self.manager_role, self.org_id)
        self._assign(user, self.member_role, self.org2_id)
        self._use_secret()
        self._create_policy(org_id=self.org_id)
        self._create_policy(org_id=self.org2_id)
        self.assertEqual(self.controller.get_enforcing_organizations(
            user.id), sorted([self.org_id, self.org2_id]))

    def test_deleted_policy_not_counted(self):
        self._use_secret()
        _, policy = self._create_policy()
        self.assertTrue(self.controller.is_mfa_enforced_for_user(
            self.member.id))
        self.client.delete(self.client.auth_policies_url(policy['id']))
        self.assertFalse(self.controller.is_mfa_enforced_for_user(
            self.member.id))

    def test_sso_policy_does_not_enforce_mfa(self):
        self._use_secret()
        code, _ = self._create_policy(purpose='sso')
        self.assertEqual(code, 201)
        self.assertFalse(self.controller.is_mfa_enforced_for_user(
            self.member.id))

    def test_deleted_assignment_not_counted(self):
        user = self._create_user('former@example.com')
        assignment = self._assign(user, self.member_role, self.org2_id)
        self._use_secret()
        self._create_policy(org_id=self.org2_id)
        self.assertTrue(self.controller.is_mfa_enforced_for_user(user.id))
        assignment.deleted_at = 1
        self.db_session.commit()
        self.assertFalse(self.controller.is_mfa_enforced_for_user(user.id))

    def test_non_organization_assignment_not_counted(self):
        user = self._create_user('pool@example.com')
        type_pool = Type(id_=20, name='pool', parent=self.type_org)
        self.db_session.add(type_pool)
        self.db_session.commit()
        # pool id equal to an enforcing organization id must not match
        self._assign(user, self.member_role, self.org2_id, type_=type_pool)
        self._use_secret()
        self._create_policy(org_id=self.org2_id)
        self.assertFalse(self.controller.is_mfa_enforced_for_user(user.id))
