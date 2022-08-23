import time
import uuid
from unittest.mock import patch

from report_server.tests.unittests.test_api_base import TestReportBase


class TesApiEvent(TestReportBase):

    def setUp(self, *args, **kwargs):
        super().setUp()
        self.org_id = str(uuid.uuid4())
        self.user_id = str(uuid.uuid4())
        patch(
            'report_server.controllers.event_base.EventBaseController.'
            'get_meta_by_token',
            return_value={'user_id': str(uuid.uuid4()),
                          'valid_until': time.time() * 2}
        ).start()

    def test_poll_event_v2(self):
        code, response = self.client.event_list(self.org_id)
        self.assertEqual(code, 200)

    @patch("report_server.controllers.base.AuthClient.action_resources_get")
    def test_event_count_v2(self, p_ares):
        p_ares.return_value = (200, {'POLL_EVENT': []})
        code, response = self.client.event_count(self.org_id)
        self.assertEqual(code, 200)

    @patch("report_server.controllers.event.Event")
    def test_submit_event(self, p_event):
        p_event.return_value.to_dict.return_value = {
            "id": "59b141a8f3820c2e18491a89"}
        event = {
            'level': 'WARNING',
            'evt_class': 'ERR_CS',
            'object_id': str(uuid.uuid4()),
            'object_type': 'Cloudsite',
            'object_name': 'Some Cloudsite',
            'organization_id': str(uuid.uuid4()),
            'description': 'Cloudsite is failed to start',
            'localized': 'N0000(test)',
            'ack': False
        }
        code, response = self.client.event_submit(**event)
        self.assertEqual(code, 201)

    @patch("report_server.controllers.base.AuthClient.action_resources_get")
    def test_example_event_count_filtering_v2(self, p_ares):
        p_ares.return_value = (200, {'POLL_EVENT': []})
        code, response = self.client.event_count(self.org_id,
                                                 levels=['WARNING', 'ERROR'])
        self.assertEqual(code, 200)

    @patch("report_server.controllers.base.AuthClient.action_resources_get")
    def test_example_poll_event_filtering_v2(self, p_ares):
        p_ares.return_value = (200, {'POLL_EVENT': []})
        code, response = self.client.event_list(
            self.org_id, levels=['INFO'], object_types=['customer'])
        self.assertEqual(code, 200)

    @patch("report_server.controllers.event.EventController._get_event")
    @patch("report_server.controllers.base.AuthClient.action_resources_get")
    def test_example_event_get_v2(self, p_ares, p_event):
        p_ares.return_value = (200, {'POLL_EVENT': [
            ['root', None],
            ['organization', '559aa2c1-081d-4ac1-a893-e8247b2e3b45'],
            ['pool', '64d921bd-b3fe-41a7-8123-c626761c48c3']]})

        p_event.return_value.organization_id = "559aa2c1-081d-4ac1-a893-e8247b2e3b45"
        p_event.return_value.to_dict.return_value = {
            "id": "59b141a8f3820c2e18491a89",
            "organization_id": "559aa2c1-081d-4ac1-a893-e8247b2e3b45"
        }

        code, response = self.client.event_get('59b141a8f3820c2e18491a89')
        self.assertEqual(code, 200)

    def test_example_event_ack_all(self):
        code, response = self.client.event_ack_all(self.org_id)
        self.assertEqual(code, 200)

    def test_example_event_list_v2(self):
        code, response = self.client.event_list(self.org_id)
        self.assertEqual(code, 200)

    def test_example_event_list_invalid(self):
        code, response = self.client.event_list(self.org_id, include_read='ss')
        self.assertEqual(code, 400)

    @patch("report_server.controllers.base.AuthClient.action_resources_get")
    def test_example_event_list_v2_with_token(self, p_ares):
        self.client.secret = None
        # evts.return_value = []
        p_ares.return_value = (200, {'POLL_EVENT': []})
        code, response = self.client.event_list(self.org_id)
        self.assertEqual(code, 200)

    @patch("report_server.controllers.event.Event")
    def test_submit_event_v2_with_initiator(self, p_event):
        p_event.return_value.to_dict.return_value = {
            "id": "59b141a8f3820c2e18491a89"}
        event = {
            'level': 'WARNING',
            'evt_class': 'ERR_CS',
            'object_id': str(uuid.uuid4()),
            'object_type': 'Cloudsite',
            'object_name': 'Some Cloudsite',
            'organization_id': str(uuid.uuid4()),
            'description': 'Cloudsite is failed to start',
            'localized': 'N0000(test)',
            'ack': False,
            'initiator_id': str(uuid.uuid4()),
            'initiator_name': 'The Initiator',
        }
        code, response = self.client.event_submit(**event)
        self.assertEqual(code, 201)
