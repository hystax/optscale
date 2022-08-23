import uuid
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestAuthHierarchyApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp()
        _, self.o1 = self.client.organization_create({'name': 'Organization1'})
        _, self.b11 = self.client.pool_create(self.o1['id'], {
            'name': 'b11'
        })
        _, self.b12 = self.client.pool_create(self.o1['id'], {
            'name': 'b12', 'parent_id': self.b11['id']
        })
        _, self.o2 = self.client.organization_create({'name': 'Organization2'})

    def test_root_hierarchy(self):
        code, hierarchy = self.client.auth_hierarchy_get('root', None)
        self.assertEqual(code, 200)
        self.assertEqual(len(hierarchy['root']['null']['organization']), 2)
        self.assertEqual(len(
            list(filter(lambda x: x in [self.o1['id'], self.o2['id']],
                        hierarchy['root']['null']['organization'].keys()))), 2)
        self.assertEqual(
            hierarchy['root']['null']['organization'][self.o2['id']]['pool'],
            [self.o2['pool_id']])
        self.assertEqual(len(
            hierarchy['root']['null']['organization'][self.o1['id']]['pool']
        ), 3)
        self.assertEqual(len(list(filter(
            lambda x: x in [self.o1['pool_id'], self.b11['id'], self.b12['id']],
            hierarchy['root']['null']['organization'][self.o1['id']]['pool']))), 3)

    def test_root_hierarchy_deleted_organization(self):
        self.delete_organization(self.o1['id'])
        code, hierarchy = self.client.auth_hierarchy_get('root', None)
        self.assertEqual(code, 200)
        self.assertEqual(len(hierarchy['root']['null']['organization']), 1)
        self.assertEqual(
            hierarchy['root']['null']['organization'][self.o2['id']]['pool'],
            [self.o2['pool_id']])

    def test_organization_hierarchy(self):
        code, hierarchy = self.client.auth_hierarchy_get(
            'organization', self.o1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(
            len(hierarchy['organization'][self.o1['id']]['pool']), 3)
        self.assertEqual(len(list(filter(
            lambda x: x in [self.o1['pool_id'], self.b11['id'], self.b12['id']],
            hierarchy['organization'][self.o1['id']]['pool']))), 3)

    def test_org_hierarchy_deleted_pool(self):
        self.client.pool_delete(self.b12['id'])
        code, hierarchy = self.client.auth_hierarchy_get('organization',
                                                         self.o1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(
            len(hierarchy['organization'][self.o1['id']]['pool']), 2)
        self.assertEqual(len(list(filter(
            lambda x: x in [self.o1['pool_id'], self.b11['id']],
            hierarchy['organization'][self.o1['id']]['pool']))), 2)

    def test_pool_hierarchy(self):
        code, hierarchy = self.client.auth_hierarchy_get('pool',
                                                         self.b11['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hierarchy['pool']), 1)

    def test_organization_resource_not_found(self):
        code, _ = self.client.auth_hierarchy_get('organization',
                                                 str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_invalid_type(self):
        code, _ = self.client.auth_hierarchy_get('invalid',
                                                 str(uuid.uuid4()))
        self.assertEqual(code, 400)

    def test_resource_no_scope(self):
        types = ['organization', 'customer', 'group']
        for t in types:
            code, _ = self.client.auth_hierarchy_get(t, None)
            self.assertEqual(code, 400)

    def test_pool_not_found(self):
        code, _ = self.client.auth_hierarchy_get('pool', str(uuid.uuid4()))
        self.assertEqual(code, 404)
