import uuid

from unittest.mock import patch

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestNodeApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.org_id = self.org['id']

        auth_user = self.gen_id()
        self.client.employee_create(
            self.org['id'], {'name': 'employee_1',
                             'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id',
              return_value=auth_user).start()

        self.valid_cloud_config = {
            'access_key_id': 'key',
            'secret_access_key': 'secret',
            'config_scheme': 'create_report'
        }
        self.valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': self.valid_cloud_config
        }
        self.p_configure = patch(
            'tools.cloud_adapter.clouds.aws.Aws.configure_report').start()

        cpu_price = 0.002
        memory_price = 0.001
        self.default_node_price = cpu_price + memory_price
        self.valid_kubernetes_cloud_acc = {
            'name': 'k8s cloud_acc',
            'type': 'kubernetes_cnr',
            'config': {
                'user': 'user',
                'password': 'password',
                'cost_model': {
                    'cpu_hourly_cost': cpu_price,
                    'memory_hourly_cost': memory_price
                }
            }
        }
        self.p_publish_recalculation = patch(
            'rest_api.rest_api_server.controllers.cloud_account.'
            'ExpensesRecalculationScheduleController.schedule').start()

    def create_cloud_acc(self, payload):
        code, cloud_acc = self.create_cloud_account(
            self.org_id, payload)
        self.assertEqual(code, 201)
        return cloud_acc

    def test_create_non_k8s(self):
        cloud_acc = self.create_cloud_acc(self.valid_aws_cloud_acc)
        payload = {
            'nodes': []
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_create_nonexisting_cloud(self):
        payload = {
            'nodes': []
        }
        code, res = self.client.node_create_bulk(str(uuid.uuid4()), payload)
        self.assertEqual(code, 404)

    def test_create_nodes_extra(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        payload = {
            'nodes': [],
            'pods': 'random'
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

        payload = {
            'nodes': [
                {
                    'name': 'last_seen', 'provider': 'flavor',
                    'last_seen': 1175, 'cpu': 1, 'memory': 2
                }
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create_nodes_extra2(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        node = {
            'name': 'last_seen', 'last_seen': 1175,
            'cpu': 1, 'memory': 2
        }
        code, res = self.client.node_create_bulk(
            cloud_acc['id'], {'nodes': [node]})
        self.assertEqual(code, 200)

        node['provider'] = 'whatever'
        code, res = self.client.node_create_bulk(
            cloud_acc['id'], {'nodes': [node]})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create_no_nodes(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        payload = {}
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_nodes_wrong_format(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        payload = {
            'nodes': {}
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0385')

    def test_create_nodes_empty(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        payload = {
            'nodes': []
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)

    def test_create_nodes_cloud_based(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': 'name',
                    'provider_id': 'flavor', 'last_seen': 1175,
                    'cpu': 1, 'memory': 2, 'hourly_price': self.default_node_price}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 1)
        node = res.get('nodes')[0]
        for f, v in src_node.items():
            self.assertEqual(node.get(f), v)
        for f in ['id', 'provider', 'created_at', 'deleted_at', 'hourly_price']:
            self.assertIsNotNone(node.get(f))
        self.assertEqual(node['hourly_price'], self.default_node_price)

    def test_create_nodes_int_price(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': 'name',
                    'provider_id': 'flavor', 'last_seen': 1175,
                    'cpu': 1, 'memory': 2, 'hourly_price': 21}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 1)

    def test_create_nodes_on_prem_with_cloud_fields(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': 'm1', 'cpu': 1, 'memory': 2,
                    'last_seen': 1175, 'hourly_price': 0.2}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0475')

        src_node['provider_id'] = src_node.pop('flavor')
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0475')

    def test_create_nodes_on_prem(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': None, 'cpu': 1, 'memory': 2,
                    'provider_id': None, 'last_seen': 1175, 'hourly_price': 0.2}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 1)
        node = res.get('nodes')[0]
        for f, v in src_node.items():
            self.assertEqual(node.get(f), v)
        for f in ['id', 'provider', 'created_at', 'deleted_at']:
            self.assertTrue(f in node.keys())

    def test_create_nodes_on_prem2(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'last_seen': 1175,
                    'cpu': 1, 'memory': 2}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 1)
        node = res.get('nodes')[0]
        for f, v in src_node.items():
            self.assertEqual(node.get(f), v)
        for f in ['id', 'provider', 'created_at', 'deleted_at']:
            self.assertTrue(f in node.keys())

    def test_create_nodes_required(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        for src_node in [{'last_seen': 1175}, {'name': 'node'},
                         {'cpu': 1}, {'memory': 2}]:
            payload = {
                'nodes': [
                    src_node
                ]
            }
            code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_nodes_recreate(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'last_seen': 1175,
                    'cpu': 1, 'memory': 2}
        code, res = self.client.node_create_bulk(
            cloud_acc['id'], {'nodes': [src_node]})
        self.assertEqual(code, 200)
        node1 = res['nodes'][0]
        node1.pop('last_seen')
        node_hourly_price = node1.pop('hourly_price')

        src_node['last_seen'] *= 2
        src_node['hourly_price'] = 2 * node_hourly_price
        code, res = self.client.node_create_bulk(
            cloud_acc['id'], {'nodes': [src_node]})
        self.assertEqual(code, 200)
        node2 = res['nodes'][0]
        self.assertEqual(node2.pop('last_seen'), src_node['last_seen'])
        self.assertEqual(node2.pop('hourly_price'), src_node['hourly_price'])

        self.assertDictEqual(node1, node2)

    def test_create_nodes_several(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        payload = {
            'nodes': [
                {'name': 'last_seen', 'flavor': 'name',
                 'provider_id': 'flavor', 'last_seen': 1175,
                 'cpu': 1, 'memory': 2, 'hourly_price': 15},
                {'name': 'name', 'flavor': 'flavor',
                 'provider_id': 'provider_id', 'last_seen': 2350,
                 'cpu': 1, 'memory': 2, 'hourly_price': 20},
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 2)

    def test_create_and_update_nodes_several(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        node1 = {'name': 'last_seen', 'flavor': 'name',
                 'provider_id': 'flavor', 'last_seen': 1175,
                 'cpu': 1, 'memory': 2, 'hourly_price': 15}
        node2 = {'name': 'name', 'flavor': 'flavor',
                 'provider_id': 'provider_id', 'last_seen': 2350,
                 'cpu': 1, 'memory': 2, 'hourly_price': 20}

        payload = {
            'nodes': [
                node1
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 1)

        node1['last_seen'] = 2350
        payload = {
            'nodes': [
                node1,
                node2
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 2)
        for dst_node in res.get('nodes'):
            for src_node in payload['nodes']:
                if src_node['name'] == dst_node['name']:
                    self.assertEqual(
                        src_node['last_seen'], dst_node['last_seen'])

    def test_list_nodes_nonexisting_cloud(self):
        code, res = self.client.node_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_list_nodes_empty(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        code, res = self.client.node_list(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))

    def test_list_nodes_non_k8s(self):
        cloud_acc = self.create_cloud_acc(self.valid_aws_cloud_acc)
        code, res = self.client.node_list(cloud_acc['id'])
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0436')

    def test_list_nodes_outdated(self):
        last_seen = 1175
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': 'name',
                    'provider_id': 'flavor', 'last_seen': last_seen,
                    'cpu': 1, 'memory': 2, 'hourly_price': 15}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)

        code, _ = self.client.cloud_account_update(
            cloud_acc['id'], {'last_import_at': last_seen * 2})
        self.assertEqual(code, 200)

        code, res = self.client.node_list(cloud_acc['id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(res.get('nodes'))
        self.assertEqual(len(res.get('nodes')), 0)

    def test_list_nodes(self):
        last_seen = 1175
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'flavor': 'name',
                    'provider_id': 'flavor', 'last_seen': last_seen,
                    'cpu': 1, 'memory': 2, 'hourly_price': 15}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 200)

        for val in [last_seen // 2, last_seen]:
            code, _ = self.client.cloud_account_update(
                cloud_acc['id'], {'last_import_at': val})
            self.assertEqual(code, 200)

            code, res = self.client.node_list(cloud_acc['id'])
            self.assertEqual(code, 200)
            self.assertIsNotNone(res.get('nodes'))
            self.assertEqual(len(res.get('nodes')), 1)

    def test_invalid_create_node_payload_with_not_all_params(self):
        cloud_acc = self.create_cloud_acc(self.valid_kubernetes_cloud_acc)
        src_node = {'name': 'last_seen', 'provider_id': 'flavor',
                    'last_seen': 1234, 'cpu': 1, 'memory': 2}
        payload = {
            'nodes': [
                src_node
            ]
        }
        code, res = self.client.node_create_bulk(cloud_acc['id'], payload)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0475')
