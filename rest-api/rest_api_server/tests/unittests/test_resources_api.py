from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestResourcesApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.o1 = self.organization_create('Organization1')
        _, self.sub_pool1 = self.client.pool_create(self.o1['id'], {
            'name': 'sub'
        })
        _, self.o2 = self.organization_create('Organization2')

    def test_organization(self):
        code, res = self.get_resources([('organization', self.o1['id'])])
        self.assertEqual(code, 200)
        self.assertEqual(len(res), 1)
        self.assertEqual(res.get(self.o1['id'])['name'], self.o1['name'])

    def test_pool(self):
        code, res = self.get_resources(
            (('pool', self.o1['pool_id']),
             ('pool', self.sub_pool1['id'])))
        self.assertEqual(code, 200)
        self.assertEqual(len(res), 2)
        self.assertEqual(res.get(self.o1['pool_id'])['name'],
                         self.o1['name'])
        self.assertEqual(res.get(self.sub_pool1['id'])['name'],
                         self.sub_pool1['name'])

    def test_org_pool(self):
        code, res = self.get_resources(
            (('organization', self.o2['id']), ('pool', self.sub_pool1['id'])))
        self.assertEqual(code, 200)
        self.assertEqual(len(res), 2)
        self.assertEqual(res.get(self.o2['id'])['name'], self.o2['name'])
        self.assertEqual(res.get(self.sub_pool1['id'])['name'],
                         self.sub_pool1['name'])

    def get_resources(self, payload):
        return self.client.resources_get(payload)

    def organization_create(self, name):
        return self.client.organization_create({'name': name})
