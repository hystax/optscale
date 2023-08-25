from slacker.slacker_server.tests.test_api_base import TestApiBase


class TestSlackApp(TestApiBase):
    def test_install(self):
        code, _ = self.client.get('install')
        self.assertEqual(code, 200)

    def test_install_path(self):
        code, _ = self.client.get_install_path()
        self.assertEqual(code, 200)
