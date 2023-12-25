import uuid
from unittest.mock import patch
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.db_factory import DBType, DBFactory
from rest_api.rest_api_server.models.models import Layout
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestLayouts(TestApiBase):
    def setUp(self, version="v2"):
        super().setUp(version)
        patch('rest_api.rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.check_cluster_secret',
              return_value=False).start()
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        self.session = BaseDB.session(engine)()

        _, self.org = self.client.organization_create({"name": "org"})
        self.org_id = self.org["id"]
        _, self.org2 = self.client.organization_create({"name": "org2"})
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'John Org', 'auth_user_id': self.user_id})
        self._mock_auth_user(self.user_id)
        self.user_id2 = self.gen_id()
        _, self.employee2 = self.client.employee_create(
            self.org_id, {'name': 'John2 Org', 'auth_user_id': self.user_id2})
        self.user_id3 = self.gen_id()
        _, self.employee_org2 = self.client.employee_create(
            self.org2['id'], {'name': 'John Org2',
                              'auth_user_id': self.user_id2})
        self.valid_layout = {
            'name': 'layout',
            'type': 'test',
            'data': '{\"some\": \"data\"}',
            'shared': True,
            'entity_id': str(uuid.uuid4())
        }

    def create_layout(self, type_='type_', name='name', owner_id=None,
                      shared=False, data='{}', entity_id=None):
        layout = Layout(
            type=type_,
            name=name,
            shared=shared,
            data=data,
            owner_id=owner_id,
            entity_id=entity_id
        )
        self.session.add(layout)
        self.session.commit()
        return layout.to_dict()

    def test_create_layout(self):
        code, res = self.client.layouts_create(
            self.org_id, self.valid_layout)
        self.assertEqual(201, code)
        self.assertEqual(res['owner_id'], self.employee['id'])
        for k, v in self.valid_layout.items():
            self.assertEqual(res[k], self.valid_layout[k])

    def test_create_missing_params(self):
        for param in ['entity_id', 'data', 'shared']:
            ps = self.valid_layout.copy()
            ps.pop(param, None)
            code, res = self.client.layouts_create(
                self.org_id, ps)
            self.assertEqual(201, code)

        for param in ['name', 'type']:
            ps = self.valid_layout.copy()
            ps.pop(param, None)
            code, res = self.client.layouts_create(
                self.org_id, ps)
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_invalid_params(self):
        for param in ['name', 'type', 'entity_id']:
            ps = self.valid_layout.copy()
            for value in [[], {}, 25]:
                ps[param] = value
                code, res = self.client.layouts_create(
                    self.org_id, ps)
                self.assertEqual(400, code)
                self.assertEqual(res['error']['error_code'], 'OE0214')

        for value in ['test', [], {}, 25]:
            ps = self.valid_layout.copy()
            ps['shared'] = value
            code, res = self.client.layouts_create(
                self.org_id, ps)
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0226')

        for value in ['test', [], {}, 25]:
            ps = self.valid_layout.copy()
            ps['data'] = value
            code, res = self.client.layouts_create(
                self.org_id, ps)
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0219')

        ps = self.valid_layout.copy()
        ps['unexpected'] = 'value'
        code, res = self.client.layouts_create(
            self.org_id, ps)
        self.assertEqual(400, code)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_list_layouts(self):
        type_ = 'test_type'
        layout0 = self.create_layout(owner_id=self.employee_org2['id'],
                                     type_=type_, shared=True)
        layout1 = self.create_layout(owner_id=self.employee['id'])
        layout2 = self.create_layout(
            type_=type_, owner_id=self.employee['id'])
        layout3 = self.create_layout(
            type_=type_, owner_id=self.employee['id'], entity_id=self.user_id)
        layout4 = self.create_layout(
            type_=type_, owner_id=self.employee2['id'], entity_id=self.user_id,
            shared=True)
        layout5 = self.create_layout(
            type_=type_, owner_id=self.employee2['id'], entity_id=self.user_id,
            shared=False)
        layout6 = self.create_layout(
            type_=type_, owner_id=self.employee2['id'], shared=True)

        # not shared, no entity_id
        code, res = self.client.layouts_list(
            self.org_id, layout_type=type_)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['layouts']), 2)
        res_layouts_ids = [x['id'] for x in res['layouts']]
        self.assertIn(layout2['id'], res_layouts_ids)
        self.assertIn(layout3['id'], res_layouts_ids)
        for res_layout in res['layouts']:
            self.assertNotIn('data', res_layout)
        self.assertEqual(res['current_employee_id'], self.employee['id'])

        # entity_id
        code, res = self.client.layouts_list(
            self.org_id, layout_type=type_, entity_id=self.user_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['layouts']), 1)
        res_layouts_ids = [x['id'] for x in res['layouts']]
        self.assertIn(layout3['id'], res_layouts_ids)

        # shared
        code, res = self.client.layouts_list(
            self.org_id, layout_type=type_, include_shared=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['layouts']), 4)
        res_layouts_ids = [x['id'] for x in res['layouts']]
        self.assertIn(layout2['id'], res_layouts_ids)
        self.assertIn(layout3['id'], res_layouts_ids)
        self.assertIn(layout4['id'], res_layouts_ids)
        self.assertIn(layout6['id'], res_layouts_ids)

        # shared, entity_id
        code, res = self.client.layouts_list(
            self.org_id, layout_type=type_, include_shared=True,
            entity_id=self.user_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['layouts']), 2)
        self.assertIn(layout3['id'], res_layouts_ids)
        self.assertIn(layout4['id'], res_layouts_ids)

        # cluster_secret
        patch('rest_api.rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.check_cluster_secret',
              return_value=True).start()
        code, res = self.client.layouts_list(
            self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['layouts']), 6)
        res_layouts_ids = [x['id'] for x in res['layouts']]
        self.assertNotIn(layout0['id'], res_layouts_ids)
        self.assertEqual(res['current_employee_id'], None)

    def test_update_layout(self):
        layout1 = self.create_layout(owner_id=self.employee['id'])
        params = self.valid_layout.copy()
        params.pop('type', None)
        params.pop('entity_id', None)
        code, res = self.client.layout_update(
            self.org_id, layout1['id'], params)
        self.assertEqual(code, 200)
        for k, v in params.items():
            self.assertEqual(res[k], v)

        layout2 = self.create_layout(owner_id=self.employee2['id'])
        code, res = self.client.layout_update(
            self.org_id, layout2['id'], params)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_update_invalid_params(self):
        layout = self.create_layout(owner_id=self.employee['id'])
        for param in ['type', 'entity_id']:
            code, res = self.client.layout_update(
                self.org_id, layout['id'], {param: 'test'})
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0211')

        for value in [[], {}, 25]:
            code, res = self.client.layout_update(
                    self.org_id, layout['id'], {'name': value})
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0214')

        for value in ['test', [], {}, 25]:
            code, res = self.client.layout_update(
                    self.org_id, layout['id'], {'shared': value})
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0226')

        for value in ['test', [], {}, 25]:
            code, res = self.client.layout_update(
                    self.org_id, layout['id'], {'data': value})
            self.assertEqual(400, code)
            self.assertEqual(res['error']['error_code'], 'OE0219')

        code, res = self.client.layout_update(
            self.org_id, layout['id'], {'unexpected': 'value'})
        self.assertEqual(400, code)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_get_layout(self):
        layout1 = self.create_layout(owner_id=self.employee['id'])
        code, res = self.client.layout_get(
            self.org_id, layout1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(res['id'], layout1['id'])

        # shared
        layout2 = self.create_layout(owner_id=self.employee2['id'],
                                     shared=True)
        code, res = self.client.layout_get(
            self.org_id, layout2['id'])
        self.assertEqual(code, 200)

        # not shared
        layout3 = self.create_layout(owner_id=self.employee2['id'],
                                     shared=False)
        code, res = self.client.layout_get(
            self.org_id, layout3['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_delete_layout(self):
        layout1 = self.create_layout(owner_id=self.employee['id'])
        code, _ = self.client.layout_delete(
            self.org_id, layout1['id'])
        self.assertEqual(code, 204)
        res = self.session.query(Layout).filter(
            Layout.id == layout1['id']).one_or_none()
        self.assertIsNone(res)

        layout2 = self.create_layout(owner_id=self.employee2['id'],
                                     shared=True)
        code, res = self.client.layout_delete(
            self.org_id, layout2['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

        # cluster secret
        patch('rest_api.rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.check_cluster_secret',
              return_value=True).start()
        layout3 = self.create_layout(owner_id=self.employee2['id'],
                                     shared=True)
        code, res = self.client.layout_delete(
            self.org_id, layout3['id'])
        self.assertIsNone(res)
        self.assertEqual(code, 204)
        res = self.session.query(Layout).filter(
            Layout.id == layout3['id']).one_or_none()
        self.assertIsNone(res)

        code, res = self.client.layout_delete(
            self.org_id, layout3['id'])
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

        code, res = self.client.layout_delete(
            self.org_id, '123')
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')
