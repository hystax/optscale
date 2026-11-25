import logging
import re
import time
import uuid
from datetime import timedelta
from unittest.mock import patch

import pyotp
from freezegun import freeze_time
from pymacaroons import Macaroon

from auth.auth_server.models.models import (
    Action, ActionGroup, Assignment, LoginChallenge, MFAMethod, Role, Type,
    User, gen_salt)
from auth.auth_server.tests.unittests.test_api_base import TestAuthBase
from auth.auth_server.utils import hash_password
from tools.optscale_time import utcnow

CONTEXT_URL = 'auth.auth_server.controllers.base.BaseController.get_context'
RES_INFO_URL = ('auth.auth_server.controllers.base.'
                'BaseController.get_resources_info')
HERALD_CLIENT = ('auth.auth_server.controllers.verification_code.'
                 'HeraldClient')
CONFIG_CLIENT = 'optscale_client.config_client.client.Client'
PASSWORD = 'toor'
USER_EMAIL = 'user@example.com'
MANAGER_EMAIL = 'manager@example.com'
TOTP_PERIOD = 30
UUID_RE = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}')


class TestMfaScenarios(TestAuthBase):
    """
    End-to-end scenarios of the MFA feature (MPT-26350): the flows of the
    TDR from enrollment through login to reset, as the UI and the other
    services drive them (auth_client methods, real credentials), checking
    the security properties that are easy to break between the pieces:
    single-use codes, attempt limits, enforcement across organizations, no
    bypass through the password-recovery login, no secrets in the logs.
    """

    def setUp(self, version='v2'):
        super().setUp(version)
        self.cluster_secret = self.client.secret
        self._start_patch(f'{CONFIG_CLIENT}.product_name',
                          return_value='FinOps for Cloud')
        self._start_patch(f'{CONFIG_CLIENT}.herald_url',
                          return_value='http://herald')
        self.herald = self._start_patch(HERALD_CLIENT).return_value
        # organization A (the user and the manager), organization B (the
        # user only): known to the (mocked) rest api
        self.org_a = str(uuid.uuid4())
        self.org_b = str(uuid.uuid4())
        self._start_patch(CONTEXT_URL, side_effect=lambda res_type, uuid_: {
            'organization': uuid_})
        self._start_patch(RES_INFO_URL, side_effect=lambda payload: {
            res_id: {'name': 'org', 'type': res_type}
            for res_type, res_id in payload
            if res_id in (self.org_a, self.org_b)})
        session = self.db_session
        self.type_org = Type(id_=10, name='organization',
                             parent=self.create_root_type())
        group = ActionGroup(name='organization')
        info_action = Action(name='INFO_ORGANIZATION', type_=self.type_org,
                             action_group=group)
        edit_action = Action(name='EDIT_PARTNER', type_=self.type_org,
                             action_group=group)
        self.member_role = Role(name='Member', type_=self.type_org,
                                lvl=self.type_org, description='member')
        self.manager_role = Role(name='Manager', type_=self.type_org,
                                 lvl=self.type_org, description='manager')
        session.add_all([self.type_org, group, info_action, edit_action,
                         self.member_role, self.manager_role])
        self.member_role.assign_action(info_action)
        self.manager_role.assign_action(info_action)
        self.manager_role.assign_action(edit_action)
        session.commit()
        self.user = self._create_user(USER_EMAIL)
        self.manager = self._create_user(MANAGER_EMAIL)
        self._assign(self.user, self.member_role, self.org_a)
        self._assign(self.user, self.member_role, self.org_b)
        self._assign(self.manager, self.manager_role, self.org_a)
        self._no_credential()

    # --- fixtures ---

    def _start_patch(self, target, **kwargs):
        patcher = patch(target, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def _create_user(self, email):
        salt = gen_salt()
        user = User(email, type_=self.type_org,
                    password=hash_password(PASSWORD, salt), salt=salt,
                    display_name=email, scope_id=self.org_a)
        user.verified = True
        self.db_session.add(user)
        self.db_session.commit()
        return user

    def _assign(self, user, role, org_id):
        self.db_session.add(Assignment(user, role, self.type_org, org_id))
        self.db_session.commit()

    # --- credentials ---

    def _no_credential(self):
        """Sign in, challenge completion and enrollment with a challenge"""
        self.client.token = None
        self.client.secret = None

    def _use_token(self, token):
        self.client.secret = None
        self.client.token = token

    def _use_secret(self):
        self.client.token = None
        self.client.secret = self.cluster_secret

    # --- flows ---

    def _sign_in(self, email=USER_EMAIL, **credential):
        self._no_credential()
        credential = credential or {'password': PASSWORD}
        return self.client.token_get(email, **credential)

    def _complete(self, challenge_id, code, method_id=None):
        self._no_credential()
        return self.client.token_get_by_challenge(challenge_id, code,
                                                  method_id)

    def _enforce(self, org_id):
        self._use_secret()
        code, policy = self.client.auth_policy_create('organization', org_id,
                                                      'mfa')
        self.assertEqual(code, 201, policy)
        return policy['id']

    def _status(self):
        self._use_secret()
        code, status = self.client.mfa_methods_get(self.user.id)
        self.assertEqual(code, 200, status)
        return status

    def _enroll_totp(self, token, label='Phone'):
        """Enrollment as the Security page does it, with the user's token.
        Returns (method id, authenticator seed)"""
        self._use_token(token)
        code, method = self.client.mfa_method_create(self.user.id, 'totp',
                                                     label=label)
        self.assertEqual(code, 201, method)
        code, confirmed = self.client.mfa_method_confirm(
            self.user.id, method['id'], self._totp(method['secret']))
        self.assertEqual(code, 200, confirmed)
        self.assertTrue(confirmed['confirmed'])
        return method['id'], method['secret']

    def _enroll_email(self, token):
        self._use_token(token)
        code, method = self.client.mfa_method_create(self.user.id, 'email')
        self.assertEqual(code, 201, method)
        code, confirmed = self.client.mfa_method_confirm(
            self.user.id, method['id'], self._sent_code())
        self.assertEqual(code, 200, confirmed)
        return method['id']

    def _password_token(self, email=USER_EMAIL):
        """A user without method signs in with the password only"""
        code, token = self._sign_in(email)
        self.assertEqual(code, 201, token)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:none'])
        return token['token']

    # --- codes ---

    @staticmethod
    def _totp(seed, steps=0):
        """The code of the current step, or of a neighbour (the server
        accepts one step on each side, a step is accepted once)"""
        return pyotp.TOTP(seed).at(time.time() + steps * TOTP_PERIOD)

    def _sent_code(self, call_idx=-1):
        kwargs = self.herald.email_send.call_args_list[call_idx].kwargs
        return kwargs['template_params']['texts']['code']

    @staticmethod
    def _wrong(code):
        return f'{(int(code) + 1) % 1_000_000:06d}'

    # --- inspection ---

    @staticmethod
    def _mfa_caveat(token):
        caveats = [c.caveat_id for c in
                   Macaroon.deserialize(token).first_party_caveats()]
        return [c for c in caveats if c.startswith('mfa:')]

    def _rows(self, model, user=None):
        self.db_session.expire_all()
        return self.db_session.query(model).filter(
            model.user_id == (user or self.user).id).all()

    def _assert_error(self, response, status, error_code):
        code, body = response
        self.assertEqual(code, status, body)
        self.assertEqual(body['error']['error_code'], error_code, body)
        return body

    # --- 1. authenticator app: enrollment, then two-step sign in ---

    def test_totp_enrollment_then_login(self):
        token = self._password_token()
        method_id, seed = self._enroll_totp(token)
        self._use_token(token)
        code, status = self.client.mfa_methods_get(self.user.id)
        self.assertEqual(code, 200)
        self.assertEqual(status['status'], 'configured')
        self.assertEqual([m['id'] for m in status['methods']], [method_id])

        code, challenge = self._sign_in()
        self.assertEqual(code, 202, challenge)
        self.assertEqual(challenge['state'], 'mfa_required')
        self.assertEqual(challenge['default_method_id'], method_id)
        self.assertFalse(challenge['code_sent'])
        self.assertEqual(challenge['attempts_left'], 5)
        self.assertNotIn('token', challenge)
        # the step after the one used for the confirmation
        code, token = self._complete(challenge['challenge_id'],
                                     self._totp(seed, 1))
        self.assertEqual(code, 201, token)
        self.assertEqual(token['user_id'], self.user.id)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:totp'])
        # a real session
        self._use_token(token['token'])
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 200)
        # the challenge is single use
        self._assert_error(
            self._complete(challenge['challenge_id'], self._totp(seed, 1)),
            404, 'OA0085')

    # --- 2. enforced organization, user without method ---

    def test_enforced_user_enrolls_during_login(self):
        self._enforce(self.org_a)
        self.assertEqual(self._status()['status'], 'enforced')
        code, challenge = self._sign_in()
        self.assertEqual(code, 202, challenge)
        self.assertEqual(challenge['state'], 'enrollment_required')
        self.assertEqual(challenge['methods'], [])
        challenge_id = challenge['challenge_id']
        # no completion without a method, no enrollment with a wrong user
        self._assert_error(self._complete(challenge_id, '123456'),
                           403, 'OA0088')
        self._no_credential()
        self._assert_error(self.client.mfa_method_create(
            self.manager.id, 'totp', label='Phone',
            challenge_id=challenge_id), 403, 'OA0012')
        code, method = self.client.mfa_method_create(
            self.user.id, 'totp', label='Phone', challenge_id=challenge_id)
        self.assertEqual(code, 201, method)
        self.assertFalse(method['confirmed'])
        code, result = self.client.mfa_method_confirm(
            self.user.id, method['id'], self._totp(method['secret']),
            challenge_id=challenge_id)
        self.assertEqual(code, 201, result)
        self.assertTrue(result['method']['confirmed'])
        self.assertTrue(result['method']['is_default'])
        self.assertEqual(self._mfa_caveat(result['token']['token']),
                         ['mfa:totp'])
        self._use_token(result['token']['token'])
        code, status = self.client.mfa_methods_get(self.user.id)
        self.assertEqual(code, 200)
        self.assertEqual(status['status'], 'enforced')
        self.assertEqual(len(status['methods']), 1)
        # the challenge is consumed, the next sign in verifies the method
        self._assert_error(self.client.mfa_method_create(
            self.user.id, 'totp', label='Tablet', challenge_id=challenge_id
        ), 404, 'OA0085')
        code, challenge = self._sign_in()
        self.assertEqual(code, 202)
        self.assertEqual(challenge['state'], 'mfa_required')

    # --- 3. e-mail as default: code with the challenge, resend, throttle --

    def test_email_default_code_sent_resend_and_throttle(self):
        now = utcnow()
        with freeze_time(now):
            method_id = self._enroll_email(self._password_token())
        self.assertEqual(self.herald.email_send.call_count, 1)
        with freeze_time(now + timedelta(minutes=2)):
            code, challenge = self._sign_in()
            self.assertEqual(code, 202, challenge)
            self.assertTrue(challenge['code_sent'])
            self.assertEqual(challenge['default_method_id'], method_id)
            self.assertEqual(self.herald.email_send.call_count, 2)
            first_code = self._sent_code()
            # "Resend" right away: one code per minute
            self._assert_error(self.client.login_challenge_code_send(
                challenge['challenge_id']), 403, 'OA0072')
            self.assertEqual(self.herald.email_send.call_count, 2)
        with freeze_time(now + timedelta(minutes=3, seconds=1)):
            code, _ = self.client.login_challenge_code_send(
                challenge['challenge_id'], method_id)
            self.assertEqual(code, 204)
            self.assertEqual(self.herald.email_send.call_count, 3)
            second_code = self._sent_code()
            self.assertNotEqual(first_code, second_code)
            self._assert_error(self.client.login_challenge_code_send(
                challenge['challenge_id']), 403, 'OA0072')
            # the e-mails say what the code is for
            subjects = [c.args[1] for c in
                        self.herald.email_send.call_args_list]
            self.assertIn('confirm your e-mail', subjects[0])
            self.assertIn('sign-in code', subjects[1])
            self.assertIn('sign-in code', subjects[2])
            # the first code was replaced by the resend: one attempt lost
            self._assert_error(
                self._complete(challenge['challenge_id'], first_code,
                               method_id), 403, 'OA0086')
            code, token = self._complete(challenge['challenge_id'],
                                         second_code, method_id)
        self.assertEqual(code, 201, token)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:email'])

    # --- 4. attempt limit and replay protection ---

    def test_lockout_after_five_failures_and_totp_replay(self):
        _, seed = self._enroll_totp(self._password_token())
        _, challenge = self._sign_in()
        wrong = self._wrong(self._totp(seed))
        for left in [4, 3, 2, 1]:
            body = self._assert_error(
                self._complete(challenge['challenge_id'], wrong),
                403, 'OA0086')
            self.assertEqual(body['error']['params'], [left])
        self._assert_error(self._complete(challenge['challenge_id'], wrong),
                           403, 'OA0087')
        # locked: even the right code is refused, a new sign in is needed
        self._assert_error(
            self._complete(challenge['challenge_id'], self._totp(seed, 1)),
            404, 'OA0085')

        _, challenge = self._sign_in()
        self.assertEqual(challenge['attempts_left'], 5)
        used = self._totp(seed, 1)
        code, _ = self._complete(challenge['challenge_id'], used)
        self.assertEqual(code, 201)
        # the same code (still within the time window) on a new sign in
        _, challenge = self._sign_in()
        self._assert_error(self._complete(challenge['challenge_id'], used),
                           403, 'OA0086')

    # --- 5. enforcement across organizations ---

    def test_enforcement_follows_the_organizations(self):
        # the user is in A (enforced) and B (not): enforced
        policy_id = self._enforce(self.org_a)
        self.assertEqual(self._status()['status'], 'enforced')
        code, challenge = self._sign_in()
        self.assertEqual(code, 202)
        self.assertEqual(challenge['state'], 'enrollment_required')
        # the manager of A is enforced too, a user of B only is not
        code, challenge = self._sign_in(MANAGER_EMAIL)
        self.assertEqual(code, 202)
        self.assertEqual(challenge['state'], 'enrollment_required')
        member_b = self._create_user('b-only@example.com')
        self._assign(member_b, self.member_role, self.org_b)
        code, _ = self._sign_in(member_b.email)
        self.assertEqual(code, 201)

        # with a method (enrolled from a service session: the password sign
        # in of an enforced user returns a challenge, not a token), the
        # last one cannot be removed while enforced
        method_id, _ = self._enroll_totp(self._secret_token())
        self.assertEqual(self._status()['status'], 'enforced')
        self._use_secret()
        self._assert_error(self.client.mfa_method_delete(
            self.user.id, method_id), 403, 'OA0091')

        # the policy of A removed: MFA is optional again
        self._use_secret()
        code, _ = self.client.auth_policy_delete(policy_id)
        self.assertEqual(code, 204)
        self.assertEqual(self._status()['status'], 'configured')
        code, _ = self.client.mfa_method_delete(self.user.id, method_id)
        self.assertEqual(code, 204)
        self.assertEqual(self._status()['status'], 'not_configured')
        code, _ = self._sign_in()
        self.assertEqual(code, 201)

    def _secret_token(self):
        """A token of the user issued by a service (cluster secret), as in
        an enforced organization the password sign in cannot return one"""
        self._use_secret()
        code, token = self.client.token_get_user_id(self.user.id)
        self.assertEqual(code, 201, token)
        return token['token']

    # --- 6. reset by an organization manager ---

    def test_reset_by_manager_ends_sessions(self):
        _, seed = self._enroll_totp(self._password_token())
        _, challenge = self._sign_in()
        code, token = self._complete(challenge['challenge_id'],
                                     self._totp(seed, 1))
        self.assertEqual(code, 201)
        self._use_token(token['token'])
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 200)

        # the manager of A signs in (password only: no method, no policy)
        manager_token = self._password_token(MANAGER_EMAIL)
        self._use_token(manager_token)
        code, _ = self.client.mfa_methods_reset(self.user.id)
        self.assertEqual(code, 204)
        # the user's sessions are over, the manager's is not
        self._use_token(token['token'])
        code, _ = self.client.user_get(self.user.id)
        self.assertEqual(code, 401)
        self._use_token(manager_token)
        code, _ = self.client.user_get(self.manager.id)
        self.assertEqual(code, 200)
        self.assertEqual(self._status()['status'], 'not_configured')
        # next sign in: password only...
        code, token = self._sign_in()
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:none'])
        # ...or a new enrollment if an organization enforces MFA
        self._enforce(self.org_b)
        code, challenge = self._sign_in()
        self.assertEqual(code, 202)
        self.assertEqual(challenge['state'], 'enrollment_required')

    # --- 7. no bypass through the password-recovery sign in ---

    def test_recovery_code_login_goes_through_mfa(self):
        _, seed = self._enroll_totp(self._password_token())
        self._use_secret()
        code, _ = self.client.verification_code_create(USER_EMAIL, '123456')
        self.assertEqual(code, 201)
        code, challenge = self._sign_in(verification_code='123456')
        self.assertEqual(code, 202, challenge)
        self.assertEqual(challenge['state'], 'mfa_required')
        self.assertNotIn('token', challenge)
        code, token = self._complete(challenge['challenge_id'],
                                     self._totp(seed, 1))
        self.assertEqual(code, 201)
        self.assertEqual(self._mfa_caveat(token['token']), ['mfa:totp'])
        # the recovery code was consumed by the sign in
        self._assert_error(self._sign_in(verification_code='123456'),
                           403, 'OA0071')

    # --- review: secrets never reach the logs ---

    def test_logs_contain_no_secrets(self):
        with self.assertLogs(level=logging.DEBUG) as logs:
            token = self._password_token()
            self._use_token(token)
            code, totp = self.client.mfa_method_create(
                self.user.id, 'totp', label='Phone')
            self.assertEqual(code, 201)
            seed = totp['secret']
            codes = [self._wrong(self._totp(seed)), self._totp(seed)]
            self.client.mfa_method_confirm(self.user.id, totp['id'],
                                           codes[0])
            code, _ = self.client.mfa_method_confirm(self.user.id,
                                                     totp['id'], codes[1])
            self.assertEqual(code, 200)
            self._enroll_email(token)
            codes.append(self._sent_code())
            _, challenge = self._sign_in()
            codes.append(self._totp(seed, 1))
            self._complete(challenge['challenge_id'], self._wrong(codes[-1]))
            code, token = self._complete(challenge['challenge_id'],
                                         codes[-1])
            self.assertEqual(code, 201)
        output = '\n'.join(logs.output)
        self.assertIn('Login challenge completed', output)
        secrets = {
            'seed': seed,
            'otpauth_uri': totp['otpauth_uri'],
            'challenge_id': challenge['challenge_id'],
            'token': token['token'],
            'password': PASSWORD,
        }
        for name, secret in secrets.items():
            self.assertNotIn(secret, output, name)
        # a 6 digit code could appear by chance inside an id: ids removed
        without_ids = UUID_RE.sub('<id>', output)
        for code in codes:
            self.assertNotIn(code, without_ids, 'code in logs')

    # --- review: stale state is cleaned lazily ---

    def test_stale_challenges_and_pending_methods_cleaned(self):
        now = utcnow()
        token = self._password_token()
        self._use_token(token)
        with freeze_time(now):
            code, pending = self.client.mfa_method_create(
                self.user.id, 'totp', label='Phone')
            self.assertEqual(code, 201)
        # pending enrollments live 15 minutes: the next enrollment drops
        # the stale one (never listed by the status)
        with freeze_time(now + timedelta(minutes=16)):
            self.assertEqual(self._status()['methods'], [])
            self._use_token(token)
            code, replacement = self.client.mfa_method_create(
                self.user.id, 'totp', label='Phone')
            self.assertEqual(code, 201)
        self.assertEqual([m.id for m in self._rows(MFAMethod)],
                         [replacement['id']])
        self._assert_error(self.client.mfa_method_confirm(
            self.user.id, pending['id'],
            self._totp(pending['secret'])), 404, 'OA0003')

        # challenges are kept for the attempts window (15 min) after their
        # 5 minutes lifetime, then removed by the next sign in
        self._use_token(token)
        code, _ = self.client.mfa_method_confirm(
            self.user.id, replacement['id'],
            self._totp(replacement['secret']))
        self.assertEqual(code, 200)
        with freeze_time(now + timedelta(minutes=20)):
            _, first = self._sign_in()
        with freeze_time(now + timedelta(minutes=30)):
            _, second = self._sign_in()
            self.assertEqual({c.id for c in self._rows(LoginChallenge)},
                             {first['challenge_id'],
                              second['challenge_id']})
            self._assert_error(self._complete(first['challenge_id'],
                                              '123456'), 404, 'OA0085')
        with freeze_time(now + timedelta(minutes=41)):
            _, third = self._sign_in()
        self.assertEqual({c.id for c in self._rows(LoginChallenge)},
                         {second['challenge_id'], third['challenge_id']})
