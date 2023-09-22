import json
import time
import uuid
from copy import deepcopy
from datetime import datetime
from unittest.mock import patch

import optscale_client.rest_api_client

from tools.optscale_exceptions.common_exc import InternalServerError
import optscale_client.rest_api_client.client
import optscale_client.rest_api_client.client_v2
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    ConstraintLimitHit, Pool, Employee, CloudAccount, Checklist,
    ResourceConstraint, PoolPolicy, OrganizationConstraint,
    OrganizationLimitHit)
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


PRESET_CLOUD_RESOURCE_ID = "sunflower-eu-fra"
PRESET_RESOURCE_NAME = "sunflower-eu-fra"
DUPLICATION_COUNT = 3
BASIC_PRESET = {
    "cloud_accounts": [
        {
            "id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "name": "AWS HQ",
            "last_import_at_offset": 18852,
            "created_at_offset": 11787368,
            "type": "aws_cnr",
            "import_period": 1
        }
    ],
    "checklists": [
        {
            "last_run_offset": 25861,
            "last_completed_offset": 25861,
            "next_run_offset": 15334,
            "created_at_offset": 3658802
        }
    ],
    "resources": [
        {
            "pool_id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "resource_type": "Bucket",
            "cloud_account_name": "AWS HQ",
            "created_at_offset": 11786789,
            "active": True,
            "pool_purpose": "business_unit",
            "last_seen_offset": 62416,
            "pool_name": "Engineering",
            "cloud_resource_id": PRESET_CLOUD_RESOURCE_ID,
            "employee_id": "083298ff-6575-4adb-a82a-92cea7bc8ff0",
            "meta": {},
            "name": PRESET_RESOURCE_NAME,
            "tags": {},
            "deleted_at_offset": 0,
            "_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "region": "eu-central-1",
            "recommendations": {
                "modules": [
                    {
                        "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
                        "resource_name": PRESET_RESOURCE_NAME,
                        "cloud_resource_id": PRESET_CLOUD_RESOURCE_ID,
                        "region": "eu-central-1",
                        "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                        "cloud_account_name": "AWS HQ",
                        "cloud_account_type": "aws_cnr",
                        "saving": 20,
                        "name": "abandoned_instances"
                    },
                    {
                        "monthly_saving": 10.05,
                        "annually_monthly_saving": 14.37,
                        "saving": 14.366,
                        "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
                        "resource_name": PRESET_RESOURCE_NAME,
                        "cloud_resource_id": PRESET_CLOUD_RESOURCE_ID,
                        "region": "eu-central-1",
                        "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                        "cloud_account_name": "AWS HQ",
                        "cloud_account_type": "aws_cnr",
                        "name": "instance_subscription"
                    }
                ]
            }
        },
        {
            "pool_id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "resource_type": "Savings Plan",
            "cloud_account_name": "AWS HQ",
            "created_at_offset": 11786789,
            "active": False,
            "pool_purpose": "business_unit",
            "last_seen_offset": 62416,
            "pool_name": "Engineering",
            "cloud_resource_id": "savings_plan_arn",
            "employee_id": "083298ff-6575-4adb-a82a-92cea7bc8ff0",
            "meta": {},
            "name": None,
            "tags": {},
            "deleted_at_offset": 0,
            "_id": "3addfeea-e4f7-48f1-846a-68827ae9a92b",
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "region": "eu-central-1",
            "recommendations": {}
        }
    ],
    "resource_constraints": [
        {
            "type": "ttl",
            "limit": 1,
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "created_at_offset": 4001234
        }
    ],
    "pool_policies": [
        {
            "pool_id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "limit": 10,
            "type": "ttl",
            "created_at_offset": 5461804,
            "active": True
        }
    ],
    "raw_expenses": [
        {
            "start_date_offset": 5148934,
            "_id": "5f5b550de447c06bc4f73910",
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "end_date_offset": 5062534,
            "cost": 0.88250706,
            "resource_id": PRESET_CLOUD_RESOURCE_ID,
            "pricing/publicOnDemandCost": 0.12345,
        }
    ],
    "rules": [],
    "pools": [
        {
            "id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "parent_id": "31622be0-00f9-4138-b033-eee45aefb558",
            "name": "Engineering",
            "created_at_offset": 11786676,
            "purpose": "business_unit",
            "limit": 50000,
            "default_owner_id": "015c36f9-5c05-4da8-b445-932560a00191"
        }
    ],
    "employees": [
        {
            "id": "083298ff-6575-4adb-a82a-92cea7bc8ff0",
            "auth_user_id": "3ef4d308-9d45-4f3e-aacf-12bbd5a33a21",
            "name": "Emily Garcia",
            "created_at_offset": 5487346
        }
    ],
    "assignments": [
        {
            "pool_id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "created_at_offset": 0,
            "owner_id": "083298ff-6575-4adb-a82a-92cea7bc8ff0"
        }
    ],
    "limit_hits": [
        {
            "pool_id": "6731a6ef-7b52-44ed-bc69-a137c36f8840",
            "type": "ttl",
            "created_at_offset": 1572791,
            "constraint_limit": 5,
            "time_offset": 1572791,
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "ttl_value": 15,
            "expense_value": None
        }
    ],
    "conditions": [],
    "auth_users": [
        {
            "role_purpose": "optscale_manager",
            "role_scope_id": None,
            "role_name": "Manager",
            "assignment_resource_id": "2a03382a-a036-4881-b6b5-68c08192cc44",
            "user_display_name": "Emily Garcia",
            "role_id": 3,
            "assignment_id": "28905769-bc3f-43d6-a101-7067c54a33e6",
            "user_email": "egarcia@sunflower.example",
            "assignment_type_id": 2,
            "user_id": "3ef4d308-9d45-4f3e-aacf-12bbd5a33a21"
        },
        {
            "role_purpose": "optscale_member",
            "role_scope_id": None,
            "role_name": "Member",
            "assignment_resource_id": "2a03382a-a036-4881-b6b5-68c08192cc44",
            "user_display_name": "Emily Garcia",
            "role_id": 5,
            "assignment_id": "7d691997-a7ba-41e0-87a8-56ce9fc0096b",
            "user_email": "egarcia@sunflower.example",
            "assignment_type_id": 2,
            "user_id": "3ef4d308-9d45-4f3e-aacf-12bbd5a33a21"
        }
    ],
    "optimizations": [
        {
            "module": "abandoned_instances",
            "data": [
                {
                    "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
                    "resource_name": PRESET_RESOURCE_NAME,
                    "cloud_resource_id": PRESET_CLOUD_RESOURCE_ID,
                    "region": "Germany (Frankfurt)",
                    "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                    "cloud_account_name": "AWS HQ",
                    "cloud_account_type": "aws_cnr",
                    "saving": 12.5434
                }
            ],
            "created_at_offset": 25861
        },
        {
            "module": "instance_subscription",
            "created_at_offset": 25861,
            "data": [
                {
                    "monthly_saving": 10.05,
                    "annually_monthly_saving": 14.37,
                    "saving": 14.366,
                    "flavor": "ecs.n4.large",
                    "region": "Germany (Frankfurt)",
                    "cloud_resource_id": PRESET_CLOUD_RESOURCE_ID,
                    "resource_name": PRESET_RESOURCE_NAME,
                    "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
                    "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
                    "cloud_account_name": "AWS HQ",
                    "cloud_type": "aws_cnr",
                }
            ],
        }
    ],
    "clean_expenses": [
        {
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "cost": 1159.5993548571,
            "sign": 1,
            "date_offset": 5148934
        }
    ],
    "organization_constraint": [
        {
            "deleted_at": 0,
            "id": "56fd877e-b870-4006-ada2-993863db05bf",
            "created_at": 1646217169,
            "name": "Marketing resource count",
            "type": "resource_count_anomaly",
            "definition": {
                "threshold_days": 30,
                "threshold": 10
            },
            "filters": {
                "pool_id": ["6731a6ef-7b52-44ed-bc69-a137c36f8840+"],
                "owner_id": ["083298ff-6575-4adb-a82a-92cea7bc8ff0"],
                "cloud_account_id": ["8c63e980-6572-4b36-be82-a2bc59705888"],
                "region": [None]
            },
            "last_run": 1646221248
        },
        {
            "deleted_at": 0,
            "id": "7179e6af-7231-4e1c-8afd-2a8b569192f7",
            "created_at": 1646217169,
            "name": "Marketing expense anomaly",
            "type": "expense_anomaly",
            "definition": {
                "threshold_days": 30,
                "threshold": 10
            },
            "filters": {
                "pool_id": ["6731a6ef-7b52-44ed-bc69-a137c36f8840+"],
                "owner_id": ["083298ff-6575-4adb-a82a-92cea7bc8ff0"],
                "cloud_account_id": ["8c63e980-6572-4b36-be82-a2bc59705888"],
                "region": [None]
            },
            "last_run": 1646221248
        },
        {
            "id": "74b255f9-ab09-4df5-a866-e716d8aa4242",
            "name": "expiring budget",
            "type": "expiring_budget",
            "definition": {
                "total_budget": 1
            },
            "filters": {},
            "last_run": 1647869474,
            "created_at_offset": 323821,
            "definition.start_date_offset": 1694962
        },
    ],
    "organization_limit_hit": [
        {
            "constraint_id": "56fd877e-b870-4006-ada2-993863db05bf",
            "constraint_limit": 10.0,
            "value": 12.0,
            "created_at_offset": 229009
        },
        {
            "constraint_id": "7179e6af-7231-4e1c-8afd-2a8b569192f7",
            "constraint_limit": 40.0,
            "value": 52.0,
            "created_at_offset": 229009
        },
        {
            "constraint_id": "74b255f9-ab09-4df5-a866-e716d8aa4242",
            "constraint_limit": 1,
            "value": 1159.5993548571,
            "created_at_offset": 229009
        }
    ],
    "traffic_expenses": [
        {
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "type": "inbound",
            "from": "us-east-1",
            "to": "us-west-1",
            "usage": 11,
            "cost": 121,
            "date_offset": 229009
        }
    ],
    "ri_sp_usage": [
        {
            "cloud_account_id": "8c63e980-6572-4b36-be82-a2bc59705888",
            "resource_id": "14d75330-c111-482a-97d0-0fe4b3b7125c",
            "offer_id": "3addfeea-e4f7-48f1-846a-68827ae9a92b",
            "offer_type": "ri",
            "offer_cost": 99,
            "on_demand_cost": 111,
            "usage": 12,
            "sign": 1,
            "date_offset": 229009
        }
    ]
}


class TestLiveDemosApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        self.preset = BASIC_PRESET
        self.multiplier = 2
        user_data = self.preset['auth_users'][0]
        self.user = {'id': str(uuid.uuid4()),
                     'display_name': user_data['user_display_name'],
                     'email': user_data['user_email']}
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_get_auth_user_params', return_value=(
                  self.user['email'], self.user['display_name'], 'password')).start()
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'create_auth_user', return_value=self.user).start()
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_info', return_value=self.user).start()
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_get_demo_multiplier', return_value=self.multiplier).start()
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_insert_clickhouse').start()

    def check_db(self, check_empty=True):
        session = self.init_db_session()
        for model in [Pool, Employee, CloudAccount, Checklist,
                      ResourceConstraint, PoolPolicy, ConstraintLimitHit,
                      OrganizationConstraint, OrganizationLimitHit]:
            cnt = len(session.query(model).all())
            if check_empty:
                # we don't rollback org pool and appropriate employee
                if model not in [Pool, Employee]:
                    self.assertEqual(cnt, 0)
            else:
                self.assertNotEqual(cnt, 0)
        session.close()

    def check_mongo(self, check_empty=True):
        for collection in [
            self.raw_expenses, self.resources_collection,
            self.checklists_collection
        ]:
            cnt = len(list(collection.find()))
            if check_empty:
                self.assertEqual(cnt, 0)
            else:
                self.assertNotEqual(cnt, 0)

    def check_clean_expenses(self, ch_mock_obj):
        preset_expenses = BASIC_PRESET['clean_expenses'].copy()
        table, values = ch_mock_obj.call_args_list[0][0]
        self.assertEqual(table, 'expenses')
        self.assertEqual(len(values), len(preset_expenses))
        for i, exp in enumerate(values):
            self.assertEqual(
                exp['cost'], preset_expenses[i]['cost'] * self.multiplier)

    def check_traffic_expenses(self, ch_mock_obj):
        preset_expenses = BASIC_PRESET['traffic_expenses'].copy()
        table, values = ch_mock_obj.call_args_list[1][0]
        self.assertEqual(table, 'traffic_expenses')
        self.assertEqual(len(values), len(preset_expenses))
        for i, exp in enumerate(values):
            self.assertEqual(exp['from'], preset_expenses[i]['from'])
            self.assertEqual(exp['to'], preset_expenses[i]['to'])
            self.assertEqual(
                exp['cost'], preset_expenses[i]['cost'] * self.multiplier)

    def check_ri_sp_usage(self, ch_mock_obj):
        preset_expenses = BASIC_PRESET['ri_sp_usage'].copy()
        table, values = ch_mock_obj.call_args_list[2][0]
        self.assertEqual(table, 'ri_sp_usage')
        self.assertEqual(len(values), len(preset_expenses))
        for i, exp in enumerate(values):
            self.assertEqual(exp['offer_type'], preset_expenses[i]['offer_type'])
            self.assertEqual(exp['offer_cost'],
                             preset_expenses[i]['offer_cost'] * self.multiplier)
            self.assertEqual(exp['on_demand_cost'],
                             preset_expenses[i]['on_demand_cost'] * self.multiplier)
            self.assertEqual(exp['usage'], preset_expenses[i]['usage'])

    def check_clickhouse(self, ch_mock_obj):
        self.assertEqual(ch_mock_obj.call_count, 3)
        self.check_clean_expenses(ch_mock_obj)
        self.check_traffic_expenses(ch_mock_obj)
        self.check_ri_sp_usage(ch_mock_obj)

    def test_live_demo_create(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
                       '_insert_clickhouse') as clickhouse_mock:
                code, response = self.client.live_demo_create()
                self.assertEqual(code, 201)
                for val in ['organization_id', 'password', 'email']:
                    self.assertIsNotNone(response[val])
                code, response = self.client.organization_get(
                    response['organization_id'])
                self.assertEqual(code, 200)
                self.assertEqual(response['is_demo'], True)
                self.check_db(check_empty=False)
                self.check_mongo(check_empty=False)
                self.check_clickhouse(clickhouse_mock)

    def test_live_demo_org_constraint_create(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
        session = self.init_db_session()
        constraint = session.query(OrganizationConstraint).all()
        self.assertEqual(len(constraint), 3)
        filters = json.loads(constraint[0].filters)
        self.assertEqual(filters['region'], [None])
        self.assertEqual(len(filters['pool_id']), 1)
        self.assertTrue(filters['pool_id'][0].endswith('+'))
        for f in ['owner_id', 'cloud_account_id']:
            self.assertEqual(len(filters[f]), 1)
            self.assertIsNotNone(filters[f][0])

        start_date = int(datetime.utcnow().replace(
            hour=0, minute=0, second=0).timestamp()) - self.preset[
            'organization_constraint'][2]['definition.start_date_offset']
        total_budget = self.preset['organization_constraint'][2][
            'definition']['total_budget'] * self.multiplier
        definition = {'total_budget': total_budget, 'start_date': start_date}
        self.assertDictEqual(json.loads(constraint[2].definition), definition)

    def test_live_demo_create_double(self):
        for i in range(2):
            with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                       '.load_preset', return_value=deepcopy(self.preset)):
                code, response = self.client.live_demo_create()
                self.assertEqual(code, 201)

    def test_live_demo_create_no_expenses(self):
        preset = deepcopy(self.preset)
        for val in ['raw_expenses', 'clean_expenses']:
            preset[val] = []
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            for val in ['organization_id', 'password', 'email']:
                self.assertIsNotNone(response[val])

    def test_live_demo_create_no_optimizations(self):
        preset = deepcopy(self.preset)
        preset['optimizations'] = []
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            for val in ['organization_id', 'password', 'email']:
                self.assertIsNotNone(response[val])

    def test_live_demo_create_permissions(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            http_provider = optscale_client.rest_api_client.client.FetchMethodHttpProvider(
                self.fetch, rethrow=False)
            client = TestApiBase.get_client().Client(
                http_provider=http_provider)
            code, response = client.live_demo_create()
            self.assertEqual(code, 201)

            code, response = client.live_demo_get()
            self.assertEqual(code, 200)
            self.assertEqual(response['is_alive'], False)

    def test_live_demo_error_optimization(self):
        preset = deepcopy(self.preset)
        preset['optimizations'][0]['data'] = {'error': 'Some error'}
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            for val in ['organization_id', 'password', 'email']:
                self.assertIsNotNone(response[val])

    def test_live_demo_create_empty_org(self):
        preset = deepcopy(self.preset)
        for val in preset.copy().keys():
            if val not in ['auth_users', 'employees', 'pools']:
                preset[val] = []
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            for val in ['organization_id', 'password', 'email']:
                self.assertIsNotNone(response[val])

    def test_live_demo_create_preset_load_exc(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset',
                   side_effect=InternalServerError(Err.OE0450, [])):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 500)
            self.assertEqual(response['error']['error_code'], 'OE0450')

    @patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
           '.fill_organization', side_effect=Exception())
    def test_live_demo_create_fill_org_exc(self, p_fill_org):
        preset = deepcopy(self.preset)
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 500)
            self.assertEqual(response['error']['error_code'], 'OE0451')

    @patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
           '._bind_pools', side_effect=Exception())
    def test_live_demo_create_rollback(self, p_recover_objs):
        preset = deepcopy(self.preset)
        p_delete_clickhouse_info = patch(
            'rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
            'delete_clickhouse_info').start()
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=preset):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 500)
            self.assertEqual(response['error']['error_code'], 'OE0451')
            self.check_db()
            self.check_mongo()
            p_delete_clickhouse_info.assert_called_once()

    def test_live_demo_get(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            self.client.live_demo_create()
            self._mock_auth_user(self.user['id'])
            code, response = self.client.live_demo_get()
            self.assertEqual(code, 200)
            self.assertEqual(response['is_alive'], True)

    def test_live_demo_get_expired(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            self.client.live_demo_create()
            self.p_get_meta_by_token.return_value = {
                'user_id': self.user['id'], 'valid_until': time.time() / 2}
            code, response = self.client.live_demo_get()
            self.assertEqual(code, 200)
            self.assertEqual(response['is_alive'], False)

    def test_live_demo_get_no_token(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            self.client.live_demo_create()
            self.p_get_meta_by_token.side_effect = AttributeError()
            code, response = self.client.live_demo_get()
            self.assertEqual(code, 200)
            self.assertEqual(response['is_alive'], False)

    def test_live_demo_get_another_user(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            self.client.live_demo_create()
            self._mock_auth_user(str(uuid.uuid4()))
            code, response = self.client.live_demo_get()
            self.assertEqual(code, 200)
            self.assertEqual(response['is_alive'], False)

    def test_live_demo_multipliers_default(self):
        etcd_multipliers_default = 10
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_get_demo_multiplier',
              return_value=etcd_multipliers_default).start()
        preset_raw_cost = self.preset.get('raw_expenses')[0].get('cost')
        preset_raw_public_cost = self.preset.get('raw_expenses')[0].get(
            'pricing/publicOnDemandCost')
        preset_optimizations = self.preset.get('optimizations')
        abandoned_saving = preset_optimizations[0].get('data')[0].get('saving')
        instance_subscription_saving = preset_optimizations[1].get(
            'data')[0].get('saving')
        instance_subscription_monthly = preset_optimizations[1].get(
            'data')[0].get('monthly_saving')
        instance_subscription_annually = preset_optimizations[1].get(
            'data')[0].get('annually_monthly_saving')
        preset_resource_modules = self.preset.get('resources')[0].get(
            'recommendations').get('modules')
        resource_abandoned_saving = preset_resource_modules[0].get('saving')
        resource_subscription_saving = preset_resource_modules[1].get('saving')
        resource_subscription_monthly_saving = preset_resource_modules[1].get(
            'monthly_saving')
        resource_subscription_annually = preset_resource_modules[1].get(
            'annually_monthly_saving')
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            raw_expense = list(self.raw_expenses.find())[0]
            optimization = list(self.checklists_collection.find())
            resource = list(self.resources_collection.find())
            self.assertEqual(raw_expense['cost'], preset_raw_cost * 10)
            self.assertEqual(raw_expense['pricing/publicOnDemandCost'],
                             preset_raw_public_cost * 10)
            self.assertEqual(optimization[0]['data'][0]['saving'],
                             abandoned_saving * 10)
            self.assertEqual(optimization[1]['data'][0]['saving'],
                             instance_subscription_saving * 10)
            self.assertEqual(optimization[1]['data'][0]['monthly_saving'],
                             instance_subscription_monthly * 10)
            self.assertEqual(optimization[1]['data'][0][
                'annually_monthly_saving'],
                instance_subscription_annually * 10)
            self.assertEqual(resource[0]['recommendations']['modules'][0]
                             ['saving'], resource_abandoned_saving * 10)
            self.assertEqual(resource[0]['recommendations']['modules'][1]
                             ['saving'], resource_subscription_saving * 10)
            self.assertEqual(resource[0]['recommendations']['modules'][1]
                             ['monthly_saving'],
                             resource_subscription_monthly_saving * 10)
            self.assertEqual(resource[0]['recommendations']['modules'][1]
                             ['annually_monthly_saving'],
                             resource_subscription_annually * 10)

    def test_live_demo_not_active_multipliers(self):
        etcd_multiplier_default = 1
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_get_demo_multiplier',
              return_value=etcd_multiplier_default).start()
        preset_raw_cost = self.preset.get('raw_expenses')[0].get('cost')
        preset_optimization_saving = self.preset.get(
            'optimizations')[0].get('data')[0].get('saving')
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            raw_expense = list(self.raw_expenses.find())[0]
            optimization = list(self.checklists_collection.find())[0]
            self.assertEqual(raw_expense['cost'], preset_raw_cost)
            self.assertEqual(optimization['data'][0]['saving'],
                             preset_optimization_saving)

    def test_resources_from_top_10_not_duplicated(self):
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            raw_expenses = list(self.raw_expenses.find())
            optimizations = list(self.checklists_collection.find())
            resources = list(self.resources_collection.find())
            self.assertEqual(len(raw_expenses), 1)
            self.assertEqual(len(resources), 2)
            self.assertEqual(len(optimizations[0]['data']), 1)

    def test_resources_not_from_top_10_duplicated(self):
        with patch(
                'rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                '.load_preset', return_value=deepcopy(self.preset)):
            patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
                  'get_top_resources_by_total_cost', return_value=[]).start()
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            raw_expenses = list(self.raw_expenses.find())
            optimizations = list(self.checklists_collection.find())
            resources = list(self.resources_collection.find())
            self.assertEqual(len(raw_expenses), 4)
            self.assertEqual(len(resources), 5)
            self.assertEqual(len(optimizations[0]['data']), 4)
            for i in range(0, DUPLICATION_COUNT + 1):
                resource = resources[i]
                recommendations = resource['recommendations']
                module_count = 2
                res_ending = ''
                if i != 0:
                    res_ending = '-x%s' % i
                    module_count = 1
                cloud_res_id = PRESET_CLOUD_RESOURCE_ID + res_ending
                self.assertEqual(raw_expenses[i]['resource_id'], cloud_res_id)
                self.assertEqual(resource['cloud_resource_id'], cloud_res_id)
                self.assertEqual(len(recommendations['modules']), module_count)
                self.assertEqual(optimizations[0]['data'][i][
                    'cloud_resource_id'], cloud_res_id)

    def test_organization_limit_hit_multiplier(self):
        etcd_multiplier_value = 2
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              '_get_demo_multiplier',
              return_value=etcd_multiplier_value).start()
        org_res_count_preset = self.preset.get('organization_limit_hit')[0]
        preset_res_count_limit = org_res_count_preset.get('constraint_limit')
        preset_res_count_value = org_res_count_preset.get('value')
        org_exp_anomaly_preset = self.preset.get('organization_limit_hit')[1]
        preset_exp_anomaly_limit = org_exp_anomaly_preset.get(
            'constraint_limit')
        preset_exp_anomaly_value = org_exp_anomaly_preset.get('value')
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController'
                   '.load_preset', return_value=deepcopy(self.preset)):
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            session = self.init_db_session()
            org_limit_hits = session.query(OrganizationLimitHit).all()
            self.assertEqual(len(org_limit_hits), 3)
            self.assertEqual(org_limit_hits[0].constraint_limit,
                             preset_res_count_limit)
            self.assertEqual(org_limit_hits[0].value,
                             preset_res_count_value)
            self.assertEqual(org_limit_hits[1].constraint_limit,
                             preset_exp_anomaly_limit * etcd_multiplier_value)
            self.assertEqual(org_limit_hits[1].value,
                             preset_exp_anomaly_value * etcd_multiplier_value)

    def test_live_demo_invalid_params(self):
        code, response = self.client.live_demo_create({'unexpected': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0212')

        code, response = self.client.live_demo_create({'subscribe': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0226')

        code, response = self.client.live_demo_create({'email': 'value'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0218')

    def test_live_demo_subscriber_email(self):
        patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
              'get_top_resources_by_total_cost', return_value=[]).start()
        p_send = patch('rest_api.rest_api_server.controllers.live_demo.'
                       'LiveDemoController._send_subscribe_email').start()
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
                   'load_preset', return_value=deepcopy(self.preset)).start():
            code, response = self.client.live_demo_create()
            self.assertEqual(code, 201)
            p_send.assert_not_called()
        with patch('rest_api.rest_api_server.controllers.live_demo.LiveDemoController.'
                   'load_preset', return_value=deepcopy(self.preset)).start():
            code, response = self.client.live_demo_create({
                'email': 'some@email.com',
                'subscribe': False
            })
            self.assertEqual(code, 201)
            p_send.assert_called_once()
