import uuid
from datetime import datetime
from unittest.mock import patch, ANY, call

from pymongo import UpdateMany

from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.utils import encoded_tags


class TestClusterTypesApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        self.valid_cluster_type = {
            'name': 'cluster',
            'tag_key': 'type'
        }

        self.auth_user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': self.auth_user_id})
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee['id'])
        self._mock_auth_user(self.auth_user_id)
        self.user = {
            'id': self.auth_user_id,
            'display_name': 'default',
            'email': 'email@email.com',
        }
        patch('rest_api_server.handlers.v1.base.BaseAuthHandler._get_user_info',
              return_value=self.user).start()
        self.p_get_user_info.return_value = self.user
        self.allowed_user_pool_actions = {
            self.auth_user_id: {
                'MANAGE_RESOURCES': [self.org['pool_id']],
                'MANAGE_OWN_RESOURCES': [self.org['pool_id']]
            }
        }

        cloud_acc = {
            'name': 'cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, cloud_acc, auth_user_id=self.auth_user_id)

    def test_cluster_type_create(self):
        code, res = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        self.assertEqual(res['organization_id'], self.org_id)
        self.assertEqual(res['priority'], 1)
        for k, v in self.valid_cluster_type.items():
            self.assertEqual(res[k], v)

    def test_cluster_type_create_existing(self):
        for expected_code in [201, 409]:
            code, res = self.client.cluster_type_create(
                self.org_id, self.valid_cluster_type)
            self.assertEqual(code, expected_code)
            if code == 409:
                self.assertEqual(res['error']['error_code'], 'OE0463')

    def test_cluster_type_create_not_provided(self):
        for k in ['name', 'tag_key']:
            valid_cluster_type = self.valid_cluster_type.copy()
            valid_cluster_type.pop(k, None)
            code, res = self.client.cluster_type_create(
                self.org_id, valid_cluster_type)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_cluster_type_create_unexpected(self):
        valid_cluster_type = self.valid_cluster_type.copy()
        valid_cluster_type['unexpected'] = 'arg'
        code, res = self.client.cluster_type_create(
            self.org_id, valid_cluster_type)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_cluster_type_create_wrong_org(self):
        code, res = self.client.cluster_type_create(
            str(uuid.uuid4()), self.valid_cluster_type)
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_cluster_type_create_wrong_type(self):
        for k in ['name', 'tag_key']:
            valid_cluster_type = self.valid_cluster_type.copy()
            valid_cluster_type[k] = 1
            code, res = self.client.cluster_type_create(
                self.org_id, valid_cluster_type)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0214')

    def test_cluster_type_create_length(self):
        for k in ['name', 'tag_key']:
            valid_cluster_type = self.valid_cluster_type.copy()
            valid_cluster_type[k] = 'a' * 300
            code, res = self.client.cluster_type_create(
                self.org_id, valid_cluster_type)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0215')

    def test_cluster_type_list(self):
        code, created_obj = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        code, res = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('cluster_types')), 1)
        for c_type in res.get('cluster_types'):
            for k, v in created_obj.items():
                self.assertEqual(c_type.get(k), v)

    def test_cluster_type_list_wrong_org(self):
        code, res = self.client.cluster_type_list(
            str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_cluster_type_list_empty(self):
        code, res = self.client.cluster_type_list(
            self.org_id)
        self.assertEqual(code, 200)

    def test_cluster_type_delete(self):
        code, res = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_type_delete(res['id'])
        self.assertEqual(code, 204)

    def test_cluster_type_delete_wrong_id(self):
        code, res = self.client.cluster_type_delete(str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_cluster_type_priority_not_exist(self):
        code, res = self.client.cluster_type_priority_update(str(uuid.uuid4()), '')
        self.assertEqual(code, 404)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_cluster_type_priority_without_action(self):
        code, cl_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_type_priority_update(cl_type['id'], '')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_cluster_type_priority_wrong_action(self):
        code, cl_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_type_priority_update(
            cl_type['id'], 'some')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0166')

        code, res = self.client.cluster_type_priority_update(
            cl_type['id'], 1)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0214')

    def test_cluster_type_priority_valid_actions(self):
        code, cl_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        for action in ['prioritize', 'promote', 'demote', 'deprioritize']:
            code, res = self.client.cluster_type_priority_update(
                cl_type['id'], action)
            self.assertEqual(code, 200)

    def test_cluster_type_priority_changed_after_deletion(self):
        code, cl_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        self.assertEqual(cl_type['priority'], 1)
        code, cl_type2 = self.client.cluster_type_create(
            self.org_id, {'name': 'name_2', 'tag_key': 'key_2'})
        self.assertEqual(code, 201)
        self.assertEqual(cl_type2['priority'], 2)

        code, _ = self.client.cluster_type_delete(cl_type['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        cluster_types = resp['cluster_types']
        self.assertEqual(len(cluster_types), 1)
        self.assertEqual(cluster_types[0]['id'], cl_type2['id'])
        self.assertEqual(cluster_types[0]['priority'], 1)

        code, cl_type3 = self.client.cluster_type_create(
            self.org_id, {'name': 'name_3', 'tag_key': 'key_3'})
        self.assertEqual(code, 201)
        self.assertEqual(cl_type2['priority'], 2)

    def test_cluster_type_prioritize(self):
        for cl_name in ['cl_type1', 'cl_type2', 'cl_type3', 'cl_type4']:
            self.client.cluster_type_create(
                self.org_id, {'name': cl_name, 'tag_key': cl_name})

        code, cl_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        initial_order = [r['id'] for r in cl_types['cluster_types']]

        # prioritize first. No changes
        code, response = self.client.cluster_type_prioritize(initial_order[0])
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(initial_order, new_order)

        # prioritize 3rd
        expected_new_order = [initial_order[2], initial_order[0],
                              initial_order[1], initial_order[3]]
        code, response = self.client.cluster_type_prioritize(initial_order[2])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(expected_new_order, new_order)

        code, list_cluster_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(list_cluster_types, response)

    def test_cluster_type_promote(self):
        for cl_name in ['cl_type1', 'cl_type2', 'cl_type3', 'cl_type4']:
            self.client.cluster_type_create(
                self.org_id, {'name': cl_name, 'tag_key': cl_name})

        code, cl_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        initial_order = [r['id'] for r in cl_types['cluster_types']]

        # promote first
        code, response = self.client.cluster_type_promote(initial_order[0])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(initial_order, new_order)

        # promote 3rd
        code, response = self.client.cluster_type_promote(initial_order[2])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        expected_order = [initial_order[0], initial_order[2],
                          initial_order[1], initial_order[3]]
        self.assertEqual(expected_order, new_order)

    def test_cluster_type_demote(self):
        for cl_name in ['cl_type1', 'cl_type2', 'cl_type3', 'cl_type4']:
            self.client.cluster_type_create(
                self.org_id, {'name': cl_name, 'tag_key': cl_name})

        code, cl_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        initial_order = [r['id'] for r in cl_types['cluster_types']]

        # demote last
        code, response = self.client.cluster_type_demote(initial_order[3])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(initial_order, new_order)

        # demote 2nd
        code, response = self.client.cluster_type_demote(initial_order[1])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        expected_order = [initial_order[0], initial_order[2],
                          initial_order[1], initial_order[3]]
        self.assertEqual(expected_order, new_order)

    def test_cluster_type_deprioritize(self):
        for cl_name in ['cl_type1', 'cl_type2', 'cl_type3', 'cl_type4']:
            self.client.cluster_type_create(
                self.org_id, {'name': cl_name, 'tag_key': cl_name})

        code, cl_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        initial_order = [r['id'] for r in cl_types['cluster_types']]

        # deprioritize last
        code, response = self.client.cluster_type_deprioritize(
            initial_order[3])
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(initial_order, new_order)

        # deprioritize 2nd
        expected_new_order = [initial_order[0], initial_order[2],
                              initial_order[3], initial_order[1]]
        code, response = self.client.cluster_type_deprioritize(
            initial_order[1])
        self.assertEqual(code, 200)
        new_order = [r['id'] for r in response['cluster_types']]
        self.assertEqual(expected_new_order, new_order)

        code, list_cluster_types = self.client.cluster_type_list(self.org_id)
        self.assertEqual(code, 200)
        self.assertEqual(list_cluster_types, response)

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='test_type',
                              name='test_resource', tags=None, last_seen=None,
                              region=None):
        resource = {
            'cloud_resource_id': self.gen_id(),
            'name': name,
            'resource_type': resource_type,
            'employee_id': employee_id,
            'pool_id': pool_id,
            'last_seen': last_seen or int(datetime.utcnow().timestamp()),
            'region': region
        }
        if tags:
            resource.update({'tags': tags})
        code, resource = self.cloud_resource_create(
            cloud_account_id, resource)
        return code, resource

    def create_environment_resource(self, organization_id, employee_id=None,
                                    pool_id=None, resource_type='test_type',
                                    name='test_resource', tags=None):
        resource = {
            'name': name,
            'resource_type': resource_type,
            'employee_id': employee_id,
            'pool_id': pool_id,
        }
        if tags:
            resource.update({'tags': tags})
        code, resource = self.environment_resource_create(
            organization_id, resource)
        return code, resource

    def test_cluster_types_apply(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val2'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource3 = self.create_environment_resource(
            self.org_id, tags={'type': 'val2'})
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertIsNotNone(res.get('processed_resources'))
        self.assertIsNotNone(res.get('processed_cluster_types'))
        self.assertEqual(res['processed_resources'], 0)
        self.assertEqual(len(res['processed_cluster_types']), 0)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 3)
        self.assertEqual(len(res['processed_cluster_types']), 1)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['id'], cluster_type['id'])
            self.assertEqual(c_type_info['clusters_count'], 2)
            self.assertEqual(c_type_info['clustered_resources_count'], 3)

    def test_cluster_types_apply_unexpected(self):
        unexpected = {'unexpected': 'arg'}
        code, res = self.client.post(
            self.client.cluster_types_apply_url(self.org_id), unexpected)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_cluster_types_reapply_tag_loose(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val', 'another': 'tag'},
            region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val', 'yet_another': 'tag'},
            region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        new_tags = resource1.get('tags')
        new_tags.pop('another')
        new_tags['yet_another'] = 'taggg'

        self.resources_collection.update_one(
            filter={'_id': resource1['id']},
            update={'$set': {'tags': encoded_tags(new_tags)}}
        )
        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        cluster = list(self.resources_collection.find(
            {'cluster_type_id': {'$exists': True}}))
        cluster = cluster[0]
        self.assertEqual(len(cluster.get('tags', {})), 1)

    def test_cluster_types_apply_priority(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type1 = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 1)
        self.assertEqual(len(res['processed_cluster_types']), 1)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['id'], cluster_type1['id'])
            self.assertEqual(c_type_info['clusters_count'], 1)
            self.assertEqual(c_type_info['clustered_resources_count'], 1)

        code, resource = self.client.cloud_resource_get(resource1['id'])
        self.assertEqual(code, 200)
        old_cluster_id = resource['cluster_id']

        valid_cluster_type = self.valid_cluster_type.copy()
        valid_cluster_type['name'] = 'cluster2'
        code, cluster_type2 = self.client.cluster_type_create(
            self.org_id, valid_cluster_type)
        self.assertEqual(code, 201)
        code, res = self.client.cluster_type_prioritize(cluster_type2['id'])
        self.assertEqual(code, 200)
        for c_type in res['cluster_types']:
            if c_type['name'] == cluster_type2['name']:
                self.assertEqual(c_type['priority'], 1)

        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-west')
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        for r_id in [resource1['id'], resource2['id']]:
            code, resource = self.client.cloud_resource_get(r_id)
            self.assertEqual(code, 200)
            new_cluster_id = resource['cluster_id']
            self.assertNotEqual(old_cluster_id, new_cluster_id)

    def test_cluster_types_apply_keep_old(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 1)
        self.assertEqual(len(res['processed_cluster_types']), 1)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['id'], cluster_type['id'])
            self.assertEqual(c_type_info['clusters_count'], 1)
            self.assertEqual(c_type_info['clustered_resources_count'], 1)

        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val2'}, region='us-west')
        self.assertEqual(code, 201)
        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 2)
        self.assertEqual(len(res['processed_cluster_types']), 1)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['id'], cluster_type['id'])
            self.assertEqual(c_type_info['clusters_count'], 2)
            self.assertEqual(c_type_info['clustered_resources_count'], 2)

        for r_id in [resource1['id'], resource2['id']]:
            code, resource = self.client.cloud_resource_get(r_id)
            self.assertEqual(code, 200)
            self.assertIsNotNone(resource.get('cluster_id'))

    def test_cluster_types_reapply(self):
        resources_count = 4
        for _ in range(resources_count):
            code, resource = self.create_cloud_resource(
                self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
            self.assertEqual(code, 201)

        valid_cluster_type = self.valid_cluster_type.copy()
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        valid_cluster_type['name'] = 'high priority cluster'
        code, cluster_type2 = self.client.cluster_type_create(
            self.org_id, valid_cluster_type)
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_type_prioritize(cluster_type2['id'])
        self.assertEqual(code, 200)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], resources_count)
        self.assertEqual(len(res['processed_cluster_types']), 1)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['id'], cluster_type2['id'])
            self.assertEqual(c_type_info['clusters_count'], 1)
            self.assertEqual(c_type_info['clustered_resources_count'], resources_count)

        cluster = list(self.resources_collection.find(
            {'cluster_type_id': cluster_type2['id']}))
        self.assertEqual(len(cluster), 1)
        cluster = cluster[0]

        code, res = self.client.cloud_resource_list(cloud_account_id=self.cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertTrue(len(res.get('resources', [])) > 0)
        for resource in res['resources']:
            self.assertEqual(resource['cluster_id'], cluster['_id'])

    def test_cluster_types_apply_complex(self):
        cluster_types_count = 2
        clusters_per_cluster_type = 3
        resources_per_cluster = 5
        tag_key_template = 'type %s'
        tag_value_template = 'val %s'
        for a in range(cluster_types_count):
            tag_key = tag_key_template % a
            for b in range(clusters_per_cluster_type):
                tag_value = tag_value_template % b
                for c in range(resources_per_cluster):
                        code, _ = self.create_cloud_resource(
                            self.cloud_acc['id'], tags={tag_key: tag_value},
                            region='us-east')
                        self.assertEqual(code, 201)

        code, extra_resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'yet': 'another'}, region='us-east')
        self.assertEqual(code, 201)

        valid_cluster_type = self.valid_cluster_type.copy()
        for i in range(cluster_types_count):
            valid_cluster_type['name'] = str(i)
            valid_cluster_type['tag_key'] = tag_key_template % i
            code, _ = self.client.cluster_type_create(
                self.org_id, valid_cluster_type)
            self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(
            res['processed_resources'],
            cluster_types_count * clusters_per_cluster_type *
            resources_per_cluster)
        self.assertEqual(len(res['processed_cluster_types']),
                         cluster_types_count)
        for c_type_info in res['processed_cluster_types']:
            self.assertEqual(c_type_info['clusters_count'],
                             clusters_per_cluster_type)
            self.assertEqual(c_type_info['clustered_resources_count'],
                             clusters_per_cluster_type * resources_per_cluster)

        code, res = self.client.cloud_resource_list(
            cloud_account_id=self.cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertEqual(
            len(res.get('resources', [])), cluster_types_count *
            clusters_per_cluster_type * resources_per_cluster + 1)
        for resource in res['resources']:
            if resource['id'] == extra_resource['id']:
                self.assertIsNone(resource.get('cluster_id'))
            else:
                self.assertIsNotNone(resource.get('cluster_id'))

    def test_cluster_types_events(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        activity_param_tuples_1 = self.get_publish_activity_tuple(
            self.org_id, self.org['id'], 'organization',
            'cluster_types_processing_started', ANY)
        activity_param_tuples_2 = self.get_publish_activity_tuple(
            self.org_id, cluster_type['id'], 'cluster_type',
            'cluster_type_applied', ANY)
        activity_param_tuples_3 = self.get_publish_activity_tuple(
            self.org_id, self.org['id'], 'organization',
            'cluster_types_processing_done', ANY)

        p_publish_activities.assert_has_calls([
            call(*activity_param_tuples_1, add_token=True),
            call(*activity_param_tuples_2, add_token=True),
            call(*activity_param_tuples_3, add_token=True)
        ])

    def test_cluster_types_apply_deleted_cluster_type(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_type_delete(cluster_type['id'])
        self.assertEqual(code, 204)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(res['processed_resources'], 0)
        self.assertEqual(len(res['processed_cluster_types']), 0)

    def test_cluster_types_apply_deleted_cluster_type2(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.cluster_type_delete(cluster_type['id'])
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, self.org['id'], 'organization',
            'cluster_resources_deleted', {
                'object_name': self.org['name'],
                'cluster_type_name': cluster_type['name'],
                'cluster_type_id': cluster_type['id'],
                'modified_count': 1
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )
        clustered_resources = list(self.resources_collection.find(
            {'cluster_id': {'$exists': True}}))
        self.assertEqual(len(clustered_resources), 0)
        clusters = list(self.resources_collection.find(
            {'cluster_type_id': {'$exists': True}, 'deleted_at': 0}))
        self.assertEqual(len(clusters), 0)

        code, _ = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        clusters = list(self.resources_collection.find(
            {'cluster_type_id': {'$exists': True}, 'deleted_at': 0}))
        self.assertEqual(len(clusters), 1)
        clustered_resources = list(self.resources_collection.find(
            {'cluster_id': {'$exists': True}}))
        self.assertEqual(len(clustered_resources), 1)
        self.assertEqual(clustered_resources[0]['cluster_id'], clusters[0]['_id'])

    def test_cluster_types_apply_no_deleted_cluster_reuse(self):
        def get_clustered_resource():
            clustered_resources = list(self.resources_collection.find(
                {'cluster_id': {'$exists': True}}))
            self.assertEqual(len(clustered_resources), 1)
            return clustered_resources[0]

        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val', 'val': 'type'},
            region='us-east')
        self.assertEqual(code, 201)

        for tag_key in ['type', 'val']:
            valid_cluster_type = {
                'name': tag_key,
                'tag_key': tag_key
            }
            code, cluster_type = self.client.cluster_type_create(
                self.org_id, valid_cluster_type)
            self.assertEqual(code, 201)

        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        clustered_resource = get_clustered_resource()
        base_cluster_id = clustered_resource['cluster_id']

        code, _ = self.client.cluster_type_prioritize(cluster_type['id'])
        self.assertEqual(code, 200)
        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_type_deprioritize(cluster_type['id'])
        self.assertEqual(code, 200)
        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        clustered_resource = get_clustered_resource()
        current_cluster_id = clustered_resource['cluster_id']
        self.assertNotEqual(base_cluster_id, current_cluster_id)

    def test_cluster_types_apply_dependent_assignment_cleanup(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east',
            pool_id=self.org['pool_id'], employee_id=self.employee['id'])
        self.assertEqual(code, 201)
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, _ = self.client.cluster_types_apply(self.org_id)
        clustered_resources = list(self.resources_collection.find(
            {'cluster_id': {'$exists': True}}))
        self.assertEqual(len(clustered_resources), 1)
        self.assertEqual(clustered_resources[0].get('pool_id'),
                         self.org['pool_id'])
        self.assertEqual(clustered_resources[0].get('employee_id'),
                         self.employee['id'])

    def test_cluster_types_apply_assignment_request_invalidation(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        _, employee2 = self.client.employee_create(
            self.org_id, {'name': 'name2', 'auth_user_id': self.gen_id()})
        new_request = {
            'resource_id': resource['id'],
            'message': '=^__^=',
            'approver_id': employee2['id']}

        code, _ = self.client.assignment_request_create(
            self.org_id, new_request)
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        code, requests = self.client.assignment_request_list(
            organization_id=self.org_id)
        self.assertEqual(code, 200)
        self.assertListEqual(
            requests.get('assignment_requests', {}).get('outgoing', []), [])

    def test_cluster_types_apply_dependent_constraint_cleanup(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc['id'], tags={'type': 'val'}, region='us-east',
            pool_id=self.org['pool_id'], employee_id=self.employee['id'])
        self.assertEqual(code, 201)
        self.resources_collection.bulk_write([UpdateMany(
            filter={'_id': resource['id']},
            update={'$set': {'last_seen': int(datetime.utcnow().timestamp() - 5),
                             'active': True}},
        )])

        code, constraint = self.client.resource_constraint_create(
            resource['id'], {
                'limit': int(datetime.utcnow().timestamp()) + 3600,
                'type': 'ttl'
            })
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, _ = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        code, _ = self.client.resource_constraint_get(constraint['id'])
        self.assertEqual(code, 404)

    def test_cluster_types_apply_no_overlap_tags(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'],
            tags={'type': 'val', 'resource_1': 'resource_1', 'other': 'tag'},
            region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'],
            tags={'type': 'val', 'resource_2': 'resource_2'},
            region='us-west')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        clusters = list(self.resources_collection.find(
            {'cluster_type_id': {'$exists': True}}))
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0].get('tags', {})), 4)

    def test_cluster_types_apply_overlap_tags(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'],
            tags={'type': 'val', 'resource_1': 'resource_1'},
            region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'],
            tags={'type': 'val', 'resource_1': 'resource_2'},
            region='us-west')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        clusters = list(self.resources_collection.find(
            {'cluster_type_id': {'$exists': True}}))
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0].get('tags', {})), 1)

    def test_cluster_types_apply2(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc['id'],
            tags={'type': 'val', 'resource_1': 'resource_1'},
            region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc['id'], tags={}, region='us-west')
        self.assertEqual(code, 201)

        code, cluster_type = self.client.cluster_type_create(
            self.org_id, self.valid_cluster_type)
        self.assertEqual(code, 201)

        code, res = self.client.cluster_types_apply(self.org_id)
        self.assertEqual(code, 201)

        clustered_resources = list(self.resources_collection.find(
            {'cluster_id': {'$exists': True}}))
        self.assertEqual(len(clustered_resources), 1)
