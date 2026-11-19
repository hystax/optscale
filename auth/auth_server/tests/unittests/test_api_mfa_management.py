import uuid
from unittest.mock import patch

import pyotp

from auth.auth_server.models.models import (
    Action, ActionGroup, Assignment, AuthPolicy, AuthPolicyPurpose,
    AuthPolicyScope, LoginChallenge, LoginChallengeState, MFAMethod, MFAType,
    Role, Token, Type, User, gen_salt)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import encrypt_mfa_secret, hash_password
from tools.optscale_time import utcnow_timestamp

CONTEXT_URL = 'auth.auth_server.controllers.base.BaseController.get_context'
HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
CONFIG_CLIENT = 'optscale_client.config_client.client.Client'
PASSWORD = 'pass'


class TestMfaManagement(TestAuthBase):
    """Status, update, removal and reset of MFA methods (MPT-26345)"""

    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        patch(f'{CONFIG_CLIENT}.product_name',
              return_value='FinOps for Cloud').start()
        patch(f'{CONFIG_CLIENT}.herald_url',
              return_value='http://herald').start()
        self.herald = patch(HERALD_CLIENT).start().return_value
        self.org_id = str(uuid.uuid4())
        self.org2_id = str(uuid.uuid4())
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
        self.user = self._create_user('user@example.com')
        self.manager = self._create_user('manager@example.com')
        self.member = self._create_user('member@example.com')
        self._assign(self.user, self.member_role, self.org_id)
        self._assign(self.manager, self.manager_role, self.org_id)
        self._assign(self.member, self.member_role, self.org_id)
        patch(CONTEXT_URL).start().side_effect = (
            lambda res_type, uuid_: {'organization': uuid_})
        self._login(self.user)

    # --- helpers ---

    def _create_user(self, email):
        salt = gen_salt()
        user = User(email, type_=self.type_org,
                    password=hash_password(PASSWORD, salt), salt=salt,
                    display_name=email, scope_id=self.org_id)
        user.verified = True
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def _assign(self, user, role, org_id):
        self.db_session.add(Assignment(user, role, self.type_org, org_id))
        self.db_session.commit()

    def _login(self, user):
        # cluster secret issuance: a password login of a user with methods
        # would return an MFA challenge instead
        self._use_secret()
        code, token = self.client.token_get_user_id(user.id)
        self.assertEqual(code, 201)
        self.client.token = token['token']
        self.client.secret = None
        return token['token']

    def _use_secret(self):
        self.client.token = None
        self.client.secret = self.cluster_secret

    def _add_method(self, user=None, type_=MFAType.totp, is_default=False,
                    confirmed=True, label='label', created_at=None):
        seed = pyotp.random_base32() if type_ == MFAType.totp else None
        method = MFAMethod(
            user_id=(user or self.user).id, type=type_,
            secret=encrypt_mfa_secret(seed) if seed else None,
            label=label, is_default=is_default)
        if confirmed:
            method.confirmed_at = utcnow_timestamp()
        if created_at is not None:
            method.created_at = created_at
        self.db_session.add(method)
        self.db_session.commit()
        return method

    def _enforce(self, org_id=None):
        self.db_session.add(AuthPolicy(
            scope_type=AuthPolicyScope.organization,
            scope_id=org_id or self.org_id, purpose=AuthPolicyPurpose.mfa))
        self.db_session.commit()

    def _method(self, method_id):
        # not get(): a dropped row still in the identity map would raise
        self.db_session.expire_all()
        return self.db_session.query(MFAMethod).filter(
            MFAMethod.id == method_id).one_or_none()

    def _active_methods(self, user=None):
        self.db_session.expire_all()
        return self.db_session.query(MFAMethod).filter(
            MFAMethod.user_id == (user or self.user).id,
            MFAMethod.deleted.is_(False)).all()

    def _status(self, user_id=None):
        return self.client.get(
            self.client.mfa_methods_url(user_id or self.user.id))

    def _patch(self, method_id, body, user_id=None):
        return self.client.patch(
            self.client.mfa_methods_url(user_id or self.user.id, method_id),
            body)

    def _delete(self, method_id, user_id=None):
        return self.client.delete(
            self.client.mfa_methods_url(user_id or self.user.id, method_id))

    def _reset(self, user_id=None):
        return self.client.delete(
            self.client.mfa_methods_url(user_id or self.user.id))

    # --- status ---

    def test_status_not_configured(self):
        code, resp = self._status()
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'methods': [], 'mfa_enforced': False,
            'enforcing_organizations': [], 'status': 'not_configured'})

    def test_status_configured(self):
        email = self._add_method(type_=MFAType.email, label='us***@x.com')
        totp = self._add_method(is_default=True)
        self._add_method(confirmed=False, label='pending')
        code, resp = self._status()
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'configured')
        self.assertFalse(resp['mfa_enforced'])
        # confirmed methods only, the default one first, no secrets
        self.assertEqual([m['id'] for m in resp['methods']],
                         [totp.id, email.id])
        self.assertTrue(resp['methods'][0]['is_default'])
        for method in resp['methods']:
            self.assertTrue(method['confirmed'])
            self.assertNotIn('secret', method)
            self.assertNotIn('last_used_step', method)

    def test_status_enforced(self):
        self._enforce()
        code, resp = self._status()
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'enforced')
        self.assertTrue(resp['mfa_enforced'])
        self.assertEqual(resp['enforcing_organizations'], [self.org_id])
        self.assertEqual(resp['methods'], [])
        # still enforced once a method is configured
        self._add_method(is_default=True)
        _, resp = self._status()
        self.assertEqual(resp['status'], 'enforced')
        self.assertEqual(len(resp['methods']), 1)

    def test_status_policy_on_other_organization(self):
        self._enforce(self.org2_id)
        _, resp = self._status()
        self.assertEqual(resp['status'], 'not_configured')
        self.assertEqual(resp['enforcing_organizations'], [])

    def test_status_by_secret(self):
        self._use_secret()
        code, resp = self._status()
        self.assertEqual(code, 200)
        self.assertEqual(resp['status'], 'not_configured')

    def test_status_foreign_token_forbidden(self):
        self._login(self.member)
        code, resp = self._status()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_status_unknown_user(self):
        self._use_secret()
        code, resp = self._status(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0024')

    def test_status_no_credentials(self):
        self.client.token = None
        code, _ = self._status()
        self.assertEqual(code, 401)

    # --- update ---

    def test_rename_totp(self):
        method = self._add_method(is_default=True, label='Phone')
        code, resp = self._patch(method.id, {'label': 'Old phone'})
        self.assertEqual(code, 200)
        self.assertEqual(resp['label'], 'Old phone')
        self.assertTrue(resp['is_default'])
        self.assertEqual(self._method(method.id).label, 'Old phone')

    def test_rename_pending_totp(self):
        method = self._add_method(confirmed=False, label='Phone')
        code, resp = self._patch(method.id, {'label': 'Tablet'})
        self.assertEqual(code, 200)
        self.assertEqual(resp['label'], 'Tablet')
        self.assertFalse(resp['confirmed'])

    def test_rename_email_rejected(self):
        method = self._add_method(type_=MFAType.email, is_default=True,
                                  label='us***@example.com')
        code, resp = self._patch(method.id, {'label': 'My mail'})
        self.assertEqual(code, 400)
        self.assertEqual(resp['error']['error_code'], 'OA0060')
        self.assertEqual(self._method(method.id).label, 'us***@example.com')

    def test_set_default(self):
        first = self._add_method(is_default=True, label='Phone')
        second = self._add_method(label='Tablet')
        code, resp = self._patch(second.id, {'is_default': True})
        self.assertEqual(code, 200)
        self.assertTrue(resp['is_default'])
        self.assertFalse(self._method(first.id).is_default)
        self.assertTrue(self._method(second.id).is_default)
        # exactly one default, listed first
        _, status = self._status()
        self.assertEqual([m['is_default'] for m in status['methods']],
                         [True, False])
        self.assertEqual(status['methods'][0]['id'], second.id)

    def test_set_default_already_default(self):
        method = self._add_method(is_default=True)
        code, resp = self._patch(method.id, {'is_default': True})
        self.assertEqual(code, 200)
        self.assertTrue(resp['is_default'])

    def test_set_default_with_label(self):
        self._add_method(is_default=True)
        second = self._add_method(label='Tablet')
        code, resp = self._patch(second.id,
                                 {'is_default': True, 'label': 'iPad'})
        self.assertEqual(code, 200)
        self.assertTrue(resp['is_default'])
        self.assertEqual(resp['label'], 'iPad')

    def test_set_default_pending_conflict(self):
        self._add_method(is_default=True)
        pending = self._add_method(confirmed=False)
        code, resp = self._patch(pending.id, {'is_default': True})
        self.assertEqual(code, 409)
        self.assertEqual(resp['error']['error_code'], 'OA0092')
        self.assertFalse(self._method(pending.id).is_default)

    def test_update_validation(self):
        method = self._add_method(is_default=True)
        for body, error_code in [
            # an empty body is OA0050 at the handler, so a null label
            ({'label': None}, 'OA0032'),
            ({'is_default': False}, 'OA0060'),
            ({'is_default': 'yes'}, 'OA0063'),
            ({'label': 1}, 'OA0033'),
            ({'label': 'x' * 257}, 'OA0048'),
            ({'label': '   '}, 'OA0065'),
            ({'type': 'email'}, 'OA0022'),
            ({'label': 'x', 'challenge_id': 'c'}, 'OA0022'),
        ]:
            code, resp = self._patch(method.id, body)
            self.assertEqual(code, 400, body)
            self.assertEqual(resp['error']['error_code'], error_code, body)
        self.assertEqual(self._method(method.id).label, 'label')

    def test_update_unknown_method(self):
        code, resp = self._patch(str(uuid.uuid4()), {'label': 'x'})
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')

    def test_update_method_of_other_user(self):
        other = self._add_method(user=self.member, is_default=True)
        code, resp = self._patch(other.id, {'label': 'x'})
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')
        self.assertEqual(self._method(other.id).label, 'label')

    def test_update_foreign_token_forbidden(self):
        method = self._add_method(is_default=True)
        self._login(self.member)
        code, resp = self._patch(method.id, {'label': 'x'})
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')

    def test_update_by_secret(self):
        method = self._add_method(is_default=True)
        self._use_secret()
        code, resp = self._patch(method.id, {'label': 'Support renamed'})
        self.assertEqual(code, 200)
        self.assertEqual(resp['label'], 'Support renamed')

    def test_update_removed_method(self):
        method = self._add_method(is_default=True)
        self._delete(method.id)
        code, resp = self._patch(method.id, {'label': 'x'})
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')

    # --- delete ---

    def test_delete_non_default(self):
        default = self._add_method(is_default=True)
        other = self._add_method(type_=MFAType.email)
        code, _ = self._delete(other.id)
        self.assertEqual(code, 204)
        self.assertTrue(self._method(other.id).deleted)
        self.assertTrue(self._method(default.id).is_default)
        _, status = self._status()
        self.assertEqual([m['id'] for m in status['methods']], [default.id])

    def test_delete_default_promotes_oldest(self):
        now = utcnow_timestamp()
        default = self._add_method(is_default=True, created_at=now - 300)
        oldest = self._add_method(label='oldest', created_at=now - 200)
        newest = self._add_method(label='newest', created_at=now - 100)
        code, _ = self._delete(default.id)
        self.assertEqual(code, 204)
        self.assertTrue(self._method(default.id).deleted)
        self.assertFalse(self._method(default.id).is_default)
        self.assertTrue(self._method(oldest.id).is_default)
        self.assertFalse(self._method(newest.id).is_default)
        _, status = self._status()
        self.assertEqual(status['methods'][0]['id'], oldest.id)

    def test_delete_last_not_enforced(self):
        method = self._add_method(is_default=True)
        code, _ = self._delete(method.id)
        self.assertEqual(code, 204)
        _, status = self._status()
        self.assertEqual(status['status'], 'not_configured')

    def test_delete_last_enforced_forbidden(self):
        self._enforce()
        first = self._add_method(is_default=True)
        second = self._add_method(label='second')
        code, _ = self._delete(first.id)
        self.assertEqual(code, 204)
        self.assertTrue(self._method(second.id).is_default)
        code, resp = self._delete(second.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0091')
        self.assertFalse(self._method(second.id).deleted)
        _, status = self._status()
        self.assertEqual([m['id'] for m in status['methods']], [second.id])

    def test_delete_last_enforced_by_other_organization(self):
        # the policy of any organization of the user counts
        self._assign(self.user, self.member_role, self.org2_id)
        self._enforce(self.org2_id)
        method = self._add_method(is_default=True)
        code, resp = self._delete(method.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0091')

    def test_delete_pending_while_enforced(self):
        # a pending enrollment is not a configured method: always removable
        self._enforce()
        self._add_method(is_default=True)
        pending = self._add_method(confirmed=False)
        code, _ = self._delete(pending.id)
        self.assertEqual(code, 204)
        self.assertIsNone(self._method(pending.id))

    def test_delete_pending_dropped(self):
        pending = self._add_method(confirmed=False)
        code, _ = self._delete(pending.id)
        self.assertEqual(code, 204)
        # never confirmed: the row is removed, not soft-deleted
        self.assertIsNone(self._method(pending.id))

    def test_delete_twice(self):
        method = self._add_method(is_default=True)
        self._delete(method.id)
        code, resp = self._delete(method.id)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')

    def test_delete_method_of_other_user(self):
        other = self._add_method(user=self.member, is_default=True)
        code, resp = self._delete(other.id)
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0003')
        self.assertFalse(self._method(other.id).deleted)

    def test_delete_foreign_token_forbidden(self):
        method = self._add_method(is_default=True)
        self._login(self.member)
        code, resp = self._delete(method.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self.assertFalse(self._method(method.id).deleted)

    def test_delete_by_secret(self):
        method = self._add_method(is_default=True)
        self._use_secret()
        code, _ = self._delete(method.id)
        self.assertEqual(code, 204)
        self.assertTrue(self._method(method.id).deleted)

    def test_removed_method_cannot_be_enrolled_type_conflict(self):
        # a removed e-mail method does not block a new enrollment
        email = self._add_method(type_=MFAType.email, is_default=True)
        self._delete(email.id)
        code, _ = self.client.post(self.client.mfa_methods_url(self.user.id),
                                   {'type': 'email'})
        self.assertEqual(code, 201)

    # --- reset ---

    def _open_challenge(self, user=None):
        challenge = LoginChallenge(
            user_id=(user or self.user).id,
            state=LoginChallengeState.mfa_required,
            expires_at=utcnow_timestamp() + 300, attempts=0)
        self.db_session.add(challenge)
        self.db_session.commit()
        return challenge

    def _tokens(self, user=None):
        return self.db_session.query(Token).filter(
            Token.user_id == (user or self.user).id).count()

    def test_reset_by_manager(self):
        totp = self._add_method(is_default=True)
        email = self._add_method(type_=MFAType.email)
        # the id now: the dropped row cannot be loaded after expire_all
        pending_id = self._add_method(confirmed=False).id
        challenge = self._open_challenge()
        user_token = self.client.token
        self.assertEqual(self._tokens(), 1)
        self._login(self.manager)
        code, _ = self._reset()
        self.assertEqual(code, 204)
        # confirmed methods kept as history, the pending one dropped
        self.assertTrue(self._method(totp.id).deleted)
        self.assertFalse(self._method(totp.id).is_default)
        self.assertTrue(self._method(email.id).deleted)
        self.assertIsNone(self._method(pending_id))
        self.assertEqual(self._active_methods(), [])
        # sessions ended, challenges revoked
        self.assertEqual(self._tokens(), 0)
        self.assertTrue(self.db_session.query(LoginChallenge).get(
            challenge.id).deleted)
        self.client.token = user_token
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 401)
        # the manager's own session is untouched
        self.assertEqual(self._tokens(self.manager), 1)
        self._use_secret()
        _, status = self._status()
        self.assertEqual(status['status'], 'not_configured')

    def test_reset_by_secret(self):
        self._add_method(is_default=True)
        self._use_secret()
        code, _ = self._reset()
        self.assertEqual(code, 204)
        self.assertEqual(self._active_methods(), [])
        self.assertEqual(self._tokens(), 0)

    def test_reset_without_methods(self):
        self._login(self.manager)
        code, _ = self._reset()
        self.assertEqual(code, 204)
        self.assertEqual(self._tokens(), 0)

    def test_reset_by_member_forbidden(self):
        method = self._add_method(is_default=True)
        self._login(self.member)
        code, resp = self._reset()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self.assertFalse(self._method(method.id).deleted)
        self.assertEqual(self._tokens(), 1)

    def test_reset_by_owner_forbidden(self):
        # the owner removes methods one by one, the reset is a manager
        # (or support) operation
        method = self._add_method(is_default=True)
        code, resp = self._reset()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self.assertFalse(self._method(method.id).deleted)

    def test_reset_by_manager_of_other_organization(self):
        method = self._add_method(is_default=True)
        outsider = self._create_user('outsider@example.com')
        self._assign(outsider, self.manager_role, self.org2_id)
        self._login(outsider)
        code, resp = self._reset()
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self.assertFalse(self._method(method.id).deleted)

    def test_reset_by_manager_of_second_organization(self):
        # a manager of any organization of the user may reset
        self._assign(self.user, self.member_role, self.org2_id)
        manager2 = self._create_user('manager2@example.com')
        self._assign(manager2, self.manager_role, self.org2_id)
        self._add_method(is_default=True)
        self._login(manager2)
        code, _ = self._reset()
        self.assertEqual(code, 204)
        self.assertEqual(self._active_methods(), [])

    def test_reset_user_without_organizations(self):
        loner = self._create_user('loner@example.com')
        self._add_method(user=loner, is_default=True)
        self._login(self.manager)
        code, resp = self._reset(loner.id)
        self.assertEqual(code, 403)
        self.assertEqual(resp['error']['error_code'], 'OA0012')
        self._use_secret()
        code, _ = self._reset(loner.id)
        self.assertEqual(code, 204)
        self.assertEqual(self._active_methods(loner), [])

    def test_reset_unknown_user(self):
        self._use_secret()
        code, resp = self._reset(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OA0024')

    def test_reset_then_password_only_login(self):
        self._add_method(is_default=True)
        self._use_secret()
        self._reset()
        self.client.secret = None
        code, resp = self.client.token_get('user@example.com', PASSWORD)
        self.assertEqual(code, 201)
        self.assertIn('token', resp)

    def test_reset_enforced_user_enrolls_again(self):
        self._enforce()
        self._add_method(is_default=True)
        self._login(self.manager)
        code, _ = self._reset()
        self.assertEqual(code, 204)
        self.client.token = None
        code, resp = self.client.token_get('user@example.com', PASSWORD)
        self.assertEqual(code, 202)
        self.assertEqual(resp['state'], 'enrollment_required')

    def test_reset_body_ignored_for_auth(self):
        # challenge_id in the body is not a credential for the reset
        method = self._add_method(is_default=True)
        challenge = self._open_challenge()
        self.client.token = None
        code, resp = self.client.delete(
            self.client.mfa_methods_url(self.user.id) +
            f'?challenge_id={challenge.id}')
        self.assertEqual(code, 401)
        self.assertFalse(self._method(method.id).deleted)
        self.assertIsNotNone(resp)
