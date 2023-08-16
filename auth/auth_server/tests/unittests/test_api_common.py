from auth.auth_server.tests.unittests.test_api_base import TestAuthBase


class TestCommonApi(TestAuthBase):
    def test_invalid_url(self):
        code, response = self.client.post('invalid', {})
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['reason'], 'Not Found')


class TestCommonApiV2(TestCommonApi):
    def setUp(self, version="v2"):
        super().setUp(version=version)
