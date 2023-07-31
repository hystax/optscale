import base64
import uuid
import unittest
from config_client.client import Client as ConfigClient
from datetime import datetime, timedelta
from unittest.mock import MagicMock, PropertyMock, patch, mock_open, call

from bumblebi.exporter.main import Worker

RESTAPI_URL = "restapi"
CLUSTER_SECRET = "secret"


class TestWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.config_cl = ConfigClient()
        self.config_cl.restapi_url = MagicMock(return_value=RESTAPI_URL)
        self.config_cl.cluster_secret = MagicMock(return_value=CLUSTER_SECRET)
        self.worker = Worker(None, self.config_cl)
        self.pool = {
            'id': str(uuid.uuid4()),
            'name': 'employee',
            'purpose': 'budget',
            'children': [],
            'parent_id': None
        }
        self.organization = {
            'id': str(uuid.uuid4()),
            'name': 'org',
            'pool_id': self.pool['id']
        }
        self.bi_id = str(uuid.uuid4())
        self.bi = {
            'id': self.bi_id,
            'status': 'QUEUED',
            'meta': {'credentials': 'credentials'},
            'type': 'AWS_RAW_EXPORT',
            'days': 5,
            'organization_id': self.organization['id']
        }
        self.cloud_acc = {
            'id': str(uuid.uuid4()),
            'type': 'aws_cnr',
            'name': 'aws'
        }
        self.employee = {
            'id': str(uuid.uuid4()),
            'name': 'employee'
        }
        self.tag = 'tag'
        self.mongo_resource = {
            '_id': str(uuid.uuid4()),
            'name': 'name',
            'cloud_resource_id': 'cloud_resource_id',
            'cloud_console_link': 'https://cloud_console_link',
            'tags': {base64.b64encode(
                self.tag.encode('utf-8')).decode(): self.tag},
            'region': 'region',
            'first_seen': 0,
            'last_seen': int(datetime.utcnow().timestamp()),
            'active': True,
            'resource_type': 'Instance',
            'service_name': 'service_name',
            'recommendations': {
                'run_timestamp': 1,
                'modules': [{'saving': 22.42, 'name': 'instance_migration'}]
            },
            'employee_id': self.employee['id'],
            'pool_id': self.pool['id'],
            'cloud_account_id': self.cloud_acc['id']
        }
        self.worker.rest_cl.bi_get = MagicMock(return_value=(200, self.bi))
        self.worker.rest_cl.bi_get = MagicMock(return_value=(200, self.bi))
        self.worker.rest_cl.bi_update = MagicMock(return_value=(200, self.bi))
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl',
              new_callable=PropertyMock).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.bi_get',
              return_value=(200, self.bi)).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.organization_get',
              return_value=(200, self.organization)).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.cloud_account_list',
              return_value=(200, {'cloud_accounts': [self.cloud_acc]})).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.employee_list',
              return_value=(200, {'employees': [self.employee]})).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.pool_get',
              return_value=(200, self.pool)).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.cluster_type_list',
              return_value=(200, {'cluster_types': []})).start()
        patch('bumblebi.exporter.exporter.BaseExporter.rest_cl.optimizations_get',
              return_value=(200, {'last_completed': 1})).start()
        patch('bumblebi.exporter.exporter.BaseExporter._get_resources',
              return_value=[self.mongo_resource]).start()
        patch('bumblebi.exporter.exporter.AwsExporter._upload').start()
        yesterday = datetime.utcnow() - timedelta(days=1)
        self.clichouse_expenses = [
            (yesterday, self.cloud_acc['id'], self.mongo_resource['_id'], 348.75)]
        patch('bumblebi.exporter.exporter.BaseExporter._get_expenses_clickhouse',
              return_value=self.clichouse_expenses).start()
        patch('bumblebi.exporter.exporter.BaseExporter._cleanup').start()

    def test_worker_process_task(self):
        message = MagicMock()
        self.worker._running = MagicMock()
        self.worker._success = MagicMock()
        with patch('builtins.open', mock_open()) as mock_files:
            self.worker.process_task(body={'organization_bi_id': self.bi_id},
                                     message=message)
        self.worker._running.assert_called_once()
        self.worker._success.assert_called_once()
        self.assertEqual(mock_files.call_count, 3)

        def _quote(val):
            if type(val) != str:
                return str(val)
            else:
                return '"' + val + '"'

        resources_params_list = [
            self.organization['name'],
            self.organization['id'],
            self.cloud_acc['id'],
            self.cloud_acc['type'],
            self.cloud_acc['name'],
            self.mongo_resource['_id'],
            self.mongo_resource['cloud_resource_id'],
            self.mongo_resource['cloud_console_link'],
            self.employee['id'],
            self.employee['name'],
            str({self.tag: self.tag}),
            str(datetime.fromtimestamp(self.mongo_resource['first_seen'])),
            str(datetime.fromtimestamp(self.mongo_resource['last_seen'])),
            self.mongo_resource['name'],
            self.pool['id'],
            self.pool['name'],
            self.pool['purpose'],
            '',  # parent_id
            self.mongo_resource['region'],
            self.mongo_resource['resource_type'],
            self.mongo_resource['active'],
            '',  # cluster_type_id
            '',  # cluster_name
            self.mongo_resource['service_name']
        ]
        expenses_params_list = [
            str(self.clichouse_expenses[0][0]),
            self.mongo_resource['_id'],
            self.clichouse_expenses[0][3]
        ]
        recommendation_params_list = [
            self.mongo_resource['_id'],
            self.mongo_resource['recommendations']['modules'][0]['name'],
            round(
                self.mongo_resource['recommendations']['modules'][0]['saving'],
                4)
        ]

        expected_calls = [
            # resources.csv
            call().write(','.join(
                [_quote(x) for x in resources_params_list]) + '\r\n'),
            # expenses
            call().write(','.join(
                [_quote(x) for x in expenses_params_list]) + '\r\n'),
            # recommendation
            call().write(','.join(
                [_quote(x) for x in recommendation_params_list]) + '\r\n'),
        ]
        for call_ in expected_calls:
            self.assertIn(call_, mock_files.mock_calls)

    def test_worker_invalid_task(self):
        message = MagicMock()
        message.reject = MagicMock()
        self.worker.process_task(body={}, message=message)
        message.reject.assert_called_once()

    def test_failed(self):
        def side_eff():
            raise Exception()

        message = MagicMock()
        message.reject = MagicMock()
        self.worker._fail = MagicMock()
        patch('bumblebi.exporter.exporter.AwsExporter._upload',
              side_effect=side_eff).start()
        self.worker.process_task(body={'organization_bi_id': self.bi_id},
                                 message=message)
        self.worker._fail.assert_called_once()
