import json
import uuid

from katara.katara_service.tests.unittests.test_api_base import TestBase


class TestRecipientApi(TestBase):

    def test_recipient_get(self):
        recipients = self.generate_recipients(1)
        code, recipient = self.client.recipient_get(recipients[0].id)
        self.assertEqual(code, 200)
        self.assertEqual(recipients[0].id, recipient['id'])

    def test_recipient_get_nonexisting(self):
        id_ = str(uuid.uuid4())
        code, _ = self.client.recipient_get(id_)
        self.assertEqual(code, 404)

    def test_recipient_list(self):
        self.generate_recipients(3)
        code, _ = self.client.recipient_list(None)
        self.assertEqual(code, 400)

    def test_recipient_list_filtered(self):
        recipients = self.generate_recipients(3)
        scope_id = recipients[0].scope_id
        code, api_recipients = self.client.recipient_list(scope_id=scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(api_recipients['recipients']), 1)
        self.assertEqual(api_recipients['recipients'][0]['scope_id'], scope_id)

    def test_recipient_list_empty(self):
        scope_id = str(uuid.uuid4())
        code, api_recipients = self.client.recipient_list(scope_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(api_recipients['recipients']), 0)

    def test_recipient_delete(self):
        recipients = self.generate_recipients(1)
        delete_criteria = [recipients[0].id]
        code, _ = self.client.recipients_delete(recipient_ids=delete_criteria)
        self.assertEqual(code, 204)
        code, _ = self.client.recipient_get(recipients[0].id)
        self.assertEqual(code, 404)

        recipients = self.generate_recipients(1)
        delete_criteria = [recipients[0].scope_id]
        code, _ = self.client.recipients_delete(scope_ids=delete_criteria)
        self.assertEqual(code, 204)
        code, _ = self.client.recipient_get(recipients[0].id)
        self.assertEqual(code, 404)

    def test_recipient_delete_nonexisting(self):
        id_ = str(uuid.uuid4())
        delete_criteria = [id_]
        code, _ = self.client.recipients_delete(recipient_ids=delete_criteria)
        self.assertEqual(code, 204)

    def test_recipient_delete_nonlist_param(self):
        id_ = str(uuid.uuid4())
        delete_criteria = id_
        code, _ = self.client.recipients_delete(recipient_ids=delete_criteria)
        self.assertEqual(code, 204)

    def test_recipient_update(self):
        recipients = self.generate_recipients(1)
        new_meta = json.dumps(recipients[0].to_json())
        code, recipient = self.client.recipient_update(
            recipients[0].id, meta=new_meta)
        self.assertEqual(code, 200)
        self.assertEqual(new_meta, recipient['meta'])

    def test_recipient_update_wrong_meta(self):
        recipients = self.generate_recipients(1)
        new_meta = json.loads(recipients[0].to_json())
        code, _ = self.client.recipient_update(
            recipients[0].id, meta=new_meta)
        self.assertEqual(code, 400)

    def test_recipient_create(self):
        payload = {
            "role_purpose": 'optscale_manager',
            "scope_id": str(uuid.uuid4()),
        }
        code, recipient = self.client.recipient_create(**payload)
        self.assertEqual(code, 201)
        self.assertNotEqual(recipient['id'], None)
        self.assertEqual(recipient['role_purpose'], payload['role_purpose'])
        self.assertEqual(recipient['scope_id'], payload['scope_id'])

    def test_recipient_create_user_id(self):
        payload = {
            "user_id": str(uuid.uuid4()),
            "scope_id": str(uuid.uuid4()),
        }
        code, recipient = self.client.recipient_create(**payload)
        self.assertEqual(code, 201)
        self.assertNotEqual(recipient['id'], None)
        self.assertEqual(recipient['user_id'], payload['user_id'])
        self.assertEqual(recipient['scope_id'], payload['scope_id'])

    def test_recipient_create_unassigned(self):
        payload = {
            "scope_id": str(uuid.uuid4()),
        }
        code, _ = self.client.recipient_create(**payload)
        self.assertEqual(code, 400)

    def test_recipient_create_multi_assigned(self):
        payload = {
            "role_purpose": 'optscale_manager',
            "user_id": str(uuid.uuid4()),
            "scope_id": str(uuid.uuid4()),
        }
        code, _ = self.client.recipient_create(**payload)
        self.assertEqual(code, 400)

    def test_recipient_create_wrong_porpose(self):
        payload = {
            "role_purpose": 'optscale_slave',
            "scope_id": str(uuid.uuid4()),
        }
        code, _ = self.client.recipient_create(**payload)
        self.assertEqual(code, 400)

    def test_recipient_create_wrong_meta(self):
        payload = {
            "role_purpose": 'optscale_manager',
            "scope_id": str(uuid.uuid4()),
            "meta": {
                "k1": "v1",
                "k2": "v2"
            }
        }
        code, _ = self.client.recipient_create(**payload)
        self.assertEqual(code, 400)
