import uuid

from rest_api_server.controllers.cluster_type import ClusterTypeController
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.models.db_factory import DBType, DBFactory
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.enums import PoolPurposes
from cloud_adapter.model import InstanceResource, PodResource, IpAddressResource

from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch


class TestCloudResourcesDiscoveryApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        self.session = BaseDB.session(engine)()
        _, self.org = self.client.organization_create(
            {'name': "organization_test"})
        self.client.pool_update(self.org['pool_id'], {'limit': 200})
        self.valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            },
        }
        self.valid_azure_cloud_acc = {
            'name': 'azure',
            'type': 'azure_cnr',
            'config': {
                'client_id': 'client',
                'secret': 'secret',
                'tenant': 'tenant',
                'subscription_id': 'subscription',
            }
        }
        self.org_id = self.org['id']
        self.auth_user_1 = self.gen_id()
        _, employee = self.client.employee_create(
            self.org_id, {'name': 'Eliot Alderson',
                          'auth_user_id': self.auth_user_1})
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, auth_user_id=self.auth_user_1)
        self.cloud_acc_id = cloud_account['id']
        self.valid_aws_cloud_acc['name'] = 'my_cloud_acc2'
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_cloud_acc, auth_user_id=self.auth_user_1)
        self.cloud_acc_id2 = cloud_account['id']
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_azure_cloud_acc, auth_user_id=self.auth_user_1)
        self.azure_cloud_acc_id = cloud_account['id']
        self.valid_employee = {
            'name': 'Eliot Alderson',
        }
        _, employee = self.client.employee_create(
            self.org_id, self.valid_employee)
        _, pool = self.client.pool_create(self.org_id, {
            'name': 'sub', 'parent_id': self.org['pool_id'], 'limit': 100
        })
        self.employee_id = employee['id']
        self.pool_id = pool['id']
        self.pool_name = pool['name']

    def mock_assign_resources(self, data):
        for k, v in data.items():
            owner_id, pool_id = v
            self.resources_collection.update_one(
                filter={
                    '_id': k,
                },
                update={'$set': {
                    'employee_id': owner_id,
                    'pool_id': pool_id
                }}
            )

    def get_instances(self):
        i1 = InstanceResource(
            cloud_resource_id='i-aaa',
            cloud_account_id=self.cloud_acc_id,
            region='us-1',
            name='Instance1',
            flavor='t1-tiny',
            tags={},
        )
        i2 = InstanceResource(
            cloud_resource_id='i-aab',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='instance2',
            flavor='t1-tiny',
            tags={},
        )
        i3 = InstanceResource(
            cloud_resource_id='i-ccb',
            cloud_account_id=self.cloud_acc_id2,
            region='us-2',
            name='Instance3',
            flavor='t1-tiny',
            tags={},
        )
        i4 = InstanceResource(
            cloud_resource_id='i-cbe',
            cloud_account_id=self.cloud_acc_id2,
            region='us-2',
            name='INstance7',
            flavor='t777-superlarge',
            tags={},
        )
        i5 = InstanceResource(
            cloud_resource_id='instance_id',
            cloud_account_id=self.azure_cloud_acc_id,
            region='regionname',
            name='azureVM',
            flavor='flavor',
            tags={},
        )
        return [i1, i2, i3, i4, i5]

    def get_kubernetes_pods(self):
        p1 = PodResource(
            cloud_resource_id=self.gen_id(),
            name='kube-pod-name-fc2cbf5f',
            cloud_account_id=self.cloud_acc_id,
            region='ubuntu-node1',
            created_by_kind='ReplicaSet',
            created_by_name='job-123',
            host_ip='192.168.1.1',
            instance_address='192.168.11.1',
            k8s_node='ubuntu-node1',
            k8s_namespace='kube-system',
            k8s_service='kube-dns',
            pod_ip='10.4.3.2',
            tags={"eks_amazonaws_com_component": "coredns",
                  "k8s_app": "kube-dns",
                  "pod_template_hash": "6548845887"},
        )
        p2 = PodResource(
            cloud_resource_id=self.gen_id(),
            name='kube-pod-name-4a28b97a',
            cloud_account_id=self.cloud_acc_id,
            region='ubuntu-node2',
            created_by_kind='ReplicaSet',
            created_by_name='job-124',
            host_ip='192.168.1.2',
            instance_address='192.168.11.2',
            k8s_node='ubuntu-node2',
            k8s_namespace='default',
            k8s_service='monitoring-nginx',
            pod_ip='10.4.3.3',
            tags={"eks_amazonaws_com_component": "coredns",
                  "k8s_app": "kube-dns", "pod_template_hash": "6548845887"},
        )
        p3 = PodResource(
            cloud_resource_id=self.gen_id(),
            name='kube-pod-name-75d7259e',
            cloud_account_id=self.cloud_acc_id2,
            region='ubuntu-node3',
            created_by_kind='ReplicaSet',
            created_by_name='job-125',
            host_ip='192.168.1.3',
            instance_address='192.168.11.3',
            k8s_node='ubuntu-node3',
            k8s_namespace='default',
            k8s_service='monitoring-nginx',
            pod_ip='10.4.3.4',
            tags={"eks_amazonaws_com_component": "coredns",
                  "k8s_app": "kube-dns", "pod_template_hash": "6548845887"},
        )
        return [p1, p2, p3]

    def get_ip_addresses(self):
        ip1 = IpAddressResource(
            cloud_resource_id=self.gen_id(),
            cloud_account_id=self.cloud_acc_id,
            name='ip_address_name_1',
            region='us-1',
            instance_id='instance-1',
            available=True
        )
        ip2 = IpAddressResource(
            cloud_resource_id=self.gen_id(),
            cloud_account_id=self.cloud_acc_id,
            name='ip_address_name_2',
            region='us-2',
            instance_id='instance-2',
            available=True
        )
        ip3 = IpAddressResource(
            cloud_resource_id=self.gen_id(),
            cloud_account_id=self.cloud_acc_id2,
            name='ip_address_name_3',
            region='us-1',
            instance_id='instance-1',
            available=False
        )
        return [ip1, ip2, ip3]

    def test_get_instances(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertEqual(code, 200)
        meta = response['data'][0]['meta']
        for f in ['flavor', 'image_id', 'security_groups', 'os', 'cpu_count',
                  'spotted', 'last_seen_not_stopped', 'stopped_allocated',
                  'cloud_console_link']:
            self.assertTrue(f in meta.keys())

    def test_get_pods(self):
        params = {
            "enabled": True,
            "resource_type": "k8s_pod"
        }
        code, _ = self.client.discovery_info_create_bulk(
            self.cloud_acc_id, {'discovery_info': [params]})
        self.assertEqual(code, 200)
        self.resource_discovery_call(self.get_kubernetes_pods())

        code, response = self.client.cloud_resources_discover(
            self.org_id, 'k8s_pod')
        self.assertEqual(code, 200)
        meta = response['data'][0]['meta']
        for f in ['pod_ip', 'instance_address', 'host_ip']:
            self.assertTrue(f in meta.keys())
        for pod in response['data']:
            self.assertNotIn('cloud_console_link', pod)

    def test_get_ip_addresses(self):
        self.resource_discovery_call(self.get_ip_addresses())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'ip_address')
        self.assertEqual(code, 200)
        meta = response['data'][0]['meta']
        for f in ['cloud_console_link', 'available', 'last_used', 'instance_id']:
            self.assertTrue(f in meta.keys())

    def test_get_invalid_type(self):
        type_ = 'foobar'
        code, response = self.client.cloud_resources_discover(
            self.org_id, type_)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Invalid resource type: foobar")

    def test_get_no_type(self):
        type_ = None
        code, response = self.client.cloud_resources_discover(
            self.org_id, type_)
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], "Resource type is required")

    def test_invalid_filter_format(self):
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'volume', 'foo')
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], "Filters should be a dict")

    def test_invalid_filter_name(self):
        filter_name = 'bar'
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'volume', {filter_name: 1})
        self.assertEqual(code, 400)
        self.assertEqual(
            response['error']['reason'], "Invalid filter name %s" %
                                         filter_name)

    def test_invalid_filter_condition(self):
        filter_name = 'cloud_account_id'
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'volume', {filter_name: 1})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Value for filter %s should be a list" % filter_name)

    def test_sort_format(self):
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'volume', {}, 'foo')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Sort condition must be a dict")

    def test_sort_condition_one(self):
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'volume', {}, {'name': 'asc', 'flavor': 'desc'})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Sort condition should be one")

    def test_sort_condition_invalid_for_type(self):
        type_ = 'Volume'
        key_ = 'flavor'
        code, response = self.client.cloud_resources_discover(
            self.org_id, type_, {}, {key_: 'desc'})
        self.assertEqual(code, 400)
        self.assertTrue('Invalid sort condition %s for type %s' % (
            key_, type_) in response['error']['reason'])

    def test_sort_invalid_order(self):
        type_ = 'volume'
        key_ = 'size'
        order = 'foobar'
        code, response = self.client.cloud_resources_discover(
            self.org_id, type_, {}, {key_: order})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Sort order should be asc or desc")

    def test_no_filter(self):
        resources = self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), len(resources))

    def test_filter_simple(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'cloud_account_id': [self.cloud_acc_id]})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 2)

    def test_filter_region(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {'region': ['us-1']})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 1)

    def test_filter_complex(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'cloud_account_id': [self.cloud_acc_id]
            })
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 2)
        res_id = response['data'][0]['resource_id']
        self.mock_assign_resources({res_id: (
            self.employee_id, self.pool_id)})
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'cloud_account_id': [self.cloud_acc_id],
                'owner_id': [self.employee_id]
            })
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 1)
        obj = response['data'][0]
        self.assertEqual(obj['resource_id'], res_id)

    def test_sorting(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'cloud_account_id': [self.cloud_acc_id]
            }, sort={'name': 'asc'})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 2)
        self.assertEqual(response['data'][0]['name'], 'Instance1')
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'cloud_account_id': [self.cloud_acc_id]
            }, sort={'name': 'desc'})
        self.assertEqual(response['data'][0]['name'], 'instance2')

    def test_cache_time(self):
        """
        Steps:
           - 1. Discover from cache (should be 0 resources)
           - 2. Create resources like 'discover worker' do
           - 3. Discover from cache (should be 5 resources)
           - 4. Do cloud resources discover but without resources
           - 5. Discover from cache again (should be 0 resources)
        """
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 0)
        self.assertEqual(response['from_cache'], True)
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
          self.org_id, 'instance')
        self.assertEqual(code, 200)
        self.assertEqual(response['from_cache'], True)
        self.assertEqual(len(response['data']), 5)
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 5)
        self.assertEqual(response['from_cache'], True)
        now = datetime.utcnow()
        with freeze_time(now + timedelta(60)):
            self.resource_discovery_call(
                self.get_instances(), create_resources=False)
            code, response = self.client.cloud_resources_discover(
                self.org_id, 'instance')
            self.assertEqual(code, 200)
            self.assertEqual(response['from_cache'], True)
            self.assertEqual(len(response['data']), 0)

    def test_saving_resources(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'resource_id': 'asc'})
        resource_ids1 = list(map(lambda x: x['resource_id'], response['data']))
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'resource_id': 'asc'})
        resource_ids2 = list(map(lambda x: x['resource_id'], response['data']))
        self.assertEqual(resource_ids1, resource_ids2)

    def test_owner_info(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertTrue(len(response['data']) > 0)
        res_id = response['data'][0]['resource_id']
        self.mock_assign_resources({res_id: (
            self.employee_id, self.pool_id)})
        _, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'owner_id': [self.employee_id]})
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['owner_name'],
                         self.valid_employee['name'])
        # check response from cache
        code, response_from_cache = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'owner_id': [self.employee_id]})
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['owner_name'],
                         self.valid_employee['name'])
        self.assertEqual(response['data'][0]['owner_name'],
                         response_from_cache['data'][0]['owner_name'])

    def test_pool_info(self):
        self.resource_discovery_call(self.get_instances())
        _, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertTrue(len(response['data']) > 0)
        res_id = response['data'][0]['resource_id']
        self.mock_assign_resources({res_id: (
            self.employee_id, self.pool_id)})

        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'pool_id': [self.pool_id]
            })
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['pool_name'],
                         self.pool_name)
        self.assertEqual(response['data'][0]['pool_purpose'],
                         PoolPurposes.BUDGET.value)
        # check response from cache from cache
        code, response_from_cache = self.client.cloud_resources_discover(
            self.org_id, 'instance', {
                'pool_id': [self.pool_id]
            })
        self.assertEqual(len(response_from_cache['data']), 1)
        self.assertTrue(response_from_cache['from_cache'])
        self.assertEqual(response['data'][0]['pool_name'],
                         response_from_cache['data'][0]['pool_name'])

    def test_cloud_account_names(self):
        self.resource_discovery_call(self.get_instances())
        _, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertTrue(len(response['data']) > 0)
        for obj in response['data']:
            self.assertIsNotNone(obj.get('cloud_account_name'))

    def test_sorting_case_sensitivity(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'name': 'asc'})
        example = list(map(lambda x: x['name'], response['data']))
        example.sort(key=lambda x: x.lower())
        self.assertEqual(list(map(lambda x: x['name'], response['data'])),
                         example)

    def test_nonexistent_org(self):
        fake_org_id = str(uuid.uuid4())
        code, resp = self.client.cloud_resources_discover(
            fake_org_id, 'instance')
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_with_cloud_type_from_cache(self):
        self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance',
            cloud_type='azure_cnr')
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 1)
        self.assertEqual(response['data'][0]['cloud_account_id'],
                         self.azure_cloud_acc_id)

    def test_with_invalid_cloud_type(self):
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', cloud_type='demo')
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0436')

    def test_without_cached(self):
        url = self.client.cloud_resource_discovery_url(self.org_id)
        code, _ = self.client.get(url + self.client.query_url(
            **{'type': 'instance'}))
        self.assertEqual(code, 200)

    def test_first_seen_discover(self):
        now = datetime.utcnow()
        with freeze_time(now):
            self.resource_discovery_call(self.get_instances())
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'resource_id': 'asc'})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 5)
        for discovered_resource in response['data']:
            _, resp = self.client.cloud_resource_get(
                discovered_resource['resource_id'])
            self.assertEqual(resp['first_seen'], int(now.timestamp()))

        past_date = now - timedelta(days=10)
        self.resource_discovery_call(self.get_instances(),
                                     first_seen=int(past_date.timestamp()))
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'resource_id': 'asc'})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 5)
        for discovered_resource in response['data']:
            _, resp = self.client.cloud_resource_get(
                discovered_resource['resource_id'])
            self.assertEqual(resp['first_seen'], int(past_date.timestamp()))

        future_date = now + timedelta(days=10)
        self.resource_discovery_call(self.get_instances(),
                                     first_seen=int(future_date.timestamp()))
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance', sort={'resource_id': 'asc'})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['data']), 5)
        for discovered_resource in response['data']:
            _, resp = self.client.cloud_resource_get(
                discovered_resource['resource_id'])
            # should be 'past', not 'future'
            self.assertEqual(resp['first_seen'], int(past_date.timestamp()))

    def test_import_after_discover(self):
        now = datetime.utcnow()
        with freeze_time(now):
            self.resource_discovery_call([self.get_instances()[0]])
        code, response = self.client.cloud_resources_discover(
            self.org_id, 'instance')
        self.assertEqual(code, 200)
        discovered_resource = response['data'][0]
        _, resp = self.client.cloud_resource_get(
            discovered_resource['resource_id'])
        self.assertEqual(resp['first_seen'], int(now.timestamp()))
        old_first_seen = 1600000000

        payload = [{
            'meta': {'flavor': discovered_resource['meta']['flavor']},
            'last_seen': int(now.timestamp()),
            'cloud_resource_id': discovered_resource['cloud_resource_id'],
            'name': discovered_resource['name'],
            'resource_type': 'Instance',
            'region': discovered_resource['region'],
            'first_seen': old_first_seen
        }]
        code, response = self.cloud_resource_create_bulk(
            self.cloud_acc_id, {'resources': payload},
            behavior='skip_existing', return_resources=True)
        self.assertEqual(code, 200)
        self.assertEqual(
            response['resources'][0]['first_seen'], old_first_seen)

    def test_invalid_cluster_type_id(self):
        type_ = str(uuid.uuid4())
        code, response = self.client.cloud_resources_discover(
            self.org_id, type_)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['reason'],
                         "Invalid cluster type id %s in resource type" % type_)

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

    def test_get_cluster_resources(self):
        ct_name, ct_tag = 'ct_name', 'type'
        tag_values = ['val', 'val2']
        cr_ids = []
        for tv in tag_values:
            cr_ids.append('%s/%s' % (ct_name, tv))
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': ct_name, 'tag_key': ct_tag})
        self.assertEqual(code, 201)
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc_id, tags={ct_tag: tag_values[0]})
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc_id, tags={ct_tag: tag_values[1]})
        self.assertEqual(code, 201)
        ctc = ClusterTypeController(self.session)
        for cr_id in cr_ids:
            ctc.get_or_create({
                'cluster_type_id': ct['id'],
                'cloud_resource_id': cr_id,
                'active': True,
                'deleted_at': 0
            })
        code, cluster_list = self.client.cloud_resources_discover(
            self.org_id, ct['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(cluster_list['data']), 2)
        for cluster in cluster_list['data']:
            self.assertIn(cluster['cloud_resource_id'], cr_ids)
            self.assertEqual(cluster['cluster_type_id'], ct['id'])
