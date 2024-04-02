import uuid

from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_infrastructure_base import (
    TestInfrastructureBase, get_http_error)


class TestTemplateApi(TestInfrastructureBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        self.param_to_obj_map = {
            'task_ids': 'tasks',
            'cloud_account_ids': 'cloud_accounts',
            'region_ids': 'regions',
            'instance_types': 'instance_types'
        }

    def test_create(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        for k, v in self.valid_template.items():
            if k in self.param_to_obj_map:
                new_param = self.param_to_obj_map[k]
                self.assertTrue(isinstance(template[new_param], list))
                for x in template[new_param]:
                    self.assertTrue(isinstance(x, object))
            else:
                self.assertEqual(template[k], v)

    def test_create_incorrect(self):
        incorrect_updates = {
            'name': 1,
            'tags': 2,
            'hyperparameters': 3,
            'task_ids': [4],
            'cloud_account_ids': True,
            'region_ids': '6',
            'instance_types': {7: 7},
            'budget': 'eight',
            'name_prefix': -1
        }
        for k, v in incorrect_updates.items():
            valid_template = self.valid_template.copy()
            valid_template[k] = v
            code, _ = self.client.template_create(
                self.organization_id, valid_template)
            self.assertEqual(code, 400)

    def test_create_unexpected(self):
        valid_template = self.valid_template.copy()
        valid_template['extra'] = 'value'
        code, res = self.client.template_create(
            self.organization_id, valid_template)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_create_missing(self):
        for k, v in self.valid_template.items():
            valid_template = self.valid_template.copy()
            valid_template.pop(k)
            code, res = self.client.template_create(
                self.organization_id, valid_template)
            self.assertEqual(code, 400)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0216')

    def test_create_nonexisting_entities(self):
        nonexisting_updates = ['task_ids', 'cloud_account_ids']
        for k in nonexisting_updates:
            valid_template = self.valid_template.copy()
            valid_template[k] = [str(uuid.uuid4())]
            code, res = self.client.template_create(
                self.organization_id, valid_template)
            self.assertEqual(code, 404)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0002')

    def test_create_incorrect_cloud_params(self):
        valid_template = self.valid_template.copy()
        valid_template['instance_types'] = [str(uuid.uuid4())]
        code, res = self.client.template_create(
            self.organization_id, valid_template)
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0542')

    def test_create_duplicate(self):
        code, _ = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        target = ('rest_api.rest_api_server.controllers.infrastructure.template.'
                  'TemplateController.create_template')
        with patch(target, side_effect=get_http_error(409)):
            code, res = self.client.template_create(
                self.organization_id, self.valid_template)
            self.assertEqual(code, 409)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0149')

    def test_create_deleted_ca(self):
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 404)

    def test_create_deleted_task(self):
        code, _ = self.client.task_delete(self.organization_id, self.task_id)
        self.assertEqual(code, 204)
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 404)

    def test_get(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, resp = self.client.template_get(
            self.organization_id, template['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, template)

    def test_get_nonexisting(self):
        code, _ = self.client.template_get(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_get_deleted_ca(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        code, resp = self.client.template_get(
            self.organization_id, template['id'])
        self.assertEqual(code, 200)
        self.assertTrue(resp['cloud_accounts'][0].get('deleted'))

    def test_get_deleted_task(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, _ = self.client.task_delete(self.organization_id, self.task_id)
        self.assertEqual(code, 204)
        code, resp = self.client.template_get(
            self.organization_id, template['id'])
        self.assertEqual(code, 200)
        self.assertTrue(resp['tasks'][0].get('deleted'))

    def test_delete(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, resp = self.client.template_delete(
            self.organization_id, template['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.template_delete(
            self.organization_id, template['id'])
        self.assertEqual(code, 404)

    def test_delete_nonexisting(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, _ = self.client.runset_create(
            self.organization_id, template['id'], self.valid_runset)
        code, _ = self.client.template_delete(
            self.organization_id, template['id'])
        self.assertEqual(code, 409)

    def test_delete_with_runset(self):
        code, _ = self.client.template_delete(
            self.organization_id, str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_update(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        updates = {
            'name': 'new_name',
            'tags': {
                'template': 'not test'
            },
            'hyperparameters': {
                'MODEL_URL': 'https://not-example.com/model/url',
                'DATASET_URL': 'https://not-example.com/dataset/url',
                'LEARNING_RATE': '2'
            },
            'region_ids': ['us-east-1', 'us-west-1'],
            'instance_types': ['p4', 'p3', 'p2', 'm5'],
        }
        code, template = self.client.template_update(
            self.organization_id, template['id'], updates)
        self.assertEqual(code, 200)
        for k, v in updates.items():
            if isinstance(v, dict):
                self.assertDictEqual(template[k], v)
            elif isinstance(v, list):
                for val in template[self.param_to_obj_map[k]]:
                    self.assertTrue(val['name'] in v)
            else:
                self.assertEqual(template[k], v)

    def test_update_nonexisting(self):
        updates = {
            'name': 'new_name',
        }
        code, _ = self.client.template_update(
            self.organization_id, str(uuid.uuid4()), updates)
        self.assertEqual(code, 404)

    def test_update_incorrect(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        updates_base = {
            'name': 1,
            'tags': 2,
            'hyperparameters': 3,
            'task_ids': [4],
            'cloud_account_ids': True,
            'region_ids': '6',
            'instance_types': {7: 7},
            'budget': 'eight',
            'name_prefix': -1
        }
        for k, v in updates_base.items():
            updates = {k: v}
            code, _ = self.client.template_update(
                self.organization_id, template['id'], updates)
            self.assertEqual(code, 400)

    def test_update_unexpected(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, res = self.client.template_update(
            self.organization_id, template['id'], {'extra': 'value'})
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0212')

    def test_update_nonexisting_entities(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        nonexisting_updates = ['task_ids', 'cloud_account_ids']
        for k in nonexisting_updates:
            code, res = self.client.template_update(
                self.organization_id, template['id'], {k: [str(uuid.uuid4())]})
            self.assertEqual(code, 404)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0002')

    def test_update_incorrect_cloud_params(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, res = self.client.template_update(
            self.organization_id, template['id'],
            {'instance_types': [str(uuid.uuid4())]})
        self.assertEqual(code, 400)
        self.assertEqual(res.get('error', {}).get('error_code'), 'OE0542')

    def test_update_duplicate(self):
        code, _ = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        valid_template = self.valid_template.copy()
        base_name = valid_template.pop('name')
        valid_template['name'] = str(uuid.uuid4())
        code, template = self.client.template_create(
            self.organization_id, valid_template)
        self.assertEqual(code, 201)
        target = ('rest_api.rest_api_server.controllers.infrastructure.template.'
                  'TemplateController.update_template')
        with patch(target, side_effect=get_http_error(409)):
            code, res = self.client.template_update(
                self.organization_id, template['id'], {'name': base_name})
            self.assertEqual(code, 409)
            self.assertEqual(res.get('error', {}).get('error_code'), 'OE0149')

    def test_update_deleted_task(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, _ = self.client.task_delete(self.organization_id, self.task_id)
        self.assertEqual(code, 204)
        updates = {
            'task_ids': [self.task_id]
        }
        code, _ = self.client.template_update(
            self.organization_id, template['id'], updates)
        self.assertEqual(code, 404)

    def test_update_deleted_ca(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, _ = self.client.cloud_account_delete(self.cloud_account_id)
        self.assertEqual(code, 204)
        updates = {
            'cloud_account_ids': [self.cloud_account_id]
        }
        code, _ = self.client.template_update(
            self.organization_id, template['id'], updates)
        self.assertEqual(code, 404)

    def test_overview_empty(self):
        code, overview = self.client.templates_overview(self.organization_id)
        self.assertEqual(code, 200)
        self.assertFalse(overview.get('templates', []))

    def test_overview_zeroed(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, overview = self.client.templates_overview(self.organization_id)
        self.assertEqual(code, 200)
        self.assertTrue(overview.get('templates', []))
        for o in overview['templates']:
            self.assertEqual(template['id'], o['id'])
            self.assertEqual(template['name'], o['name'])
            self.assertEqual(o.get('total_runs'), 0)
            self.assertEqual(o.get('total_cost'), 0)
            self.assertEqual(o.get('last_runset_cost'), 0)

    def test_overview(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, runset = self.client.runset_create(
            self.organization_id, template['id'], self.valid_runset)
        # calling to trigger runners creation
        self.assertEqual(code, 201)
        code, _ = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        code, overview = self.client.templates_overview(self.organization_id)
        self.assertEqual(code, 200)
        self.assertTrue(overview.get('templates', []))
        for o in overview['templates']:
            self.assertEqual(template['id'], o['id'])
            self.assertEqual(template['name'], o['name'])
            self.assertEqual(o.get('total_runs'), 0)
            # Hardcoded based on duration and flavor cost (hourly cost is 0.224)
            self.assertEqual(o.get('total_cost'), 0.0062)
            self.assertEqual(o.get('last_runset_cost'), 0.0062)

    def test_overview_deleted_ca(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, runset = self.client.runset_create(
            self.organization_id, template['id'], self.valid_runset)
        # calling to trigger runners creation
        self.assertEqual(code, 201)
        code, _ = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        for ca_id in self.valid_template['cloud_account_ids']:
            code, _ = self.client.cloud_account_delete(ca_id)
            self.assertEqual(code, 204)
        code, overview = self.client.templates_overview(self.organization_id)
        self.assertEqual(code, 200)
        self.assertTrue(overview.get('templates', []))

    def test_overview_deleted_task(self):
        code, template = self.client.template_create(
            self.organization_id, self.valid_template)
        self.assertEqual(code, 201)
        code, runset = self.client.runset_create(
            self.organization_id, template['id'], self.valid_runset)
        # calling to trigger runners creation
        self.assertEqual(code, 201)
        code, _ = self.client.runset_get(self.organization_id, runset['id'])
        self.assertEqual(code, 200)
        for task_id in self.valid_template['task_ids']:
            code, _ = self.client.task_delete(
                self.organization_id, task_id)
            self.assertEqual(code, 204)
        code, overview = self.client.templates_overview(self.organization_id)
        self.assertEqual(code, 200)
        self.assertTrue(overview.get('templates', []))
