import os
from datetime import datetime, timezone
from unittest.mock import patch

from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.db_factory import DBFactory, DBType
from rest_api_server.models.models import Employee, Pool
from rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestAvailableFiltersApi(TestApiBase):
    # common negative cases. Positive tests can be found in expenses
    # tests cases

    def setUp(self, version='v2'):
        os.environ['ASYNC_TEST_TIMEOUT'] = '2000'
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        cloud_acc1 = {
            'name': 'aws1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }

        self.auth_user_id_1 = self.gen_id()
        self.auth_user_id_2 = self.gen_id()
        self.auth_user_id_3 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id_1)
        self.start_ts = int(datetime(2020, 4, 1, 0, 0).timestamp())
        self.end_ts = int(datetime(2020, 4, 2, 23, 59).timestamp())

    @staticmethod
    def get_all_org_employees(organization_id):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        employees = session.query(Employee).filter(
            Employee.organization_id == organization_id,
            Employee.deleted_at == 0).all()
        return list(employees)

    @staticmethod
    def get_all_org_pools(organization_id):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        pools = session.query(Pool).filter(
            Pool.organization_id == organization_id,
            Pool.deleted_at == 0).all()
        return list(pools)

    def test_available_filters_unexpected_filters(self):
        self.end_ts = int(datetime(2020, 4, 2, 23, 59).timestamp())
        filters = {
            'not_a_region': 'us-east',
        }
        code, response = self.client.available_filters_get(
            self.org_id, self.start_ts, self.end_ts, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_available_filters_dates_values(self):
        filters = {
            'cloud_account_id': [self.cloud_acc1['id']],
        }
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.available_filters_get(
            self.org_id, min_timestamp, max_timestamp, filters)
        self.assertEqual(code, 200)
        code, response = self.client.available_filters_get(
            self.org_id, min_timestamp - 1, max_timestamp, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')
        code, response = self.client.available_filters_get(
            self.org_id, min_timestamp, max_timestamp + 1, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

        code, response = self.client.available_filters_get(
            self.org_id, min_timestamp - 1, 0, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

    def test_available_filters_limit(self):
        time = int(datetime.utcnow().timestamp())
        code, response = self.client.available_filters_get(
            self.org_id, time, time + 1, {'limit': 1})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_invalid_organization(self):
        day_in_month = datetime(2020, 1, 14)

        time = int(day_in_month.timestamp())
        valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        code, cloud_acc1 = self.create_cloud_account(
            self.org_id, valid_aws_cloud_acc)
        self.assertEqual(code, 201)
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        filters = {
            'cloud_account_id': [cloud_acc1['id']]
        }
        code, response = self.client.available_filters_get(
            organization2['id'], time, time + 1, filters)
        self.assertEqual(code, 404)
        self.verify_error_code(response, 'OE0470')

    def test_available_filters_default(self):
        employees = self.get_all_org_employees(self.org_id)
        cloud_accounts = self.get_all_org_cloud_accounts(self.org_id)
        pools = self.get_all_org_pools(self.org_id)
        code, response = self.client.available_filters_get(
            self.org_id, 0, 1)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['filter_values']['pool']), len(pools))
        self.assertEqual(len(response['filter_values']['cloud_account']),
                         len(cloud_accounts))
        self.assertEqual(len(response['filter_values']['owner']),
                         len(employees))

    def test_available_filters_default_values_if_filtered_by_entity(self):
        filters = {
            'pool_id': [self.org['pool_id']],
        }
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.available_filters_get(
            self.org_id, min_timestamp, max_timestamp, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['filter_values']['pool'], [])
