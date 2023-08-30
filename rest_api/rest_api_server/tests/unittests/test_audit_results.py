import uuid
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from unittest.mock import patch


class StreamingBodyMock(object):
    def __init__(self, bytes_string):
        self._bytes_string = bytes_string

    def read(self):
        return self._bytes_string


class TestAuditResultsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "test_org"})
        self.org_id = self.org['id']

    def test_invalid_organization(self):
        code, resp = self.client.download_audit_result(str(uuid.uuid4()), '1')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_download_audit(self):
        audit_id = str(uuid.uuid4())
        audit_content = b'test'
        patch('rest_api.rest_api_server.controllers.audit_result.AuditResultController.'
              '_get_s3_audit_result',
              return_value={'Body': StreamingBodyMock(audit_content)}
              ).start()
        code, resp = self.client.download_audit_result(self.org_id, audit_id)
        self.assertEqual(code, 200)
        self.assertEqual(resp, audit_content)
