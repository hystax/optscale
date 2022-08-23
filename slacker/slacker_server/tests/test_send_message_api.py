from unittest.mock import patch, Mock, ANY
from datetime import datetime
from slack_sdk.errors import SlackApiError
from slacker_server.tests.test_api_base import TestApiBase
from slacker_server.utils import gen_id


class TestSendMessageAPI(TestApiBase):
    def setUp(self):
        super().setUp()
        self.user_id = gen_id()
        patch('slacker_server.controllers.base.BaseHandlerController.'
              'get_user_id', return_value=self.user_id).start()
        self.client.secret = self.cluster_secret
        self.client.token = None

    def connect_user(self):
        secret = gen_id()
        auth_cl_mock, rest_cl_mock = Mock(), Mock()
        patch('slacker_server.controllers.base.BaseController.'
              'get_user_api_clients',
              return_value=(auth_cl_mock, rest_cl_mock)).start()
        patch('slacker_server.handlers.v2.base.BaseHandler.get_meta_by_token',
              return_value={'user_id': self.user_id,
                            'valid_until': datetime.utcnow().timestamp()*2}
              ).start()
        auth_cl_mock.user_update.return_value = (200, {'email': '1@1.com'})
        rest_cl_mock.organization_list.return_value = (
            200, {'organizations': [{'id': 'orgid', 'name': 'org'}]})
        self.initialize_user(secret)
        code, user = self.client.connect_slack_user(secret)
        self.assertEqual(code, 201)
        return user

    def test_send_no_type(self):
        code, resp = self.client.post(self.client.send_message_url(),
                                      {'channel_id': '1'})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0010')

    def test_send_invalid_parameters_type(self):
        code, resp = self.client.send_message(
            'type', auth_user_id='1', parameters='parameters')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0011')

    def test_send_unexpected(self):
        parameters = {
            "pool_name": "forecast percent alert",
            "organization_name": "The ORG",
            "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
            "public_ip": "172.22.20.8",
            "pool_id": "a575532e-3abb-4d5b-b4d1-c3c65c5166ed",
            "limit": 500,
            "cost": 654.5546,
            "based": "forecast",
            "threshold": 50,
            "threshold_type": "percentage",
        }
        code, resp = self.client.post(self.client.send_message_url(),
                                      {'type': 'test', 'channel_id': '1',
                                       'team_id': '2',
                                       'parameters': parameters, 'extra': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0007')

    def test_send_invalid_type(self):
        channel_id = '123'
        self.initialize_user(slack_channel_id=channel_id)
        code, resp = self.client.send_message('invalid', channel_id)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0011')

    def test_send_invalid_parameters_value(self):
        channel_id = '123'
        self.initialize_user(slack_channel_id=channel_id)
        code, resp = self.client.send_message('alert', channel_id, {})
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0011')

    def test_send_success(self):
        body = {
            "pool_name": "forecast percent alert",
            "organization_name": "The ORG",
            "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
            "public_ip": "172.22.20.8",
            "pool_id": "a575532e-3abb-4d5b-b4d1-c3c65c5166ed",
            "limit": 500,
            "cost": 654.5546,
            "based": "forecast",
            "threshold": 50,
            "threshold_type": "percentage",
        }

        user = self.connect_user()
        p_post_mess = patch(
            'slacker_server.slack_client.SlackClient.chat_post').start()
        code, resp = self.client.send_message(
            'alert', parameters=body, auth_user_id=user['auth_user_id'])
        self.assertEqual(code, 201)
        p_post_mess.assert_called_with(
            channel_id=user['slack_channel_id'],
            team_id=user['slack_team_id'],
            text=ANY, blocks=ANY, unfurl_links=False)

        p_post_mess = patch(
            'slacker_server.slack_client.SlackClient.chat_post').start()
        code, resp = self.client.send_message(
            'alert', parameters=body, channel_id=user['slack_channel_id'],
            team_id=user['slack_team_id'])
        self.assertEqual(code, 201)
        p_post_mess.assert_called_with(
            channel_id=user['slack_channel_id'],
            team_id=user['slack_team_id'],
            text=ANY, blocks=ANY, unfurl_links=False)

    def test_channel_id_auth_user_id_params(self):
        code, resp = self.client.send_message('alert')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0014')

        code, resp = self.client.send_message('alert', channel_id='123',
                                              auth_user_id='123')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0015')

        code, resp = self.client.send_message('alert', team_id='123',
                                              auth_user_id='123')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0015')

    def test_auth_user_id_not_found(self):
        parameters = {
            "pool_name": "forecast percent alert",
            "organization_name": "The ORG",
            "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
            "public_ip": "172.22.20.8",
            "pool_id": "a575532e-3abb-4d5b-b4d1-c3c65c5166ed",
            "limit": 500,
            "cost": 654.5546,
            "based": "forecast",
            "threshold": 50,
            "threshold_type": "percentage",
        }
        code, resp = self.client.send_message('alert', parameters=parameters,
                                              auth_user_id='123')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OS0016')

    def test_send_channel_without_team(self):
        code, resp = self.client.send_message('alert', channel_id='123')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0017')

        code, resp = self.client.send_message('alert', team_id='123')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0017')

    def test_send_to_archived_channel(self):
        parameters = {
            "pool_name": "forecast percent alert",
            "organization_name": "The ORG",
            "organization_id": "b8835bce-da4c-4c29-98a0-4b4967baba53",
            "public_ip": "172.22.20.8",
            "pool_id": "a575532e-3abb-4d5b-b4d1-c3c65c5166ed",
            "limit": 500,
            "cost": 654.5546,
            "based": "forecast",
            "threshold": 50,
            "threshold_type": "percentage",
        }
        p_post = patch('slacker_server.slack_client.'
                       'SlackClient.chat_post').start()
        response = {'ok': False, 'error': 'is_archived'}
        p_post.side_effect = SlackApiError(message='is_archived',
                                           response=response)
        code, resp = self.client.send_message(
            'alert', channel_id='123', team_id='123', parameters=parameters)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OS0019')
