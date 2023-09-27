import uuid
from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import encoded_tags

from tools.cloud_adapter.model import (InstanceResource, VolumeResource,
                                       PodResource, IpAddressResource)


REDISCOVER_TIME = 300


class TestCloudResourceApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.org1 = self.client.organization_create({'name': "org1"})
        self.client.pool_update(self.org1['pool_id'], {'limit': 100})
        _, self.org2 = self.client.organization_create({'name': "org2"})
        self.client.pool_update(self.org2['pool_id'], {'limit': 100})
        self.org1_id = self.org1['id']
        self.org2_id = self.org2['id']
        self.auth_user_1 = self.gen_id()
        _, self.employee_1 = self.client.employee_create(
            self.org1_id, {'name': 'Eliot Alderson',
                           'auth_user_id': self.auth_user_1})
        self.update_default_owner_for_pool(self.org1['pool_id'],
                                           self.employee_1['id'])
        self.auth_user_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.org2_id, {'name': 'John Joe', 'auth_user_id': self.auth_user_2})
        _, self.pool = self.client.pool_create(self.org1_id, {
            'name': 'sub', 'parent_id': self.org1['pool_id'], 'limit': 50
        })
        self.employee_id = self.employee_1['id']
        self.pool_id = self.pool['id']
        self.pool_name = self.pool['name']
        aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, self.cloud_acc1 = self.create_cloud_account(self.org1_id,
                                                       aws_cloud_acc, auth_user_id=self.auth_user_1)
        _, cloud_rules = self.client.rules_list(self.org1_id)
        self.set_allowed_pair(self.auth_user_1, cloud_rules['rules'][0]['pool_id'])
        _, self.cloud_acc2 = self.create_cloud_account(self.org2_id,
                                                       aws_cloud_acc, auth_user_id=self.auth_user_2)
        _, cloud_rules = self.client.rules_list(self.org2_id)
        self.set_allowed_pair(self.auth_user_2, cloud_rules['rules'][0]['pool_id'])
        self.cloud_acc1_id = self.cloud_acc1['id']
        self.cloud_acc2_id = self.cloud_acc2['id']
        self.valid_resource1 = {
            'cloud_resource_id': 'res_id_1',
            'name': 'resource_1',
            'resource_type': 'test',
            'region': 'test_region',
            'service_name': 'test_service',
            'tags': {
                'tn': 'tv'
            }
        }
        self.valid_resource2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test',
        }
        self.valid_resource3 = {
            'cloud_resource_id': 'res_id_3',
            'name': 'resource_3',
            'resource_type': 'test',
        }
        self.valid_body = {
            'resources': [
                self.valid_resource1,
                self.valid_resource2,
            ]
        }
        self.valid_hash_resource1 = {
            'cloud_resource_hash': 'res_id_4',
            'name': 'resource_4',
            'resource_type': 'testo',
        }
        self.valid_hash_resource2 = {
            'cloud_resource_hash': 'res_id_5',
            'name': 'resource_5',
            'resource_type': 'testo',
        }
        self.valid_hash_body = {
            'resources': [
                self.valid_hash_resource1,
                self.valid_hash_resource2,
            ]
        }

    def _check_response_body(self, response_body, valid_body,
                             search_field='cloud_resource_id'):
        self.assertEqual(len(response_body['resources']),
                         len(valid_body['resources']))
        valid_resources_by_id = {r[search_field]: r
                                 for r in valid_body['resources']}
        for created_resource in response_body['resources']:
            valid_resource = valid_resources_by_id[
                created_resource[search_field]]
            for k, v in valid_resource.items():
                self.assertEqual(created_resource[k], v)

    @staticmethod
    def _to_discovered_resource(cad_resource, active=True):
        obj = {}
        resource_type_map = {
            InstanceResource: 'Instance',
            VolumeResource: 'Volume',
            PodResource: 'K8s Pod',
            IpAddressResource: 'IP Address'
        }
        model = type(cad_resource)
        for field in model().fields(meta_fields_incl=False):
            val = getattr(cad_resource, field)
            if val is not None:
                obj[field] = val
        obj.pop('resource_id', None)
        obj['resource_type'] = resource_type_map.get(model)
        obj['last_seen'] = int(datetime.utcnow().timestamp())
        obj['active'] = active
        obj['meta'] = getattr(cad_resource, 'meta')
        return obj

    def test_create_resources(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body)
        self.assertEqual(code, 204)
        self.assertEqual(result, None)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_hash_body)
        self.assertEqual(code, 204)
        self.assertEqual(result, None)

    def test_create_with_response(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True)
        self.assertEqual(code, 200)
        self._check_response_body(result, self.valid_body)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_hash_body,
            return_resources=True)
        self.assertEqual(code, 200)
        self._check_response_body(result, self.valid_hash_body,
                                  search_field='cloud_resource_hash')

    def test_create_with_response_on_report_import(self):
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            '_id': self.gen_id(),
            'service_name': 'test_service',
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test',
            'recommendations': [{'fake': 'recommendation'}]
        }
        self.mongo_client.restapi.resources.insert_one(resource)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            is_report_import=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        self._check_response_body(result, self.valid_body)
        for r in result['resources']:
            self.assertEqual(r['recommendations'], {})

    def test_create_with_hash_update_with_resource_id(self):
        # resource created by diworker
        hash_ = 'hash'
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            'service_name': 'test_service',
            'cloud_resource_hash': hash_,
            'name': 'resource_2',
            'resource_type': 'testo'
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, is_report_import=True,
            behavior='skip_existing')
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_resource_hash'],
                         hash_)
        self.assertIsNone(result['resources'][0].get('cloud_resource_id'))

        # resource updated by resource-discovery
        res_id = 'res_id'
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            'service_name': 'test_service',
            'cloud_resource_id': res_id,
            'cloud_resource_hash': hash_,
            'name': 'resource_2',
            'resource_type': 'testo',
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(len(list(
            self.mongo_client.restapi.resources.find())), 1)
        self.assertEqual(result['resources'][0]['cloud_resource_hash'],
                         hash_)
        self.assertEqual(result['resources'][0]['cloud_resource_id'],
                         res_id)

    def test_create_with_resource_id_update_with_hash(self):
        # resource created by resource-discovery
        res_id = 'res_id'
        hash_ = 'hash'
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            'service_name': 'test_service',
            'cloud_resource_id': res_id,
            'cloud_resource_hash': hash_,
            'name': 'resource_2',
            'resource_type': 'testo',
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_resource_id'],
                         res_id)
        self.assertEqual(result['resources'][0]['cloud_resource_hash'],
                         hash_)

        # resource updated by diworker
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            'service_name': 'test_service',
            'cloud_resource_hash': hash_,
            'name': 'resource_2',
            'resource_type': 'testo'
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, is_report_import=True,
            behavior='skip_existing')
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(len(list(
            self.mongo_client.restapi.resources.find())), 1)
        self.assertEqual(result['resources'][0]['cloud_resource_hash'],
                         hash_)
        self.assertEqual(result['resources'][0]['cloud_resource_id'],
                         res_id)

    def test_create_without_resource_id_and_hash(self):
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            'service_name': 'test_service',
            'name': 'resource_2',
            'resource_type': 'testo'
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, is_report_import=True,
            behavior='skip_existing')
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['error_code'], 'OE0517')

    def test_dismissed_recommendation_on_report_import(self):
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            '_id': self.gen_id(),
            'service_name': 'test_service',
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'test',
            'dismissed_recommendations': {'run_timestamp': 123}
        }
        self.mongo_client.restapi.resources.insert_one(resource)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            is_report_import=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        self._check_response_body(result, self.valid_body)
        for r in result['resources']:
            self.assertEqual(r['dismissed_recommendations'], {})

    def test_create_resource_with_system_tags_first(self):
        system_tag = {"aws:test:tag": "sometext"}
        tag = self.valid_resource1.pop('tags')
        self.valid_resource1["tags"] = system_tag
        publish_discovered_cluster_resource_activity = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        self.assertDictEqual(resource['tags'], {'aws:test:tag': 'sometext'})
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org1_id, self.cloud_acc1_id, 'cloud_account',
            'resources_discovered', {
                'object_name': self.cloud_acc1['name'],
                'stat': {'total': 1, 'clusters': [], 'clustered': 0}
            })
        publish_discovered_cluster_resource_activity.assert_called_once_with(
            *activity_param_tuples, add_token=True)

        self.valid_resource1["tags"] = tag
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, behavior='update_existing', return_resources=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        self.assertDictEqual(resource['tags'], {'aws:test:tag': 'sometext',
                                                'tn': 'tv'})

    def test_create_resource_with_system_tags_after_discover(self):
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        self.assertDictEqual(resource['tags'], {'tn': 'tv'})

        report_import_tag = {'aws:test:tag': 'sometext',
                             'purpose': 'test', 'tn': 'tv'}
        self.valid_resource1['tags'] = report_import_tag
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, behavior='skip_existing', return_resources=True,
            is_report_import=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        self.assertDictEqual(resource['tags'], {'aws:test:tag': 'sometext',
                                                'purpose': 'test', 'tn': 'tv'})

    def test_error_existing(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [self.valid_resource2]})
        self.assertEqual(code, 204)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body)
        self.assertEqual(code, 400)

        _, result = self.client.cloud_resource_list(self.cloud_acc1_id)
        self.assertEqual(len(result['resources']), 1)

    def test_skip_existing(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [self.valid_resource2]})
        self.assertEqual(code, 204)

        resource2_updated = dict(self.valid_resource2)
        resource2_updated['name'] = 'resource_2_updated'
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {'resources': [self.valid_resource1, resource2_updated]},
            behavior='skip_existing',
            return_resources=True
        )
        self.assertEqual(code, 200)
        self._check_response_body(result, self.valid_body)

    def test_update_existing(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [self.valid_resource2]})
        self.assertEqual(code, 204)

        resource2_updated = dict(self.valid_resource2)
        resource2_updated['name'] = 'resource_2_updated'
        resource2_updated['service_name'] = 'special_service'
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {'resources': [self.valid_resource1, resource2_updated]},
            behavior='update_existing',
            return_resources=True
        )
        self.assertEqual(code, 200)
        valid_body = {'resources': [
            self.valid_resource1,
            resource2_updated,
        ]}
        self._check_response_body(result, valid_body)

    def test_invalid_body_type(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, [], set_allowed=False)
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['reason'],
                         'Request body should be a dictionary')

    def test_invalid_behavior(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, behavior='=^__^=')
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['reason'],
                         'Behavior =^__^= is not supported')

    def test_resources_not_provided(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {}, set_allowed=False)
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['reason'],
                         'resources is not provided')

    def test_invalid_resources_type(self):
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': 0xBADF00D}, set_allowed=False)
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['reason'],
                         'resources should be a list')

    def test_unexpected_parameters(self):
        body = {
            'resources': [self.valid_resource1],
            'ZZ': ':wq'
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body)
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['reason'],
                         'Unexpected parameters: ZZ')

    def test_different_cloud_accs_scenario_1(self):
        body = {
            'resources': [self.valid_resource1],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_account_id'],
                         self.cloud_acc1_id)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc2_id, body, behavior='error_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_account_id'],
                         self.cloud_acc2_id)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc2_id, body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_account_id'],
                         self.cloud_acc2_id)

    def test_different_cloud_accs_scenario_2(self):
        body = {
            'resources': [self.valid_resource1],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_account_id'],
                         self.cloud_acc1_id)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc2_id, body, behavior='skip_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(result['resources']), 1)
        self.assertEqual(result['resources'][0]['cloud_account_id'],
                         self.cloud_acc2_id)

    @patch('rest_api.rest_api_server.controllers.rule_apply.CloudIsCondition.match')
    def test_update_existing_with_wrong_tags(self, p_rule_apply):
        p_rule_apply.return_value = False
        resource = {
            'cloud_resource_id': 'i-aaa',
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'us-1',
            'name': 'Instance1',
            'resource_type': 'Instance',
            'meta': {'flavor': 't1-tiny'},
            'pool_id': str(uuid.uuid4()),
            'employee_id': str(uuid.uuid4()),
            'tags': {},
        }
        body = {
            'resources': [resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='update_existing',
            return_resources=True, set_allowed=False)
        self.assertEqual(code, 200)
        self.assertEqual(result['resources'][0].get('pool_id'),
                         self.org1['pool_id'])
        self.assertEqual(result['resources'][0].get('employee_id'),
                         self.employee_1['id'])

    def test_update_existing_with_valid_tags(self):
        resource = {
            'cloud_resource_id': 'i-aaa',
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'us-1',
            'name': 'Instance1',
            'resource_type': 'Instance',
            'meta': {'flavor': 't1-tiny'},
            'pool_id': self.pool_id,
            'employee_id': self.employee_id,
            'tags': {},
        }
        body = {
            'resources': [resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(result['resources'][0].get('pool_id'), self.pool_id)
        self.assertEqual(result['resources'][0].get('employee_id'), self.employee_id)

    def test_update_existing_without_name(self):
        resource = {
            'cloud_resource_id': 'i-aaa',
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'us-1',
            'resource_type': 'Instance',
            'meta': {'flavor': 't1-tiny'},
            'tags': {},
        }
        body = {
            'resources': [resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertIsNone(result['resources'][0].get('name'))

    def test_update_existing_no_reassignment(self):
        instance = InstanceResource(
            cloud_resource_id='i-aaa',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='Instance1',
            flavor='t1-tiny',
            pool_id=self.pool_id,
            owner_id=self.employee_id,
            tags={},
            spotted=True
        )
        resource = self._to_discovered_resource(instance)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]}, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)

        _, employee = self.client.employee_create(
            self.org1_id, {'name': 'Eliot Aldersome'})
        _, pool = self.client.pool_create(self.org1_id, {
            'name': 'sub2', 'parent_id': self.org1['pool_id'], 'limit': 50
        })
        resource['pool_id'] = pool['id']
        resource['owner_id'] = employee['id']
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]}, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(result['resources'][0].get('pool_id'), self.pool_id)
        self.assertEqual(result['resources'][0].get('employee_id'), self.employee_id)

    def test_update_existing_min_payload(self):
        resource = {
            'cloud_resource_id': 'i-aaa',
            'cloud_account_id': self.cloud_acc1_id,
            'resource_type': 'Instance',
        }
        body = {
            'resources': [resource],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertNotEqual(len(result.get('resources', [])), 0)

    def test_update_existing_instance_spot(self):
        instance = InstanceResource(
            cloud_resource_id='i-spot',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='Instance1',
            flavor='t1-tiny',
            tags={},
            spotted=True
        )
        body = {
            'resources': [self._to_discovered_resource(instance)],
        }
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, body, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(result['resources'][0]['meta']['spotted'], True)

    def test_update_existing_volume_attached(self):
        volume = VolumeResource(
            cloud_resource_id='volume-id1',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='volume1',
            tags={},
            size=1,
            volume_type='type',
            attached=False,
        )
        resource = self._to_discovered_resource(volume)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            behavior='update_existing', return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(result['resources'][0]['meta']['last_attached'], 0)
        self.assertEqual(result['resources'][0]['meta']['attached'], False)

        volume.attached = True
        resource = self._to_discovered_resource(volume)
        cache_update_time1 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time1)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]}, behavior='update_existing',
                return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(result['resources'][0]['meta']['last_attached'],
                             int(cache_update_time1))
            self.assertEqual(result['resources'][0]['meta']['attached'], True)

        cache_update_time2 = cache_update_time1 + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time2)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(result['resources'][0]['meta']['last_attached'],
                             int(cache_update_time2))
            self.assertEqual(result['resources'][0]['meta']['attached'], True)

        volume.attached = False
        resource = self._to_discovered_resource(volume)
        cache_update_time3 = cache_update_time2 + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time3)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(result['resources'][0]['meta']['last_attached'],
                             int(cache_update_time2))
            self.assertEqual(result['resources'][0]['meta']['attached'], False)

    def test_update_existing_instance_stopped_allocated(self):
        instance = InstanceResource(
            cloud_resource_id='i-inst1',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='instance1',
            flavor='t1-tiny',
            tags={},
            stopped_allocated=True,
            image_id='image_id_mock'
        )
        resource = self._to_discovered_resource(instance)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            behavior='update_existing', return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(
            result['resources'][0]['meta']['last_seen_not_stopped'], 0)
        self.assertEqual(
            result['resources'][0]['meta']['image_id'], 'image_id_mock')
        self.assertEqual(
            result['resources'][0]['meta']['stopped_allocated'], True)

        instance.stopped_allocated = False
        resource = self._to_discovered_resource(instance)
        cache_update_time1 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time1)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time1))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)

        cache_update_time2 = cache_update_time1 + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time2)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time2))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)

        instance.stopped_allocated = True
        resource = self._to_discovered_resource(instance)
        cache_update_time3 = cache_update_time2 + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time3)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time2))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], True)

    def test_update_existing_stopped_allocated_is_none(self):
        instance = InstanceResource(
            cloud_resource_id='i-inst1',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='instance1',
            flavor='t1-tiny',
            tags={},
            stopped_allocated=True,
        )
        resource = self._to_discovered_resource(instance)
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            behavior='update_existing', return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(
            result['resources'][0]['meta']['last_seen_not_stopped'], 0)
        self.assertEqual(
            result['resources'][0]['meta']['stopped_allocated'], True)

        instance.stopped_allocated = None
        resource = self._to_discovered_resource(instance)
        with freeze_time(datetime.fromtimestamp(int(datetime.utcnow().timestamp()))):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'], 0)
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], True)

        instance.stopped_allocated = False
        resource = self._to_discovered_resource(instance)
        cache_update_time1 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time1)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time1))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)

        # verify that last_seen_not_stopped updated with new discover
        cache_update_time2 = cache_update_time1 + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time2)):
            code, result = self.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time2))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)

    def test_resource_create_resource_without_stopped_allocated(self):
        # we get this case if we create resource from diworker before first discover
        instance = InstanceResource(
            cloud_resource_id='i-inst1',
            cloud_account_id=self.cloud_acc1_id,
            region='us-1',
            name='instance1',
            flavor='t1-tiny',
            tags={},
            stopped_allocated=None
        )
        resource = self._to_discovered_resource(instance)
        code, result = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            behavior='update_existing', return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(
            result['resources'][0]['meta']['last_seen_not_stopped'], 0)
        self.assertEqual(
            result['resources'][0]['meta']['stopped_allocated'], False)
        # if in the first discover we got invalid status from Azure
        instance.stopped_allocated = None
        resource = self._to_discovered_resource(instance)
        with freeze_time(datetime.fromtimestamp(int(datetime.utcnow().timestamp()))):
            code, result = self.client.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]}, behavior='update_existing',
                return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'], 0)
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)
        instance.stopped_allocated = True
        resource = self._to_discovered_resource(instance)
        cache_update_time1 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time1)):
            code, result = self.client.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]}, behavior='update_existing',
                return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'], 0)
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], True)
        instance.stopped_allocated = False
        resource = self._to_discovered_resource(instance)
        cache_update_time2 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time2)):
            code, result = self.client.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time2))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], False)
        instance.stopped_allocated = True
        resource = self._to_discovered_resource(instance)
        cache_update_time3 = datetime.utcnow().timestamp() + REDISCOVER_TIME + 1
        with freeze_time(datetime.fromtimestamp(cache_update_time3)):
            code, result = self.client.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                behavior='update_existing', return_resources=True)
            self.assertEqual(code, 200)
            self.assertEqual(
                result['resources'][0]['meta']['last_seen_not_stopped'],
                int(cache_update_time2))
            self.assertEqual(
                result['resources'][0]['meta']['stopped_allocated'], True)

    def test_resource_with_invalid_employee_and_pool_event(self):
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        params = {
            'cloud_resource_id': 'res_id',
            'name': 'myres',
            'resource_type': 'test1',
            'employee_id': str(uuid.uuid4()),
            'pool_id': str(uuid.uuid4())
        }
        self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [params]}, set_allowed=False)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org1_id, self.cloud_acc1['id'], 'cloud_account',
            'root_assigned_resource', {
                'object_name': self.cloud_acc1['name'],
                'resource_type': params['resource_type'],
                'res_name': params['name'],
                'cloud_resource_id': params['cloud_resource_id'],
                'level': 'WARNING'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        p_publish_activities_2 = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [params]},
            behavior='skip_existing', set_allowed=False)
        p_publish_activities_2.assert_not_called()

        params2 = {
            'cloud_resource_id': 'res_id_2',
            'name': 'myres2',
            'resource_type': 'test2',
            'employee_id': str(uuid.uuid4()),
            'pool_id': str(uuid.uuid4())
        }
        p_publish_activities_3 = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [params, params2]},
            behavior='skip_existing', set_allowed=False)
        activity_param_tuples_3 = self.get_publish_activity_tuple(
            self.org1_id, self.cloud_acc1['id'], 'cloud_account',
            'root_assigned_resource', {
                'object_name': self.cloud_acc1['name'],
                'resource_type': params2['resource_type'],
                'res_name': params2['name'],
                'cloud_resource_id': params2['cloud_resource_id'],
                'level': 'WARNING'
            })
        p_publish_activities_3.assert_called_once_with(
            *activity_param_tuples_3, add_token=True
        )

    def test_non_clustered_rediscover(self):
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        code, _ = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            self.assertIsNone(rss.get('cluster_id'))
        self._check_response_body(res, self.valid_body)

    def _check_cluster(self, cluster_type, cluster_id, tag_value, active=False, tags=None):
        cluster = list(self.resources_collection.find({'_id': cluster_id}))
        self.assertEqual(len(cluster), 1)
        cluster = cluster[0]
        self.assertIsNone(cluster.get('cloud_account_id'))
        self.assertIsNone(cluster.get('region'))
        self.assertIsNone(cluster.get('name'))
        self.assertIsNone(cluster.get('cloud_console_link'))
        self.assertEqual(cluster['resource_type'], cluster_type['name'])
        self.assertEqual(cluster['organization_id'], cluster_type['organization_id'])
        self.assertEqual(cluster['cluster_type_id'], cluster_type['id'])
        self.assertEqual(cluster['active'], active)
        self.assertEqual(cluster['cloud_resource_id'],
                         '%s/%s' % (cluster_type['name'], tag_value))
        if tags:
            self.assertEqual(len(tags), len(cluster.get('tags', {})))
            tags = encoded_tags(tags)
            for k, v in tags.items():
                self.assertEqual(v, cluster.get('tags', {}).get(k))
        elif tags is not None:
            self.assertEqual(tags, cluster.get('tags', {}))

    def test_no_cluster(self):
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            self.assertIsNone(rss.get('cluster_id'))

    def test_non_clustered(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tnn'})
        self.assertEqual(code, 201)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            self.assertIsNone(rss.get('cluster_id'))

    def test_clustered(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        cluster_id = None
        for rss in res['resources']:
            if cluster_id is None:
                cluster_id = rss.get('cluster_id')
        self.assertIsNotNone(cluster_id)
        self._check_cluster(ct, cluster_id, 'tv')

    def test_clustered_priority(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        code, _ = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct2', 'tag_key': 'tn2'})
        self.assertEqual(code, 201)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        cluster_id = None
        for rss in res['resources']:
            if cluster_id is None:
                cluster_id = rss.get('cluster_id')
        self.assertIsNotNone(cluster_id)
        self._check_cluster(ct, cluster_id, 'tv')

    def test_cluster_tags(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        common_tags = {
            'tn': 'tv',
            'tn2': 'tv',
        }
        conflict_tag_name = 'tn3'
        valid_resource1 = self.valid_resource1
        valid_resource1['tags'] = {
            conflict_tag_name: 'tv1', 'tn4': 'tv', **common_tags}
        valid_resource2 = self.valid_resource2
        valid_resource2['tags'] = {
            conflict_tag_name: 'tv2', 'tn5': 'tv', **common_tags}
        valid_resource3 = self.valid_resource3
        valid_resource3['tags'] = {conflict_tag_name: 'tv1', **common_tags}
        valid_body = {
            'resources': [
                valid_resource1,
                valid_resource2,
                valid_resource3,
            ]}

        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        cluster_tags = valid_resource1['tags']
        cluster_tags.update(valid_resource2['tags'])
        cluster_tags.pop(conflict_tag_name)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags=cluster_tags)

    def test_cluster_system_tags(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'aws:tn'})
        self.assertEqual(code, 201)

        tags = {'aws:tn': 'aws:tv', 'tn': 'tv'}
        valid_resource = self.valid_resource1.copy()
        valid_resource['tags'] = tags.copy()

        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {
                'resources': [
                    valid_resource
                ]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        cluster_id = None
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'aws:tv', tags=tags)

        valid_resource['tags'].pop('aws:tn')
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {
                'resources': [
                    valid_resource
                ]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            new_cluster_id = rss.get('cluster_id')
            self.assertEqual(cluster_id, new_cluster_id)
            self._check_cluster(ct, cluster_id, 'aws:tv', tags=tags)

    def test_cluster_active(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        common_tags = {
            'tn': 'tv',
            'tn2': 'tv',
        }
        resources = []
        for cl_id in ['i-aaa', 'i-bbb']:
            instance = InstanceResource(
                cloud_resource_id=cl_id,
                cloud_account_id=self.cloud_acc1_id,
                region='us-1',
                name=cl_id,
                flavor='t1-tiny',
                tags=common_tags,
                spotted=False
            )
            resources.append(instance)
        payload = []
        for active, instance in zip([False, True], resources):
            resource = self._to_discovered_resource(instance, active)
            payload.append(resource)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': payload},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags=common_tags, active=True)

        payload.clear()
        for instance in resources:
            resource = self._to_discovered_resource(instance, False)
            payload.append(resource)
        code, res2 = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': payload},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags=common_tags)

    def test_cluster_reuse(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        common_tags = {
            'tn': 'tv',
        }
        valid_resource1 = self.valid_resource1
        valid_resource1['tags'] = common_tags
        valid_resource2 = self.valid_resource2
        valid_resource2['tags'] = common_tags
        valid_body = {
            'resources': [
                valid_resource1
            ]}

        code, _ = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, valid_body, return_resources=False,
            behavior='update_existing')
        self.assertEqual(code, 204)

        valid_body['resources'].append(valid_resource2)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)

        cluster_ids = []
        for rss in res['resources']:
            cluster_ids.append(rss.get('cluster_id'))
        self.assertEqual(len(cluster_ids), len(res['resources']))
        self.assertEqual(cluster_ids[0], cluster_ids[1])

    def test_cluster_dates(self):
        def get_cluster(cluster_type_id):
            cluster = list(self.resources_collection.find(
                {'cluster_type_id': cluster_type_id}))
            self.assertEqual(len(cluster), 1)
            return cluster[0]

        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)

        resources = []
        for cl_id in ['i-aaa', 'i-bbb']:
            instance = InstanceResource(
                cloud_resource_id=cl_id,
                cloud_account_id=self.cloud_acc1_id,
                region='us-1',
                name=cl_id,
                flavor='t1-tiny',
                tags={'tn': 'tv'},
                spotted=False
            )
            resources.append(instance)

        rss = self._to_discovered_resource(resources[0])
        rss['first_seen'] = rss['last_seen'] - 1000
        code, _ = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [rss]},
            return_resources=False, behavior='update_existing')
        self.assertEqual(code, 204)
        cluster_1 = get_cluster(ct['id'])

        rss = self._to_discovered_resource(resources[1])
        rss['last_seen'] += 10000
        rss['first_seen'] = rss['last_seen'] - 20000
        code, _ = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [rss]},
            return_resources=False, behavior='update_existing')
        self.assertEqual(code, 204)
        cluster_2 = get_cluster(ct['id'])
        for k in ['first_seen', 'last_seen']:
            self.assertNotEqual(cluster_1[k], cluster_2[k])
        self.assertEqual(cluster_1['created_at'], cluster_2['created_at'])

    def test_cluster_only_new(self):
        code, _ = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            self.assertIsNone(rss.get('cluster_id'))

    def test_cluster_tag_lose(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        common_tags = {
            'tn': 'tv',
        }
        valid_resource1 = self.valid_resource1
        valid_resource1['tags'] = common_tags

        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [valid_resource1]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags=common_tags)

        valid_resource1['tags'] = {}
        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [valid_resource1]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags={})

    def test_cluster_cloud_resource_hash(self):
        code, ct = self.client.cluster_type_create(
            self.org1_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        common_tags = {
            'tn': 'tv',
        }
        valid_resource = self.valid_hash_resource1.copy()
        valid_resource['tags'] = common_tags

        code, res = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [valid_resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        self.assertEqual(len(res['resources']), 1)
        for rss in res['resources']:
            cluster_id = rss.get('cluster_id')
            self.assertIsNotNone(cluster_id)
            self._check_cluster(ct, cluster_id, 'tv', tags=common_tags)

    def test_create_resources_threshold_fields(self):
        for fields in [
            [], ['first_seen'], ['last_seen'], ['first_seen', 'last_seen']
        ]:
            for behavior in ['skip_existing', 'error_existing', 'update_existing']:
                resource = self.valid_resource2.copy()
                resource['cloud_resource_id'] = 'some_resource_%s' % str(uuid.uuid4())
                for field in fields:
                    resource[field] = int(datetime.utcnow().timestamp())
                valid_body = {
                    'resources': [
                        resource
                    ]}
                code, result = self.cloud_resource_create_bulk(
                    self.cloud_acc1_id, valid_body, return_resources=True, behavior=behavior)
                self.assertEqual(code, 200)
                self.assertIsNotNone(result.get('resources'))
                for r in result.get('resources'):
                    for f in ['first_seen', 'last_seen']:
                        self.assertIsNotNone(r.get(f), f)

    def test_check_pod_extra_fields_saved(self):
        pod = PodResource(
            cloud_resource_id=self.gen_id(),
            name='kube-pod-name-fc2cbf5f',
            cloud_account_id=self.cloud_acc1_id,
            region='ubuntu-node1',
            created_by_kind='ReplicaSet',
            created_by_name='job-123',
            host_ip='192.168.1.1',
            instance_address='192.168.11.1',
            k8s_node='ubuntu-node1',
            k8s_namespace='kube-system',
            k8s_service='monitoring-nginx',
            pod_ip='10.4.3.2',
            tags={"eks_amazonaws_com_component": "coredns",
                  "k8s_app": "kube-dns", "pod_template_hash": "6548845887"}
        )
        resource = self._to_discovered_resource(pod)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['created_by_kind'], 'ReplicaSet')
            self.assertEqual(rss['created_by_name'], 'job-123')
            self.assertEqual(rss['meta']['host_ip'], '192.168.1.1')
            self.assertEqual(rss['meta']['instance_address'], '192.168.11.1')
            self.assertEqual(rss['k8s_node'], 'ubuntu-node1')
            self.assertEqual(rss['k8s_namespace'], 'kube-system')
            self.assertEqual(rss['k8s_service'], 'monitoring-nginx')
            self.assertDictEqual(rss['tags'],
                                 {"eks_amazonaws_com_component":
                                  "coredns", "k8s_app": "kube-dns",
                                  "pod_template_hash": "6548845887"})
        # second discover
        pod.pod_ip = '10.4.3.7'
        pod.tags = {'one_label': 'label_value'}
        resource = self._to_discovered_resource(pod)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['meta']['pod_ip'], '10.4.3.7')
            self.assertDictEqual(rss['tags'], {'one_label': 'label_value'})
        # skip existing
        pod.k8s_namespace = 'new_namespace'
        resource = self._to_discovered_resource(pod)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['k8s_namespace'], 'kube-system')

        pod.k8s_service = 'new_service'
        resource = self._to_discovered_resource(pod)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['k8s_service'], 'monitoring-nginx')

        pod.k8s_service = 'new_service'
        resource = self._to_discovered_resource(pod)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['k8s_service'], 'new_service')

    def test_check_ip_address_extra_fields_saved(self):
        ip_address = IpAddressResource(
            cloud_resource_id=self.gen_id(),
            cloud_account_id=self.cloud_acc1_id,
            name='ip_address_name',
            region='eu-central-us',
            instance_id='i-0eb60cb897386a37e',
            available=False
        )
        resource = self._to_discovered_resource(ip_address)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['meta']['instance_id'], 'i-0eb60cb897386a37e')
            self.assertEqual(rss['meta']['available'], False)
        # skip existing
        ip_address.instance_id = 'i-0eb60cb897334a23a'
        resource = self._to_discovered_resource(ip_address)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['meta']['instance_id'], 'i-0eb60cb897386a37e')

        ip_address.name = 'another_ip_address_name'
        resource = self._to_discovered_resource(ip_address)
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='update_existing')
        self.assertEqual(code, 200)
        for rss in response['resources']:
            self.assertEqual(rss['name'], 'another_ip_address_name')

    def test_env_properties(self):
        self.valid_body['resources'][0]['env_properties'] = {'field': 'value'}
        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body)
        self.assertEqual(code, 400)
        self.assertEqual(result['error']['error_code'], 'OE0212')

    def test_skip_existing_update_service_fields(self):
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)

        updates = {
            'service_name': 'some service',
        }
        self.valid_resource1.update(updates)
        self.valid_resource1['name'] = 'another_name'
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        for k, v in updates.items():
            self.assertEqual(v, resource[k])
        self.assertNotEqual(resource['name'], 'another_name')

    def test_skip_existing_update_meta(self):
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)

        updates = {
            'meta': {
                'os': 'win',
                'preinstalled': 'preinstalled',
            }
        }
        self.valid_resource1.update(updates)
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    self.valid_resource1
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        updates['meta']['cloud_console_link'] = None
        self.assertDictEqual(resource['meta'], updates['meta'])

    def test_update_existing_update_meta(self):
        params = self.valid_resource1.copy()
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    params
                ]
            }, return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 200)

        updates = {
            'meta': {
                'os': 'win',
                'preinstalled': 'preinstalled',
            }
        }
        params.update(updates)
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id,
            {
                'resources': [
                    params
                ]
            }, return_resources=True, behavior='update_existing',
            is_report_import=True)
        self.assertEqual(code, 200)
        resource = response['resources'][0]
        for k, v in updates['meta'].items():
            self.assertEqual(v, resource['meta'][k])

    def test_activities_task(self):
        m_task = patch('rest_api.rest_api_server.controllers.base.'
                       'BaseController.publish_activities_task').start()
        resource = {
            'cloud_account_id': self.cloud_acc1_id,
            'region': 'test_region',
            '_id': self.gen_id(),
            'service_name': 'test_service',
            'cloud_resource_id': 'res_id_2',
            'name': 'resource_2',
            'resource_type': 'Instance',
            'recommendations': [{'some': 'recommendation'}],
            'pool_id': self.org1['pool_id'],
            'deleted_at': 0,
            'shareable': True
        }
        self.mongo_client.restapi.resources.insert_one(resource)
        alert = {
            'pool_id': self.org1['pool_id'],
            'based': 'env_change',
            'threshold': 0,
            'contacts': [{'slack_team_id': 'team_id',
                          'slack_channel_id': 'channel_id'}]
        }
        code, alert = self.client.alert_create(self.org1['id'], alert)
        self.assertEqual(code, 201)

        code, result = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, self.valid_body, return_resources=True,
            is_report_import=True, behavior='skip_existing')
        self.assertEqual(code, 200)
        self.assertEqual(m_task.call_args_list[1][0][3],
                         'env_active_state_changed')

    def test_create_with_none_in_meta(self):
        code, resp = self.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [{
                'cloud_resource_id': 'res_id',
                'resource_type': 'Instance',
                'meta': {'preinstalled': 'NA',
                         'flavor': None}
            }]}, behavior='update_existing',
            return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(resp['resources']), 1)
        resource = resp['resources'][0]
        self.assertIn('preinstalled', resource['meta'])
        self.assertNotIn('flavor', resource['meta'])

    def test_create_meta_field_not_in_meta(self):
        os_ = 'os'
        resource = self.valid_resource1.copy()
        resource['resource_type'] = 'Instance'
        resource['os'] = os_
        code, response = self.client.cloud_resource_create_bulk(
            self.cloud_acc1_id, {'resources': [resource]},
            return_resources=True, behavior='skip_existing',
            is_report_import=True)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_resource_name_len(self):
        resource = self.valid_resource1.copy()
        for behavior in ['skip_existing', 'update_existing']:
            resource['name'] = '1' * 512
            code, response = self.client.cloud_resource_create_bulk(
                self.cloud_acc1_id, {'resources': [resource]},
                return_resources=True, behavior=behavior,
                is_report_import=True)
            self.assertEqual(code, 200)
            self.assertEqual(response['resources'][0]['name'],
                             resource['name'])
            for name in ['', '1' * 513]:
                resource['name'] = name
                code, response = self.client.cloud_resource_create_bulk(
                    self.cloud_acc1_id, {'resources': [resource]},
                    return_resources=True, behavior=behavior,
                    is_report_import=True)
                self.assertEqual(code, 400)
                self.verify_error_code(response, 'OE0215')
