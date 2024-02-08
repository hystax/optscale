import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from copy import deepcopy
from freezegun import freeze_time
from pymongo import UpdateMany
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import Checklist
from rest_api.rest_api_server.exceptions import Err

from rest_api.rest_api_server.utils import get_nil_uuid
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestExpensesApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.p_create_rule = patch(
            'rest_api.rest_api_server.controllers.rule.RuleController.'
            'create_rule').start()
        cloud_acc1 = {
            'name': 'cloud_acc1',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        cloud_acc2 = {
            'name': 'cloud_acc2',
            'type': 'azure_cnr',
            'config': {
                'subscription_id': 'id',
                'secret': 'secret',
                'client_id': 'id',
                'tenant': 't',
            }
        }
        cloud_acc3 = {
            'name': 'cloud_acc3',
            'type': 'kubernetes_cnr',
            'config': {
                'password': 'secret',
                'user': 'user',
                'cost_model': {}
            }
        }
        self.auth_user_id_1 = self.gen_id()
        self.auth_user_id_2 = self.gen_id()
        self.auth_user_id_3 = self.gen_id()
        _, self.employee1 = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.employee2 = self.client.employee_create(
            self.org_id, {'name': 'name2', 'auth_user_id': self.auth_user_id_2})
        _, self.employee3 = self.client.employee_create(
            self.org_id, {'name': 'name3', 'auth_user_id': self.auth_user_id_3})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc2, auth_user_id=self.auth_user_id_2)
        _, self.cloud_acc3 = self.create_cloud_account(
            self.org_id, cloud_acc3, auth_user_id=self.auth_user_id_3)

        _, self.sub_pool1 = self.client.pool_create(self.org_id, {
            'name': 'sub1',
            'parent_id': self.org['pool_id'],
        })
        _, self.sub_pool2 = self.client.pool_create(self.org_id, {
            'name': 'sub2',
            'parent_id': self.sub_pool1['id'],
        })

        self.prev_start = datetime(2020, 3, 30, 0, 0)
        self.prev_start_ts = int(self.prev_start.timestamp())
        self.prev_second = self.prev_start + timedelta(days=1)
        self.start_date = datetime(2020, 4, 1, 0, 0)
        self.end_date = datetime(2020, 4, 2, 23, 59)
        self.second_date = self.start_date + timedelta(days=1)
        self.start_ts = int(self.start_date.timestamp())
        self.end_ts = int(self.end_date.timestamp())
        self.second_ts = int(self.second_date.timestamp())
        self.nil_uuid = get_nil_uuid()
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee1['id'])

    def get_expenses_with_available_filters(self, *args, is_clean=True):
        if is_clean:
            code, response = self.client.clean_expenses_get(*args)
        else:
            code, response = self.client.summary_expenses_get(*args)
        self.assertEqual(code, 200)
        try:
            args[3].pop('limit')
        except BaseException:
            pass
        code, filters = self.client.available_filters_get(*args)
        self.assertEqual(code, 200)
        response.update(filters)
        return code, response

    def _make_resources_constraint_violated(self, resource_ids, value=True):
        self.resources_collection.bulk_write([UpdateMany(
            filter={'_id': {'$in': resource_ids}},
            update={'$set': {'constraint_violated': value}},
        )])

    def create_cloud_resource(self, cloud_account_id, employee_id=None,
                              pool_id=None, resource_type='test_type',
                              name='test_resource', tags=None, last_seen=None,
                              region=None, created_by_kind=None, created_by_name=None,
                              host_ip=None, instance_address=None, k8s_namespace=None,
                              k8s_node=None, pod_ip=None, first_seen=None, k8s_service=None,
                              service_name=None, resource_hash=None):
        now = int(datetime.utcnow().timestamp())
        resource = {
            'cloud_resource_id': self.gen_id(),
            'name': name,
            'resource_type': resource_type,
            'employee_id': employee_id,
            'pool_id': pool_id,
            'last_seen': last_seen or now,
            'first_seen': first_seen or now,
            'region': region,
            'service_name': service_name,
            'meta': {}
        }

        if tags:
            resource.update({'tags': tags})
        if created_by_kind:
            resource.update({'created_by_kind': created_by_kind})
        if created_by_name:
            resource.update({'created_by_name': created_by_name})
        if host_ip:
            resource['meta'].update({'host_ip': host_ip})
        if instance_address:
            resource['meta'].update({'instance_address': instance_address})
        if k8s_namespace:
            resource.update({'k8s_namespace': k8s_namespace})
        if k8s_node:
            resource.update({'k8s_node': k8s_node})
        if pod_ip:
            resource['meta'].update({'pod_ip': pod_ip})
        if k8s_service:
            resource.update({'k8s_service': k8s_service})
        if resource_hash:
            resource.update({'cloud_resource_hash': resource_hash})
        code, resource = self.cloud_resource_create(
            cloud_account_id, resource)
        return code, resource

    def add_recommendations(self, resource_id, modules, timestamp=None,
                            last_check=None, pool_id=None, checklist=True):
        if not timestamp:
            timestamp = int(datetime.utcnow().timestamp())

        recommendations = {
            'modules': modules,
            'run_timestamp': timestamp
        }
        if checklist:
            db = DBFactory(DBType.Test, None).db
            engine = db.engine
            session = BaseDB.session(engine)()
            if not last_check:
                last_check = timestamp
            record = Checklist(
                organization_id=self.org_id,
                last_run=last_check,
                last_completed=last_check
            )
            session.add(record)
            session.commit()
        updates = {
            'recommendations': recommendations,
            'active': True,
            'last_seen': int(datetime.utcnow().timestamp())
        }
        if pool_id:
            updates['pool_id'] = pool_id
        self.resources_collection.update_one(
            filter={
                '_id': resource_id
            },
            update={'$set': updates}
        )

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_get_no_filter(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.0,
                '_id': {'date': self.prev_start},
            },
            {
                'cost': 0.2,
                '_id': {'date': self.prev_second},
            },
            {
                'cost': 3.3,
                '_id': {'date': self.start_date},
            },
            {
                'cost': 2.0,
                '_id': {'date': self.second_date},
            }
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], self.start_ts, self.end_ts)
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 5.3,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.org['pool_id'],
                'name': self.org['name'],
                'breakdown': {
                    str(self.start_ts): 3.3,
                    str(self.second_ts): 2.0,
                }
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id',
            [self.cloud_acc1['id'], self.cloud_acc2['id'], self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by=None)

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_get_no_filter_for_sub_pool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.2,
                '_id': {'date': self.prev_start},
            },
            {
                'cost': 3.3,
                '_id': {'date': self.start_date},
            },
            {
                'cost': 2.0,
                '_id': {'date': self.second_date},
            }
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.sub_pool1['id'], self.start_ts, self.end_ts)
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 5.3,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.sub_pool1['id'],
                'name': self.sub_pool1['name'],
                'breakdown': {
                    str(self.start_ts): 3.3,
                    str(self.second_ts): 2.0,
                }
            }
        })
        p_expenses.assert_called_once_with(
            'pool_id',
            [self.sub_pool1['id'], self.sub_pool2['id']],
            self.prev_start, self.end_date, group_by=None)

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_cloud(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.0,
                '_id': {
                    'date': self.prev_start,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 0.2,
                '_id': {
                    'date': self.prev_second,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], self.start_ts, self.end_ts, filter_by='cloud')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.org['pool_id'],
                'name': self.org['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 2.0,
                        }
                    ],
                },
                'cloud': [
                    {
                        'id': self.cloud_acc1['id'],
                        'name': self.cloud_acc1['name'],
                        'type': self.cloud_acc1['type'],
                        'total': 4.0,
                        'previous_total': 4.0,
                    },
                    {
                        'id': self.cloud_acc2['id'],
                        'name': self.cloud_acc2['name'],
                        'type': self.cloud_acc2['type'],
                        'total': 3.0,
                        'previous_total': 0.2,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id',
            [self.cloud_acc1['id'], self.cloud_acc2['id'], self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='cloud_account_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_cloud_for_subpool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.2,
                '_id': {
                    'date': self.prev_start,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.sub_pool1['id'], self.start_ts, self.end_ts, filter_by='cloud')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.sub_pool1['id'],
                'name': self.sub_pool1['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 2.0,
                        }
                    ],
                },
                'cloud': [
                    {
                        'id': self.cloud_acc1['id'],
                        'name': self.cloud_acc1['name'],
                        'type': self.cloud_acc1['type'],
                        'total': 4.0,
                        'previous_total': 4.2,
                    },
                    {
                        'id': self.cloud_acc2['id'],
                        'name': self.cloud_acc2['name'],
                        'type': self.cloud_acc2['type'],
                        'total': 3.0,
                        'previous_total': 0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'pool_id',
            [self.sub_pool1['id'], self.sub_pool2['id']],
            self.prev_start, self.end_date, group_by='cloud_account_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_pool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.5,
                '_id': {
                    'date': self.prev_start,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.prev_second,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.2,
                '_id': {
                    'date': self.prev_second,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': None,
                },
            },
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], self.start_ts, self.end_ts, filter_by='pool')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 9.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.org['pool_id'],
                'name': self.org['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 3.3,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 1.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 0.7,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 2.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                },
                'pool': [
                    {
                        'id': self.sub_pool1['id'],
                        'name': self.sub_pool1['name'],
                        'total': 4.0,
                        'previous_total': 4.0,
                        'purpose': self.sub_pool1['purpose']
                    },
                    {
                        'id': self.sub_pool2['id'],
                        'name': self.sub_pool2['name'],
                        'total': 3.0,
                        'previous_total': 0.2,
                        'purpose': self.sub_pool2['purpose']
                    },
                    {
                        'id': self.nil_uuid,
                        'name': '(not set)',
                        'total': 2.0,
                        'previous_total': 0,
                        'purpose': '(not set)',
                    }
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id',
            [self.cloud_acc1['id'], self.cloud_acc2['id'], self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='pool_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_pool_for_subpool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_second,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool2['id'],
                },
            }
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.sub_pool1['id'], self.start_ts, self.end_ts, filter_by='pool')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.sub_pool1['id'],
                'name': self.sub_pool1['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 3.3,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 1.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 0.7,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 2.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                    ],
                },
                'pool': [
                    {
                        'id': self.sub_pool1['id'],
                        'name': self.sub_pool1['name'],
                        'total': 4.0,
                        'previous_total': 3.3,
                        'purpose': self.sub_pool1['purpose']
                    },
                    {
                        'id': self.sub_pool2['id'],
                        'name': self.sub_pool2['name'],
                        'total': 3.0,
                        'previous_total': 0.9,
                        'purpose': self.sub_pool2['purpose']
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'pool_id',
            [self.sub_pool1['id'], self.sub_pool2['id']],
            self.prev_start, self.end_date, group_by='pool_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_employee(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.2,
                '_id': {
                    'date': self.prev_start,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee2['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'owner_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'owner_id': None,
                },
            },
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], self.start_ts, self.end_ts, filter_by='employee')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 9.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.org['pool_id'],
                'name': self.org['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 1.0,
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 2.0,
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                        },
                    ],
                },
                'employee': [
                    {
                        'id': self.employee1['id'],
                        'name': self.employee1['name'],
                        'total': 4.0,
                        'previous_total': 4.2,
                    },
                    {
                        'id': self.employee2['id'],
                        'name': self.employee2['name'],
                        'total': 3.0,
                        'previous_total': 0,
                    },
                    {
                        'id': self.nil_uuid,
                        'name': '(not set)',
                        'total': 2.0,
                        'previous_total': 0,
                    }
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id',
            [self.cloud_acc1['id'], self.cloud_acc2['id'], self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='owner_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_pool_filter_by_employee_for_subpool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee2['id'],
                },
            },
        ]
        code, r = self.client.pool_breakdown_expenses_get(
            self.sub_pool1['id'], self.start_ts, self.end_ts, filter_by='employee')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 0,
                'previous_range_start': self.prev_start_ts,
                'id': self.sub_pool1['id'],
                'name': self.sub_pool1['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 1.0,
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 2.0,
                        },
                    ],
                },
                'employee': [
                    {
                        'id': self.employee1['id'],
                        'name': self.employee1['name'],
                        'total': 4.0,
                        'previous_total': 0,
                    },
                    {
                        'id': self.employee2['id'],
                        'name': self.employee2['name'],
                        'total': 3.0,
                        'previous_total': 0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'pool_id',
            [self.sub_pool1['id'], self.sub_pool2['id']],
            self.prev_start, self.end_date, group_by='owner_id')

    def test_cloud_get_no_filter(self):
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(r['error']['reason'], 'filter_by is not provided')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_service(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 4.0,
                '_id': {
                    'date': self.prev_start,
                    'service_name': 'service1',
                },
            },
            {
                'cost': 0.2,
                '_id': {
                    'date': self.prev_second,
                    'service_name': 'service1',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'service_name': 'service1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'service_name': 'service1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'service_name': 'service2',
                },
            },
            {
                'cost': 1.1,
                '_id': {
                    'date': self.second_date,
                    'service_name': 'service2',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.second_date,
                    'service_name': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts, filter_by='service')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'service1',
                            'name': 'service1',
                            'expense': 3.3,
                        },
                        {
                            'id': 'service2',
                            'name': 'service2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'service1',
                            'name': 'service1',
                            'expense': 0.7,
                        },
                        {
                            'id': 'service2',
                            'name': 'service2',
                            'expense': 1.1,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.9,
                        },
                    ],
                },
                'service': [
                    {
                        'id': 'service1',
                        'name': 'service1',
                        'total': 4.0,
                        'previous_total': 4.2,
                    },
                    {
                        'id': 'service2',
                        'name': 'service2',
                        'total': 2.1,
                        'previous_total': 0,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.9,
                        'previous_total': 0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc1['id']],
            self.prev_start, self.end_date, group_by='service_name')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_region(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'region': 'region1',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'region': 'region2',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'region': 'region1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'region': 'region1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'region': 'region2',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'region': 'region2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'region': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts, filter_by='region')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'region1',
                            'name': 'region1',
                            'expense': 3.3,
                        },
                        {
                            'id': 'region2',
                            'name': 'region2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'region1',
                            'name': 'region1',
                            'expense': 0.7,
                        },
                        {
                            'id': 'region2',
                            'name': 'region2',
                            'expense': 1.5,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.5,
                        }
                    ],
                },
                'region': [
                    {
                        'id': 'region1',
                        'name': 'region1',
                        'total': 4.0,
                        'previous_total': 3.3,
                    },
                    {
                        'id': 'region2',
                        'name': 'region2',
                        'total': 2.5,
                        'previous_total': 0.9,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.5,
                        'previous_total': 0.0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc1['id']],
            self.prev_start, self.end_date, group_by='region')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_node(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'k8s_node': 'node1',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'k8s_node': 'node2',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'k8s_node': 'node1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'k8s_node': 'node1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'k8s_node': 'node2',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_node': 'node2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_node': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc3['id'], self.start_ts, self.end_ts, filter_by='k8s_node')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc3['id'],
                'name': self.cloud_acc3['name'],
                'type': self.cloud_acc3['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'node1',
                            'name': 'node1',
                            'expense': 3.3,
                        },
                        {
                            'id': 'node2',
                            'name': 'node2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'node1',
                            'name': 'node1',
                            'expense': 0.7,
                        },
                        {
                            'id': 'node2',
                            'name': 'node2',
                            'expense': 1.5,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.5,
                        }
                    ],
                },
                'k8s_node': [
                    {
                        'id': 'node1',
                        'name': 'node1',
                        'total': 4.0,
                        'previous_total': 3.3,
                    },
                    {
                        'id': 'node2',
                        'name': 'node2',
                        'total': 2.5,
                        'previous_total': 0.9,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.5,
                        'previous_total': 0.0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='k8s_node')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_namespace(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'k8s_namespace': 'namespace1',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'k8s_namespace': 'namespace2',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'k8s_namespace': 'namespace1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'k8s_namespace': 'namespace1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'k8s_namespace': 'namespace2',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_namespace': 'namespace2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_namespace': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc3['id'], self.start_ts, self.end_ts, filter_by='k8s_namespace')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc3['id'],
                'name': self.cloud_acc3['name'],
                'type': self.cloud_acc3['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'namespace1',
                            'name': 'namespace1',
                            'expense': 3.3,
                        },
                        {
                            'id': 'namespace2',
                            'name': 'namespace2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'namespace1',
                            'name': 'namespace1',
                            'expense': 0.7,
                        },
                        {
                            'id': 'namespace2',
                            'name': 'namespace2',
                            'expense': 1.5,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.5,
                        }
                    ],
                },
                'k8s_namespace': [
                    {
                        'id': 'namespace1',
                        'name': 'namespace1',
                        'total': 4.0,
                        'previous_total': 3.3,
                    },
                    {
                        'id': 'namespace2',
                        'name': 'namespace2',
                        'total': 2.5,
                        'previous_total': 0.9,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.5,
                        'previous_total': 0.0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='k8s_namespace')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_k8s_service(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'k8s_service': 'service1',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'k8s_service': 'service2',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'k8s_service': 'service1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'k8s_service': 'service1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'k8s_service': 'service2',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_service': 'service2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'k8s_service': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc3['id'], self.start_ts, self.end_ts, filter_by='k8s_service')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc3['id'],
                'name': self.cloud_acc3['name'],
                'type': self.cloud_acc3['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'service1',
                            'name': 'service1',
                            'expense': 3.3,
                        },
                        {
                            'id': 'service2',
                            'name': 'service2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'service1',
                            'name': 'service1',
                            'expense': 0.7,
                        },
                        {
                            'id': 'service2',
                            'name': 'service2',
                            'expense': 1.5,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.5,
                        }
                    ],
                },
                'k8s_service': [
                    {
                        'id': 'service1',
                        'name': 'service1',
                        'total': 4.0,
                        'previous_total': 3.3,
                    },
                    {
                        'id': 'service2',
                        'name': 'service2',
                        'total': 2.5,
                        'previous_total': 0.9,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.5,
                        'previous_total': 0.0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='k8s_service')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_field_not_exists_in_expenses(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'test': 'test1',
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'test': 'test2',
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'test': 'test1',
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'test': 'test1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'test': 'test2',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'test': 'test2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'test': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc3['id'], self.start_ts, self.end_ts, filter_by='region')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc3['id'],
                'name': self.cloud_acc3['name'],
                'type': self.cloud_acc3['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'expense': 4.3,
                            'id': '00000000-0000-0000-0000-000000000000',
                            'name': '(not set)'
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'expense': 2.7,
                            'id': '00000000-0000-0000-0000-000000000000',
                            'name': '(not set)'
                        },
                    ],
                },
                'region': [
                    {
                        'id': '00000000-0000-0000-0000-000000000000',
                        'name': '(not set)',
                        'previous_total': 4.2,
                        'total': 7.0
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='region')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_get_filter_by_resource_type(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 5.0,
                '_id': {
                    'date': self.prev_start,
                    'resource_type': 'type1',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.prev_start,
                    'resource_type': 'type2',
                },
            },
            {
                'cost': 4.5,
                '_id': {
                    'date': self.start_date,
                    'resource_type': 'type1',
                },
            },
            {
                'cost': 1.5,
                '_id': {
                    'date': self.second_date,
                    'resource_type': 'type1',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'resource_type': 'type2',
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'resource_type': 'type2',
                },
            },
            {
                'cost': 0.5,
                '_id': {
                    'date': self.second_date,
                    'resource_type': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts, filter_by='resource_type')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 8.5,
                'previous_total': 6.5,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': 'type1',
                            'name': 'type1',
                            'expense': 4.5,
                        },
                        {
                            'id': 'type2',
                            'name': 'type2',
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': 'type1',
                            'name': 'type1',
                            'expense': 1.5,
                        },
                        {
                            'id': 'type2',
                            'name': 'type2',
                            'expense': 1.0,
                        },
                        {
                            'id': get_nil_uuid(),
                            'name': '(not set)',
                            'expense': 0.5,
                        }
                    ],
                },
                'resource_type': [
                    {
                        'id': 'type1',
                        'name': 'type1',
                        'total': 6.0,
                        'previous_total': 5.0,
                    },
                    {
                        'id': 'type2',
                        'name': 'type2',
                        'total': 2.0,
                        'previous_total': 1.5,
                    },
                    {
                        'id': get_nil_uuid(),
                        'name': '(not set)',
                        'total': 0.5,
                        'previous_total': 0.0,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc1['id']],
            self.prev_start, self.end_date, group_by='resource_type')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_filter_by_employee(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 2.4,
                '_id': {
                    'date': self.prev_start,
                    'owner_id': None,
                },
            },
            {
                'cost': 1.8,
                '_id': {
                    'date': self.prev_second,
                    'owner_id': None,
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'owner_id': self.employee2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'owner_id': self.employee2['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'owner_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'owner_id': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts, filter_by='employee')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 9.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 1.0,
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.employee1['id'],
                            'name': self.employee1['name'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.employee2['id'],
                            'name': self.employee2['name'],
                            'expense': 2.0,
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                        },
                    ],
                },
                'employee': [
                    {
                        'id': self.employee1['id'],
                        'name': self.employee1['name'],
                        'total': 4.0,
                        'previous_total': 0,
                    },
                    {
                        'id': self.employee2['id'],
                        'name': self.employee2['name'],
                        'total': 3.0,
                        'previous_total': 0,
                    },
                    {
                        'id': self.nil_uuid,
                        'name': '(not set)',
                        'total': 2.0,
                        'previous_total': 4.2,
                    }
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc1['id']],
            self.prev_start, self.end_date, group_by='owner_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_cloud_filter_by_pool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 1.2,
                '_id': {
                    'date': self.prev_start,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 3.0,
                '_id': {
                    'date': self.prev_second,
                    'pool_id': None,
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': None,
                },
            },
        ]
        code, r = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], self.start_ts, self.end_ts,
            filter_by='pool')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 9.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.cloud_acc1['id'],
                'name': self.cloud_acc1['name'],
                'type': self.cloud_acc1['type'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 3.3,
                            'purpose': self.sub_pool1['purpose'],
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 1.0,
                            'purpose': self.sub_pool2['purpose'],
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 0.7,
                            'purpose': self.sub_pool1['purpose'],
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 2.0,
                            'purpose': self.sub_pool2['purpose'],
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                },
                'pool': [
                    {
                        'id': self.sub_pool1['id'],
                        'name': self.sub_pool1['name'],
                        'total': 4.0,
                        'previous_total': 1.2,
                        'purpose': self.sub_pool1['purpose']
                    },
                    {
                        'id': self.sub_pool2['id'],
                        'name': self.sub_pool2['name'],
                        'total': 3.0,
                        'previous_total': 0,
                        'purpose': self.sub_pool2['purpose']
                    },
                    {
                        'id': self.nil_uuid,
                        'name': '(not set)',
                        'total': 2.0,
                        'previous_total': 3.0,
                        'purpose': '(not set)',
                    }
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'cloud_account_id', [self.cloud_acc1['id']],
            self.prev_start, self.end_date, group_by='pool_id')

    def test_employee_get_no_filter(self):
        code, r = self.client.employee_expenses_get(
            self.employee1['id'], self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(r['error']['reason'], 'filter_by is not provided')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_employee_filter_by_pool(self, p_expenses):
        p_expenses.return_value = [
            {
                'cost': 3.2,
                '_id': {
                    'date': self.prev_start,
                    'pool_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.prev_second,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': self.sub_pool2['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'pool_id': None,
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.second_date,
                    'pool_id': None,
                },
            },
        ]
        code, r = self.client.employee_expenses_get(
            self.employee1['id'], self.start_ts, self.end_ts,
            filter_by='pool')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 9.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.employee1['id'],
                'name': self.employee1['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 3.3,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 1.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.sub_pool1['id'],
                            'name': self.sub_pool1['name'],
                            'expense': 0.7,
                            'purpose': self.sub_pool1['purpose']
                        },
                        {
                            'id': self.sub_pool2['id'],
                            'name': self.sub_pool2['name'],
                            'expense': 2.0,
                            'purpose': self.sub_pool2['purpose']
                        },
                        {
                            'id': self.nil_uuid,
                            'name': '(not set)',
                            'expense': 1.0,
                            'purpose': '(not set)',
                        },
                    ],
                },
                'pool': [
                    {
                        'id': self.sub_pool1['id'],
                        'name': self.sub_pool1['name'],
                        'total': 4.0,
                        'previous_total': 1.0,
                        'purpose': self.sub_pool1['purpose']
                    },
                    {
                        'id': self.sub_pool2['id'],
                        'name': self.sub_pool2['name'],
                        'total': 3.0,
                        'previous_total': 0,
                        'purpose': self.sub_pool2['purpose']
                    },
                    {
                        'id': self.nil_uuid,
                        'name': '(not set)',
                        'total': 2.0,
                        'previous_total': 3.2,
                        'purpose': '(not set)',
                    }
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'owner_id', [self.employee1['id']],
            self.prev_start, self.end_date, group_by='pool_id')

    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_employee_filter_by_cloud(self, p_expenses):
        self.end_date = datetime(2020, 4, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())
        p_expenses.return_value = [
            {
                'cost': 1.8,
                '_id': {
                    'date': self.prev_start,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 2.4,
                '_id': {
                    'date': self.prev_start,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc1['id'],
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'cloud_account_id': self.cloud_acc2['id'],
                },
            },
        ]
        code, r = self.client.employee_expenses_get(
            self.employee1['id'], self.start_ts, self.end_ts, filter_by='cloud')
        self.assertEqual(code, 200)
        self.assertEqual(r, {
            'expenses': {
                'total': 7.0,
                'previous_total': 4.2,
                'previous_range_start': self.prev_start_ts,
                'id': self.employee1['id'],
                'name': self.employee1['name'],
                'breakdown': {
                    str(self.start_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 3.3,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 1.0,
                        }
                    ],
                    str(self.second_ts): [
                        {
                            'id': self.cloud_acc1['id'],
                            'name': self.cloud_acc1['name'],
                            'type': self.cloud_acc1['type'],
                            'expense': 0.7,
                        },
                        {
                            'id': self.cloud_acc2['id'],
                            'name': self.cloud_acc2['name'],
                            'type': self.cloud_acc2['type'],
                            'expense': 2.0,
                        }
                    ],
                },
                'cloud': [
                    {
                        'id': self.cloud_acc1['id'],
                        'name': self.cloud_acc1['name'],
                        'type': self.cloud_acc1['type'],
                        'total': 4.0,
                        'previous_total': 1.8,
                    },
                    {
                        'id': self.cloud_acc2['id'],
                        'name': self.cloud_acc2['name'],
                        'type': self.cloud_acc2['type'],
                        'total': 3.0,
                        'previous_total': 2.4,
                    },
                ]
            }
        })
        p_expenses.assert_called_once_with(
            'owner_id', [self.employee1['id']],
            self.prev_start, self.end_date, group_by='cloud_account_id')

    def test_raw_expenses_unexpected_filters(self):
        self.end_date = datetime(2020, 4, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())
        filters_map = {
            'not_a_region': 'us-east',
            'cloud_resource_id': 'cloud_resource_id',
            'type_resource_type': 'type_resource_type',
            'service_name': 'service_name'
        }
        for f_name, f_value in filters_map.items():
            code, response = self.client.raw_expenses_get(
                self.org_id, self.start_ts, self.end_ts, {f_name: f_value})
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['error_code'], 'OE0212')

    def test_raw_expenses(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc2['id'], tags={'some': 'thing'}, region='us-test')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'region': resource2['region'],
                'resource_id': resource2['id'],
                'raw': [
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': self.cloud_acc2['id'],
                        'resource_id': resource2['cloud_resource_id']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': self.cloud_acc2['id'],
                        'resource_id': resource2['cloud_resource_id']
                    }
                ],
            }
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        code, response = self.client.raw_expenses_get(
            resource2['id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 300)
        self.assertTrue(len(response['raw_expenses']) == 2)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 2', 'raw 3'])

    def test_raw_expenses_limit(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 450, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    },
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    }
                ],
            },
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        code, response = self.client.raw_expenses_get(
            resource1['id'], time - 100, time + 100, {'limit': 2})
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 450)
        self.assertTrue(len(response['raw_expenses']) == 2)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 1', 'raw 3'])

        for limit in [0, -1, 'a']:
            code, response = self.client.raw_expenses_get(
                resource1['id'], time - 100, time + 100, {'limit': limit})
            self.assertEqual(code, 400)

    def test_raw_expenses_by_hash(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east', resource_hash='hash')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 450, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_hash': resource1['cloud_resource_hash']
                    },
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_hash': resource1['cloud_resource_hash']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_hash': resource1['cloud_resource_hash']
                    }
                ],
            },
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        code, response = self.client.raw_expenses_get(
            resource1['id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 450)
        self.assertTrue(len(response['raw_expenses']) == 3)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 1', 'raw 2', 'raw 3'])

    def test_raw_expenses_format(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 450, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    },
                ],
            },
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        for format_ in ['json', 'advanced_json']:
            code, response = self.client.raw_expenses_get(
                resource1['id'], time - 100, time + 100, {'format': format_})
            self.assertEqual(code, 200)

    def test_raw_clean_summary_expenses_total_cost(self):
        time = datetime(2021, 8, 1)
        time_ts = int(time.timestamp())
        time_with_delta = time + timedelta(days=2)
        time_with_delta_ts = int(time_with_delta.timestamp())
        start_month = int(datetime(2021, 8, 1).timestamp())
        end_month = int(datetime(2021, 9, 1).timestamp()) - 1
        raw_expenses = [
            {
                'name': 'raw 1',
                'start_date': time,
                'end_date': time + timedelta(days=3),
                'cost': 90
            }
        ]
        expenses = [
            {
                'cost': 30, 'date': time,
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id']
            },
            {
                'cost': 30, 'date': time + timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': None,
                'pool_id': None
            },
            {
                'cost': 30, 'date': time_with_delta,
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': None,
                'pool_id': None
            }
        ]
        _, resource = self.create_cloud_resource(
            expenses[0]['cloud_acc'], employee_id=expenses[0]['owner_id'],
            pool_id=expenses[0]['pool_id'], first_seen=time_ts,
            last_seen=time_ts + 1)
        for raw in raw_expenses:
            raw.update({
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource['cloud_resource_id']
            })
        self.raw_expenses.insert_many(raw_expenses)
        for e in expenses:
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        cases = [
            (start_month, end_month, 90),
            (start_month - 1, time_ts - 1, 0),
            (start_month, time_with_delta_ts - 1, 60),
            (time_ts, time_with_delta_ts - 1, 60),
            (time_ts, int((time_with_delta + timedelta(days=1)).timestamp()), 90),
            (time_ts, int((time + timedelta(days=1, seconds=-1)).timestamp()), 30)]

        for case in cases:
            code, raw_response = self.client.raw_expenses_get(
                resource['id'], case[0], case[1])
            self.assertEqual(code, 200)
            code, clean_response = self.client.clean_expenses_get(
                self.org_id, case[0], case[1])
            self.assertEqual(code, 200)

            self.assertEqual(clean_response['total_cost'],
                             raw_response['total_cost'])
            self.assertEqual(raw_response['total_cost'], case[2])

    def test_expenses_dates_values(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        filters = {}
        min_timestamp = 0
        max_timestamp = int(datetime.max.replace(
            tzinfo=timezone.utc).timestamp()) - 1
        code, response = self.client.raw_expenses_get(
            resource1['id'], min_timestamp, max_timestamp, filters)
        self.assertEqual(code, 200)
        code, response = self.client.raw_expenses_get(
            resource1['id'], min_timestamp - 1, max_timestamp, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')
        code, response = self.client.raw_expenses_get(
            resource1['id'], min_timestamp, max_timestamp + 1, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')
        code, response = self.client.raw_expenses_get(
            resource1['id'], min_timestamp - 1, 0, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

        code, response = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], min_timestamp, max_timestamp + 1)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

        code, response = self.client.cloud_expenses_get(
            self.cloud_acc1['id'], min_timestamp, max_timestamp + 1,
            filter_by='service')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

        code, response = self.client.employee_expenses_get(
            self.employee1['id'], min_timestamp, max_timestamp + 1,
            filter_by='pool')
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0224')

    def test_summary_clean_expenses(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='name_1', first_seen=time, tags={'tag': 'val'}, region='region_1',
            service_name='service_name_1', resource_type='resource_type_1')
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc2['id'], self.employee2['id'], self.org['pool_id'],
            name='name_2', first_seen=time, tags={'tag_2': 'val'}, region='region_2',
            service_name='service_name_2', resource_type='resource_type_2')
        _, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='name_3', first_seen=time, tags={'tag': 'val'}, region='region_1',
            service_name='service_name_1', resource_type='resource_type_1')
        expenses = [
            {
                'cost': 150, 'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
            },
            {
                'cost': 300, 'date': day_in_month,
                'cloud_acc': self.cloud_acc2['id'],
                'region': 'us-east',
                'resource_id': resource2['id'],
                'owner_id': self.employee2['id'],
                'pool_id': self.org['pool_id'],
            },
            {
                'cost': 70, 'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource3['id'],
                'pool_id': self.org['pool_id'],
                'owner_id': self.employee1['id'],
            },
        ]

        for e in expenses:
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        validation_map = {
            'cloud_account_id': [
                (self.cloud_acc1['id'], self.cloud_acc1['id'], 220, 2, 2),
                (self.cloud_acc2['id'], self.cloud_acc2['id'], 300, 1, 1)
            ],
            'pool_id': [
                (self.org['pool_id'], self.org['pool_id'], 520, 3, 3)
            ],
            'owner_id': [
                (self.employee1['id'], self.employee1['id'], 220, 2, 2),
                (self.employee2['id'], self.employee2['id'], 300, 1, 1)
            ],
            'region': [
                ('region_1', 'region_1', 220, 2, 2),
                ('region_2', 'region_2', 300, 1, 1)
            ],
            'service_name': [
                ('service_name_1', 'service_name_1', 220, 2, 2),
                ('service_name_2', 'service_name_2', 300, 1, 1)
            ],
            'resource_type': [
                ('resource_type_1:regular', 'resource_type_1', 220, 2, 2),
                ('resource_type_2:regular', 'resource_type_2', 300, 1, 1)
            ]
        }
        for filter_name, cases in validation_map.items():
            for validation_data in cases:
                (filter_value, check_value, total_cost,
                 records_count, total_count) = validation_data
                filters = {
                    filter_name: filter_value,
                }
                code, clean_response = self.client.clean_expenses_get(
                    self.org_id, time, time + 1, filters)
                self.assertEqual(code, 200)
                self.assertEqual(clean_response['total_cost'], total_cost)
                self.assertEqual(len(clean_response['clean_expenses']),
                                 records_count)
                self.assertEqual(clean_response['total_count'], total_count)
                check_key = filter_name
                if check_key == 'owner_id':
                    check_key = 'employee_id'
                self.assertTrue(all(map(
                    lambda x: x[check_key] == check_value,
                    clean_response['clean_expenses'])))
                self.assertEqual(clean_response['start_date'], time)
                self.assertEqual(clean_response['end_date'], time + 1)
                code, summary_response = self.client.summary_expenses_get(
                    self.org_id, time, time + 1, filters)
                self.assertEqual(code, 200)
                self.assertEqual(summary_response['total_cost'], total_cost)
                self.assertEqual(summary_response['total_count'], total_count)
                self.assertEqual(summary_response['start_date'], time)
                self.assertEqual(summary_response['end_date'], time + 1)

        filters = {
            'cloud_account_id': resource2['cloud_account_id'],
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        clean_expense = response['clean_expenses'][0]
        self.assertEqual(clean_expense['resource_id'], resource2['id'])
        owner = clean_expense['owner']
        self.assertEqual(owner['id'], self.employee2['id'])
        self.assertEqual(owner['name'], self.employee2['name'])
        pool = clean_expense['pool']
        self.assertEqual(pool['id'], self.org['pool_id'])
        self.assertEqual(pool['name'], self.org['name'])
        self.assertEqual(pool['purpose'], 'business_unit')

    def test_summary_clean_expenses_filter_by_active(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res2', first_seen=time, last_seen=time + 1)
        expenses = [
            {
                'cost': 150,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 1'}]
            },
            {
                'cost': 300,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 2'}]
            },
            {
                'cost': 70,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 4'}, {'name': 'raw 5'}, {'name': 'raw 6'}]
            },
            {
                'cost': 150,
                'date': day_in_month,
                'cloud_acc': 'fake cloud acc id',
                'region': 'us-east',
                'resource_id': 'res_3_id',
                'raw': [{'name': 'raw 7'}]
            }
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        self._make_resources_active([resource1['id']])

        filters = {}
        code, clean_response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(clean_response['total_cost'], 520)
        clean_expenses = clean_response['clean_expenses']
        exp_map = {
            resource1['id']: (450, 2, True),
            resource2['id']: (70, 3, False)
        }
        code, summary_response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(summary_response['total_cost'], 520)
        for clean_expense in clean_expenses:
            self.assertTrue(
                clean_expense['resource_id'] in [
                    resource1['id'], resource2['id']])
            cost, raw_links, active = exp_map[clean_expense['resource_id']]
            self.assertEqual(cost, clean_expense['cost'])
            self.assertIsNotNone(clean_expense['resource_id'])
            self.assertEqual(clean_expense['active'], active)

        filters = {'active': True}
        code, clean_response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(clean_response['total_cost'], 450)
        self.assertEqual(len(clean_response['clean_expenses']), 1)
        self.assertEqual(clean_response['total_count'], 1)
        clean_expense = clean_response['clean_expenses'][0]
        self.assertTrue(clean_expense['resource_id'], resource1['id'])
        cost, raw_links, active = exp_map[clean_expense['resource_id']]
        self.assertEqual(cost, clean_expense['cost'])
        self.assertIsNotNone(clean_expense['resource_id'])
        self.assertEqual(clean_expense['active'], active)

        code, summary_response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(summary_response['total_cost'], 450)
        self.assertEqual(summary_response['total_count'], 1)

        filters = {'active': False}
        code, clean_response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(clean_response['total_cost'], 70)
        self.assertEqual(len(clean_response['clean_expenses']), 1)
        self.assertEqual(clean_response['total_count'], 1)
        clean_expense = clean_response['clean_expenses'][0]
        self.assertTrue(clean_expense['resource_id'], resource2['id'])
        cost, raw_links, active = exp_map[clean_expense['resource_id']]
        self.assertEqual(cost, clean_expense['cost'])
        self.assertIsNotNone(clean_expense['resource_id'])
        self.assertEqual(clean_expense['active'], active)

        code, summary_response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(summary_response['total_cost'], 70)
        self.assertEqual(summary_response['total_count'], 1)

    def test_summary_clean_expenses_filter_by_tag(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], name='res1',
            first_seen=time, last_seen=time + 1, tags={'hello': 'world'})
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], name='res2',
            first_seen=time, last_seen=time + 1, tags={'world': 'hello'})
        _, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], name='res3',
            first_seen=time, last_seen=time + 1,
            tags={'hello': 'world', 'world': 'hello'})
        expenses = [
            {
                'cost': 200,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'raw': [{'name': 'raw 2'}]
            },
            {
                'cost': 100,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'raw': [{'name': 'raw 4'}, {'name': 'raw 5'}, {'name': 'raw 6'}]
            },
            {
                'cost': 300,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource3['id'],
                'raw': [{'name': 'raw 7'}, {'name': 'raw 8'}]
            },
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        filters = {'tag': 'hello'}
        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 500)
        self.assertEqual(len(response['clean_expenses']), 2)
        self.assertEqual(response['total_count'], 2)
        self.assertTrue('hello' in response['clean_expenses'].pop().get('tags'))
        filter_without_tags = response.get('filter_values', {}).get('without_tag')
        self.assertListEqual(filter_without_tags, ['world'])

        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters, is_clean=False)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 500)
        self.assertEqual(response['total_count'], 2)

        filters = {'without_tag': 'hello'}
        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)
        self.assertFalse('hello' in response['clean_expenses'].pop().get('tags'))
        filter_with_tags = response.get('filter_values', {}).get('tag')
        self.assertListEqual(filter_with_tags, ['world'])

        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters, is_clean=False)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(response['total_count'], 1)

        filters = {'tag': 'hello', 'without_tag': 'world'}
        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)
        response_tags = response['clean_expenses'].pop().get('tags')
        self.assertTrue('hello' in response_tags)
        self.assertFalse('world' in response_tags)
        filter_with_tags = response.get('filter_values', {}).get('tag')
        filter_without_tags = response.get('filter_values', {}).get('without_tag')
        self.assertListEqual(filter_with_tags, [])
        self.assertListEqual(filter_without_tags, [])

        code, response = self.get_expenses_with_available_filters(
            self.org_id, time, time + 1, filters, is_clean=False)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 200)
        self.assertEqual(response['total_count'], 1)

    def test_summary_clean_expenses_filter_by_empty_tag(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], name='res1',
            first_seen=time, last_seen=time + 1, tags={})
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], name='res2',
            first_seen=time, last_seen=time + 1, tags={'world': 'hello'})
        expenses = [
            {
                'cost': 200,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'raw': [{'name': 'raw 2'}]
            },
            {
                'cost': 100,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'raw': [{'name': 'raw 4'}, {'name': 'raw 5'}, {'name': 'raw 6'}]
            },
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        filters = {'tag': get_nil_uuid()}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 200)
        self.assertEqual(response['total_count'], 1)

        filters = {'without_tag': get_nil_uuid()}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(response['total_count'], 1)

        filters = {'tag': get_nil_uuid(), 'without_tag': get_nil_uuid()}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(len(response['clean_expenses']), 0)
        self.assertEqual(response['total_count'], 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

    def test_summary_clean_expenses_invalid_limit(self):
        time = int(datetime.utcnow().timestamp())
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, {'limit': -1})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0224')
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, {'limit': 'ss'})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0217')
        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, {'limit': -1})
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0212')

    def test_summary_clean_expenses_unexpected_filters(self):
        self.end_date = datetime(2020, 4, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())
        filters = {
            'not_a_region': 'us-east',
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts, self.end_ts, filters)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0212')
        code, response = self.client.summary_expenses_get(
            self.org_id, self.start_ts, self.end_ts, filters)
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0212')

    def test_summary_clean_expenses_incorrect_dates(self):
        self.end_date = datetime(2020, 3, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())

        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0446')

        code, response = self.client.summary_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0446')

    def test_summary_clean_expenses_filter_by_regex(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res_4.regex_search_1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='another-rez_for.regex_search_!', first_seen=time, last_seen=time + 1)
        expenses = [
            {
                'cost': 150,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 1'}]
            },
            {
                'cost': 300,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 2'}]
            },
            {
                'cost': 70,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 4'}, {'name': 'raw 5'}, {'name': 'raw 6'}]
            },
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        self._make_resources_active([resource1['id']])

        for filter_val in ['re', 're?', '.regex']:
            filters = {'name_like': filter_val}
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 1, filters)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_cost'], 520)
            self.assertEqual(len(response['clean_expenses']), 2)
            self.assertEqual(response['total_count'], 2)
            code, response = self.client.summary_expenses_get(
                self.org_id, time, time + 1, filters)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_cost'], 520)
            self.assertEqual(response['total_count'], 2)

        for filter_val in ['*', '?', '***', '*?']:
            filters = {'name_like': filter_val}
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 1, filters)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['error_code'], 'OE0496')
            code, response = self.client.summary_expenses_get(
                self.org_id, time, time + 1, filters)
            self.assertEqual(code, 400)
            self.assertEqual(response['error']['error_code'], 'OE0496')

        filters = {'name_like': 'search_!'}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 70)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 70)
        self.assertEqual(response['total_count'], 1)

        filters = {'name_like': 'another_'}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(len(response['clean_expenses']), 0)
        self.assertEqual(response['total_count'], 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        filters = {'name_like': '?res_*re?ex?s*r?h*'}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 450)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 450)
        self.assertEqual(response['total_count'], 1)

        filters = {'cloud_resource_id_like': '-'}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 520)
        self.assertEqual(len(response['clean_expenses']), 2)
        self.assertEqual(response['total_count'], 2)

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 520)
        self.assertEqual(response['total_count'], 2)

    @patch('tools.cloud_adapter.clouds.azure.Azure.get_regions_coordinates')
    @patch('tools.cloud_adapter.clouds.aws.Aws.get_regions_coordinates')
    @patch('rest_api.rest_api_server.controllers.expense.ExpenseController.get_expenses')
    def test_region_expenses(self, p_expenses, p_aws_regions_map, p_azure_regions_map):
        p_expenses.return_value = [
            {
                'cost': 3.3,
                '_id': {
                    'date': self.prev_start,
                    'region': 'region1',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 0.9,
                '_id': {
                    'date': self.prev_start,
                    'region': 'region2',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 3.3,
                '_id': {
                    'date': self.start_date,
                    'region': 'region1',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 0.7,
                '_id': {
                    'date': self.second_date,
                    'region': 'region1',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 1.0,
                '_id': {
                    'date': self.start_date,
                    'region': 'region2',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 2.0,
                '_id': {
                    'date': self.second_date,
                    'region': 'region2',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 0,
                '_id': {
                    'date': self.start_date,
                    'region': 'region3',
                    'cloud_account_id': self.cloud_acc1['id']
                },
            },
            {
                'cost': 0,
                '_id': {
                    'date': self.start_date,
                    'region': None,
                },
            },
        ]
        p_aws_regions_map.return_value = {
            'region1': {'longitude': 1, 'latitude': 1},
            'region2': {'longitude': 2, 'latitude': 2},
            'region3': {'longitude': 3, 'latitude': 3},
            'region4': {'longitude': None, 'latitude': None},
            None: {'longitude': None, 'latitude': None},
        }
        p_azure_regions_map.return_value = {
            'regione_1': {'longitude': 1, 'latitude': 2},
            'regione_2': {'longitude': 2, 'latitude': 3},
            'regione_3': {'longitude': 3, 'latitude': 4},
        }
        code, r = self.client.region_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 200)
        self.assertEqual(r['expenses']['total'], 7.0)
        self.assertEqual(r['expenses']['previous_total'], 4.2)
        self.assertEqual(r['expenses']['previous_range_start'], self.prev_start_ts)
        regions_cnt = 0
        regions = {}
        regions.update(p_aws_regions_map.return_value)
        regions.update(p_azure_regions_map.return_value)
        for region in {v['id']: v for v in r['expenses']['regions']}.values():
            self.assertEqual(region['latitude'], regions[region['id']]['latitude'])
            self.assertEqual(region['longitude'], regions[region['id']]['longitude'])
            regions_cnt += 1
        self.assertEqual(regions_cnt, len(regions))
        p_expenses.assert_called_once_with(
            'cloud_account_id',
            [self.cloud_acc1['id'], self.cloud_acc2['id'], self.cloud_acc3['id']],
            self.prev_start, self.end_date, group_by='region')

    def test_region_expenses_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        self.client.pool_delete(self.sub_pool2['id'])
        self.client.pool_delete(self.sub_pool1['id'])
        self.client.organization_delete(self.org_id)
        code, r = self.client.region_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 404)

    def test_clean_expenses_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        self.client.pool_delete(self.sub_pool2['id'])
        self.client.pool_delete(self.sub_pool1['id'])
        self.client.organization_delete(self.org_id)
        code, response = self.client.clean_expenses_get(
            self.org_id, int(datetime.utcnow().timestamp()) - 1000,
            int(datetime.utcnow().timestamp()), {})
        self.assertEqual(code, 404)

    def test_summary_expenses_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        self.client.pool_delete(self.sub_pool2['id'])
        self.client.pool_delete(self.sub_pool1['id'])
        self.client.organization_delete(self.org_id)
        code, response = self.client.summary_expenses_get(
            self.org_id, int(datetime.utcnow().timestamp()) - 1000,
            int(datetime.utcnow().timestamp()), {})
        self.assertEqual(code, 404)

    def test_raw_expenses_deleted_org(self):
        patch('rest_api.rest_api_server.controllers.employee.'
              'EmployeeController.delete').start()
        self.client.pool_delete(self.sub_pool2['id'])
        self.client.pool_delete(self.sub_pool1['id'])
        self.client.organization_delete(self.org_id)
        code, response = self.client.raw_expenses_get(
            self.org_id, int(datetime.utcnow().timestamp()) - 1000,
            int(datetime.utcnow().timestamp()), {})
        self.assertEqual(code, 404)

    def test_raw_expenses_nonexistent_resource(self):
        code, response = self.client.raw_expenses_get(
            str(uuid.uuid4()), int(datetime.utcnow().timestamp()) - 1000,
            int(datetime.utcnow().timestamp()), {})
        self.assertEqual(code, 404)
        code, response = self.client.raw_expenses_get(
            get_nil_uuid(), int(datetime.utcnow().timestamp()) - 1000,
            int(datetime.utcnow().timestamp()), {})
        self.assertEqual(code, 404)

    def test_region_expenses_no_cloud_accs(self):
        self.client.cloud_account_delete(self.cloud_acc1['id'])
        self.client.cloud_account_delete(self.cloud_acc2['id'])
        self.client.cloud_account_delete(self.cloud_acc3['id'])
        code, r = self.client.region_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 424)
        self.assertEqual(r['error']['error_code'], 'OE0445')

    def test_region_expenses_incorrect_dates(self):
        self.end_date = datetime(2020, 3, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())

        code, r = self.client.region_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(r['error']['error_code'], 'OE0446')

    def test_pool_breakdown_expenses_incorrect_dates(self):
        self.end_date = datetime(2020, 3, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())

        code, r = self.client.pool_breakdown_expenses_get(
            self.org['pool_id'], self.start_ts, self.end_ts)
        self.assertEqual(code, 400)
        self.assertEqual(r['error']['error_code'], 'OE0446')

    def test_employee_expenses_incorrect_dates(self):
        self.end_date = datetime(2020, 3, 2, 23, 59)
        self.end_ts = int(self.end_date.timestamp())
        code, r = self.client.employee_expenses_get(
            self.employee1['id'], self.start_ts, self.end_ts,
            filter_by='pool')
        self.assertEqual(code, 400)
        self.assertEqual(r['error']['error_code'], 'OE0446')

    def test_clean_expenses_no_cloud_accs(self):
        self.client.cloud_account_delete(self.cloud_acc1['id'])
        self.client.cloud_account_delete(self.cloud_acc2['id'])
        self.client.cloud_account_delete(self.cloud_acc3['id'])
        code, r = self.client.clean_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 424)
        self.assertEqual(r['error']['error_code'], 'OE0445')

    def test_summary_expenses_no_cloud_accs(self):
        self.client.cloud_account_delete(self.cloud_acc1['id'])
        self.client.cloud_account_delete(self.cloud_acc2['id'])
        self.client.cloud_account_delete(self.cloud_acc3['id'])
        code, r = self.client.summary_expenses_get(
            self.org_id, self.start_ts, self.end_ts)
        self.assertEqual(code, 424)
        self.assertEqual(r['error']['error_code'], 'OE0445')

    def test_clean_expenses_inclusion(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.sub_pool1['id'],
            name='res2', first_seen=time, last_seen=time + 1)
        expenses = [
            {
                'cost': 150, 'date': day_in_month,
                'ca_id': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'raw': [
                    {'name': 'raw 1'}
                ]
            },
            {
                'cost': 70, 'date': day_in_month,
                'ca_id': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.sub_pool1['id'],
                'raw': [
                    {'name': 'raw 4'},
                    {'name': 'raw 5'},
                    {'name': 'raw 6'}
                ]
            }
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['ca_id'],
                'sign': 1
            })

        filters = {
            'pool_id': [self.pool_id_with_subpools(self.org['pool_id'])],
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 2)
        self.assertEqual(response['total_count'], 2)
        self.assertEqual(response['start_date'], time)
        self.assertEqual(response['end_date'], time + 1)

        filters = {
            'pool_id': [self.pool_id_with_subpools(self.sub_pool1['id'])],
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(response['clean_expenses'][0]['resource_id'], resource2['id'])
        self.assertEqual(response['start_date'], time)
        self.assertEqual(response['end_date'], time + 1)

    def test_summary_clean_expenses_recommendations_and_tags(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc1['id'])
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag1': 'val1'})
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag2': 'val2'})
        self.assertEqual(code, 201)
        code, resource4 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag3': 'val3'})
        self.assertEqual(code, 201)
        tags_map = {
            r['id']: r['tags'] for r in [
                resource, resource2, resource3, resource4
            ]
        }
        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource['id'],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'region': 'us-west',
                'resource_id': resource['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        with freeze_time(datetime.fromtimestamp(int(dt.timestamp()))):
            self.add_recommendations(resource['id'], [
                {'name': 'module2', 'saving': 50},
                {'name': 'module3', 'saving': 15}
            ], checklist=True, last_check=int(dt.timestamp()))
            self.add_recommendations(resource3['id'], [
                {'name': 'module4', 'saving': 100},
                {'name': 'module5', 'saving': 1000}
            ], checklist=False, timestamp=int(dt.timestamp()) - 1000)
            code, response = self.client.clean_expenses_get(
                self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100)
            self.assertEqual(code, 200)
            self.assertEqual(len(response['clean_expenses']), 4)
            saving_map = {
                resource['id']: 65,
                resource2['id']: 0,
                resource3['id']: 0,
                resource4['id']: 0
            }
            for e in response['clean_expenses']:
                self.assertEqual(e['saving'], saving_map[e['resource_id']])
                self.assertEqual(e['tags'], tags_map[e['resource_id']])
            code, response = self.client.summary_expenses_get(
                self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_saving'], 65)

        body = {'recommendations': True}
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        e = response['clean_expenses'][0]
        self.assertEqual(e['resource_id'], resource['id'])
        self.assertEqual(e['saving'], saving_map[resource['id']])
        self.assertEqual(e['tags'], tags_map[e['resource_id']])

        code, response = self.client.summary_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_saving'], 65)

        body = {'recommendations': False}
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 3)
        r_id_map = {
            resource['id']: resource,
            resource2['id']: resource2,
            resource3['id']: resource3,
            resource4['id']: resource4
        }
        for e in response['clean_expenses']:
            resource_id = e['resource_id']
            self.assertEqual(e['resource_id'], r_id_map[resource_id]['id'])
            self.assertEqual(e['saving'], saving_map[resource_id])
            self.assertEqual(e['tags'], tags_map[resource_id])
        code, response = self.client.summary_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_count'], 3)
        self.assertEqual(response['total_saving'], 0)

    def test_clean_expenses_kubernetes_fields(self):
        code, resource = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='ReplicaSet',
            created_by_name='core_dns', host_ip='192.168.0.2',
            instance_address='10.24.0.2', k8s_namespace='kube_system', k8s_node='node_test1',
            pod_ip='10.24.1.3', k8s_service='kube_dns')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='ReplicaSet',
            created_by_name='core_dns', host_ip='192.168.0.1',
            instance_address='10.24.0.2', k8s_namespace='kube_system', k8s_node='node_test1',
            pod_ip='10.24.1.3', k8s_service='monitoring-nginx')
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='ReplicaSet',
            created_by_name='core_dns1', host_ip='192.168.0.3',
            instance_address='10.24.0.2', k8s_namespace='default', k8s_node='node_test',
            pod_ip='10.24.1.3', k8s_service='kube_dns')
        self.assertEqual(code, 201)
        code, resource4 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='ReplicaSet',
            created_by_name='core_dns2', host_ip='192.168.0.1',
            instance_address='10.24.0.2', k8s_namespace='kube_system', k8s_node='node_test2',
            pod_ip='10.24.1.3', k8s_service='monitoring-nginx')
        self.assertEqual(code, 201)
        code, resource5 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='ReplicaSet',
            created_by_name='core_dns1', host_ip='192.168.0.2',
            instance_address='10.24.0.2', k8s_namespace='default', k8s_node='node_test',
            pod_ip='10.24.1.3', k8s_service='monitoring-nginx')
        self.assertEqual(code, 201)
        code, resource6 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='DaemonSet',
            created_by_name='core_dns', host_ip='192.168.0.2',
            instance_address='10.24.0.2', k8s_namespace='kube_system', k8s_node='node_test3',
            pod_ip='10.24.1.3', k8s_service='kube_dns')
        self.assertEqual(code, 201)
        code, resource7 = self.create_cloud_resource(
            self.cloud_acc3['id'], created_by_kind='DaemonSet',
            created_by_name='core_dns2', host_ip='192.168.0.3',
            instance_address='10.24.0.2', k8s_namespace='default', k8s_node='node_test1',
            pod_ip='10.24.1.3', k8s_service='monitoring-nginx')
        self.assertEqual(code, 201)
        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource3['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource4['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource5['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource6['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc3['id'],
                'resource_id': resource7['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 7)
        body = {'created_by_kind': 'DaemonSet'}
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 2)
        r_id_map = {
            resource['id']: resource,
            resource6['id']: resource6,
            resource7['id']: resource7
        }
        for e in response['clean_expenses']:
            resource_id = e['resource_id']
            self.assertEqual(e['resource_id'], r_id_map[resource_id]['id'])
        body = {'created_by_kind': 'ReplicaSet', 'created_by_name': 'core_dns'}
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 2)
        r_id_map = {
            resource['id']: resource,
            resource2['id']: resource2
        }
        for e in response['clean_expenses']:
            resource_id = e['resource_id']
            self.assertEqual(e['resource_id'], r_id_map[resource_id]['id'])
        body = {'created_by_kind': 'ReplicaSet',
                'created_by_name': 'core_dns2',
                'k8s_node': 'node_test2'}
        code, response = self.client.clean_expenses_get(
            self.org_id, self.start_ts - 100, int(dt.timestamp()) + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        r_id_map = {
            resource4['id']: resource4
        }
        for e in response['clean_expenses']:
            resource_id = e['resource_id']
            self.assertEqual(e['resource_id'], r_id_map[resource_id]['id'])

    def test_aws_k8s_cloud_resources_with_k8s_filters(self):
        day_in_month = datetime(2021, 6, 7)
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res2', first_seen=time, last_seen=time + 1)
        _, resource3 = self.create_cloud_resource(
            self.cloud_acc3['id'], k8s_namespace='default',
            k8s_node='node_test', k8s_service='kube-dns',
            first_seen=time, last_seen=time + 1)
        _, resource4 = self.create_cloud_resource(
            self.cloud_acc3['id'], k8s_namespace='kube_system',
            k8s_node='node_test2', k8s_service='monitoring-nginx',
            first_seen=time, last_seen=time + 1)
        filters = {'k8s_namespace': 'kube_system'}
        with freeze_time(datetime.fromtimestamp(time)):
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 100, filters)
            self.assertEqual(code, 200)
            clean_expenses = response['clean_expenses']
            for clean_expense in clean_expenses:
                self.assertTrue(
                    clean_expense['resource_id'] in [resource4['id']])
        filters = {'k8s_node': 'node_test'}
        with freeze_time(datetime.fromtimestamp(time)):
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 100, filters)
            self.assertEqual(code, 200)
            clean_expenses = response['clean_expenses']
            for clean_expense in clean_expenses:
                self.assertTrue(
                    clean_expense['resource_id'] in [resource3['id']])
        filters = {'k8s_service': 'kube-dns'}
        with freeze_time(datetime.fromtimestamp(time)):
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 100, filters)
            self.assertEqual(code, 200)
            clean_expenses = response['clean_expenses']
            for clean_expense in clean_expenses:
                self.assertTrue(
                    clean_expense['resource_id'] in [resource3['id']])

    def test_kubernetes_filter_values(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        k8s_nodes = [
            {'name': 'ubuntu1', 'cloud_type': self.cloud_acc3['type']},
            {'name': 'ubuntu2', 'cloud_type': self.cloud_acc3['type']},
        ]
        k8s_namespaces = [
            {'name': 'kube-system1', 'cloud_type': self.cloud_acc3['type']},
            {'name': 'kube-system2', 'cloud_type': self.cloud_acc3['type']},
        ]
        k8s_services = [
            {'name': 'kube-dns', 'cloud_type': self.cloud_acc3['type']},
            {'name': 'monitoring-nginx', 'cloud_type': self.cloud_acc3['type']},
        ]
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc3['id'], self.employee2['id'], self.org['pool_id'],
            created_by_kind='ReplicaSet', created_by_name='core_dns',
            host_ip='192.168.0.2', instance_address='10.24.0.2',
            k8s_namespace=k8s_namespaces[0]['name'],
            k8s_service=k8s_services[0]['name'], k8s_node=k8s_nodes[0]['name'],
            pod_ip='10.24.1.3', resource_type='K8s Pod', name='1',
            first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc3['id'], self.employee2['id'], self.org['pool_id'],
            created_by_kind='ReplicaSet', created_by_name='core_dns',
            host_ip='192.168.0.1', instance_address='10.24.0.2',
            k8s_namespace=k8s_namespaces[1]['name'],
            k8s_service=k8s_services[1]['name'], k8s_node=k8s_nodes[1]['name'],
            pod_ip='10.24.1.3', resource_type='K8s Pod', name='2',
            first_seen=time, last_seen=time + 1)
        costs = [25, 40]
        self._make_resources_active([resource1['id']])
        for i, resource in enumerate([resource1, resource2]):
            self.expenses.append({
                'cost': costs[i],
                'date': day_in_month,
                'resource_id': resource['id'],
                'cloud_account_id': resource['cloud_account_id'],
                'sign': 1
            })

        with freeze_time(datetime.fromtimestamp(time)):
            self.add_recommendations(resource1['id'], [
                {'name': 'module2', 'saving': 50},
                {'name': 'module3', 'saving': 15}
            ], checklist=True, last_check=time)
            code, response = self.get_expenses_with_available_filters(
                self.org_id, time, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['filter_values']['k8s_node']), 2)
        self.assertEqual(len(response['filter_values']['k8s_namespace']), 2)
        self.assertEqual(len(response['filter_values']['k8s_service']), 2)
        for k8s_node in k8s_nodes:
            self.assertIn(k8s_node, response['filter_values']['k8s_node'])
        for k8s_namespace in k8s_namespaces:
            self.assertIn(k8s_namespace, response['filter_values']['k8s_namespace'])
        for k8s_service in k8s_services:
            self.assertIn(k8s_service, response['filter_values']['k8s_service'])

    def test_clean_expenses_filter_by_constraint_violated(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res2', first_seen=time, last_seen=time + 1)
        expenses = [
            {
                'cost': 300,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 70,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'resource_id': resource2['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        self._make_resources_constraint_violated([resource1['id']])

        filters = {}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        clean_expenses = response['clean_expenses']
        exp_violated_map = {resource1['id']: True, resource2['id']: False}
        for clean_expense in clean_expenses:
            self.assertTrue(
                clean_expense['resource_id'] in [
                    resource1['id'], resource2['id']])
            violated = exp_violated_map[clean_expense['resource_id']]
            self.assertEqual(clean_expense['constraint_violated'], violated)

        filters = {'constraint_violated': True}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        clean_expense = response['clean_expenses'][0]
        self.assertTrue(clean_expense['resource_id'], resource1['id'])
        violated = exp_violated_map[clean_expense['resource_id']]
        self.assertEqual(clean_expense['constraint_violated'], violated)

        filters = {'constraint_violated': False}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        clean_expense = response['clean_expenses'][0]
        self.assertTrue(clean_expense['resource_id'], resource2['id'])
        violated = exp_violated_map[clean_expense['resource_id']]
        self.assertEqual(clean_expense['constraint_violated'], violated)

    def test_summary_clean_expenses_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val2'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource4 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'some': 'tag'}, region='us-test')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'region': resource2['region'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource3['region'],
                'resource_id': resource3['id'],
            },
            {
                'cost': 250, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource4['region'],
                'resource_id': resource4['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        with freeze_time(datetime.fromtimestamp(int(dt.timestamp()))):
            self.add_recommendations(resource1['id'], [
                {'name': 'module2', 'saving': 50},
                {'name': 'module3', 'saving': 15}
            ], checklist=True, last_check=int(dt.timestamp()))
            self.add_recommendations(resource3['id'], [
                {'name': 'module4', 'saving': 100},
                {'name': 'module5', 'saving': 1000}
            ], checklist=False, timestamp=int(dt.timestamp()))

        body = {'resource_type': '%s:cluster' % cluster_type['name']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)
        self.assertTrue(len(response['clean_expenses']) == 2)
        expenses_check_map = {
            resource1['cluster_id']: (250, 1165, [resource1['id'], resource3['id']]),
            resource2['cluster_id']: (300, 0, [resource2['id']])
        }
        for expense in response['clean_expenses']:
            cost, saving, dependent_ids = expenses_check_map.get(
                expense['resource_id'], (None, []))
            self.assertEqual(expense['cost'], cost)
            self.assertEqual(expense['saving'], saving)
            for null_field in ['cloud_console_link', 'cloud_account_id', 'region',
                               'service_name', 'cloud_account_name',
                               'cloud_account_type', 'resource_name']:
                self.assertIsNone(expense.get(null_field))
            self.assertFalse(expense['active'])
            self.assertFalse(expense['constraint_violated'])
            self.assertEqual(expense['cost'], cost)
            self.assertIsNotNone(expense.get('cluster_type_id'))

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)
        self.assertEqual(response['total_saving'], 1165)

        body = {
            'resource_type': '%s:cluster' % cluster_type['name'],
            'recommendations': False
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)
        self.assertTrue(len(response['clean_expenses']) == 2)
        self.assertEqual(response['clean_expenses'][0]['resource_id'],
                         resource2['cluster_id'])

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)
        self.assertEqual(response['total_saving'], 1165)

        body = {'resource_type': '%s:cluster' % cluster_type['name']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time + 100, time + 200, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time + 100, time + 200, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)
        self.assertEqual(response['total_saving'], 0)

        body = {'cloud_account_id': self.cloud_acc1['id']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(len(response.get('clean_expenses', [])), 1)
        for expense in response['clean_expenses']:
            self.assertEqual(expense['resource_id'], resource4['id'])
        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(response['total_saving'], 0)

        self._make_resources_active([resource1['cluster_id']])
        body = {'resource_type': '%s:cluster' % cluster_type['name'],
                'active': True, 'recommendations': False}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(len(response.get('clean_expenses', [])), 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(response['total_saving'], 1165)

        for expense_filter in ['region', 'cloud_account_id']:
            body = {expense_filter: self.nil_uuid}
            code, response = self.client.clean_expenses_get(
                self.org_id, time - 100, time + 100, body)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_cost'], 550, expense_filter)
            self.assertEqual(response['total_count'], 2)

            code, response = self.client.summary_expenses_get(
                self.org_id, time - 100, time + 100, body)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_cost'], 550)
            self.assertEqual(response['total_count'], 2)
            self.assertEqual(response['total_saving'], 1165)

        body = {'service_name': [self.nil_uuid]}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 800)
        self.assertEqual(response['total_count'], 3)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 800)
        self.assertEqual(response['total_count'], 3)
        self.assertEqual(response['total_saving'], 1165)

        body = {'recommendations': True}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(len(response.get('clean_expenses', [])), 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(response['total_saving'], 1165)

        body = {'recommendations': False}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 800)
        self.assertEqual(response['total_count'], 3)
        self.assertEqual(len(response.get('clean_expenses', [])), 3)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 800)
        self.assertEqual(response['total_count'], 3)
        self.assertEqual(response['total_saving'], 1165)

    def test_clean_expenses_shareables(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        self.resources_collection.update_one(
            filter={
                '_id': resource1['id']
            },
            update={'$set': {
                'shareable': True}}
        )
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc2['id'], region='us-east')
        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_account_id': resource1['cloud_account_id'],
                'resource_id': resource1['id'],
                'sign': 1
            },
            {
                'cost': 150, 'date': dt,
                'cloud_account_id': resource2['cloud_account_id'],
                'resource_id': resource2['id'],
                'sign': 1
            }
        ]
        for e in expenses:
            self.expenses.append(e)

        time = int(dt.timestamp())
        body = {'cloud_account_id': resource1['cloud_account_id']}
        code, shareable_cleans = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertTrue(
            shareable_cleans['clean_expenses'][0].get('shareable') is True
        )
        body = {'cloud_account_id': resource2['cloud_account_id']}
        code, not_shareable_cleans = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertTrue(
            not_shareable_cleans['clean_expenses'][0].get('shareable') is False
        )

    def test_summary_clean_expenses_environments(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.client.environment_resource_create(
            self.org_id, {'name': 'res2', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)
        code, resource3 = self.client.environment_resource_create(
            self.org_id, {'name': 'res3', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_account_id': resource1['cloud_account_id'],
                'resource_id': resource1['id'],
                'sign': 1
            },
            {
                'cost': 300, 'date': dt,
                'cloud_account_id': resource2['cloud_account_id'],
                'resource_id': resource2['id'],
                'sign': 1
            },
            {
                'cost': 100, 'date': dt,
                'cloud_account_id': resource3['cloud_account_id'],
                'resource_id': resource3['id'],
                'sign': 1
            }
        ]
        for e in expenses:
            self.expenses.append(e)

        time = int(dt.timestamp())
        body = {'resource_type': '%s:environment' % resource2['resource_type']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)
        for expense in response['clean_expenses']:
            self.assertTrue(expense.get('is_environment', False))

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)

        code, response = self.client.clean_expenses_get(
            self.org_id, time + 100, time + 200, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time + 100, time + 200, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        body = {'cloud_account_id': resource2['cloud_account_id']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)
        self.assertEqual(len(response.get('clean_expenses', [])), 2)
        for expense in response['clean_expenses']:
            self.assertTrue(expense['is_environment'])
            self.assertTrue(expense.get('shareable'))
            self.assertTrue(expense['active'])

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)

        body = {'cloud_account_id': resource2['cloud_account_id'], 'active': False}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)
        self.assertEqual(len(response.get('clean_expenses', [])), 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        body = {'region': self.nil_uuid}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 400)
        self.assertEqual(response['total_count'], 2)

        body = {'service_name': self.nil_uuid}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 3)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 3)

        body = {'service_name': [self.nil_uuid, 'sn']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 3)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 3)

    def test_summary_clean_expenses_deleted_environments(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.client.environment_resource_create(
            self.org_id, {'name': 'res2', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)
        code, resource3 = self.client.environment_resource_create(
            self.org_id, {'name': 'res3', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_account_id': resource1['cloud_account_id'],
                'resource_id': resource1['id'],
                'sign': 1
            },
            {
                'cost': 300, 'date': dt,
                'cloud_account_id': resource2['cloud_account_id'],
                'resource_id': resource2['id'],
                'sign': 1
            },
            {
                'cost': 100, 'date': dt,
                'cloud_account_id': resource3['cloud_account_id'],
                'resource_id': resource3['id'],
                'sign': 1
            }
        ]
        for e in expenses:
            self.expenses.append(e)

        time = int(dt.timestamp())
        code, _ = self.client.environment_resource_delete(resource2['id'])
        self.assertEqual(code, 204)
        body = {'resource_type': '%s:environment' % resource2['resource_type']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(response['total_count'], 1)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 100)
        self.assertEqual(response['total_count'], 1)

        code, _ = self.client.environment_resource_delete(resource3['id'])
        self.assertEqual(code, 204)
        body = {'cloud_account_id': resource2['cloud_account_id']}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)

    def test_summary_clean_expenses_clusters_filter_by_tag(self):
        tag_key = 'tag'
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={tag_key: 'val'}, region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={tag_key: 'val2'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={tag_key: 'val'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource4 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'some': 'tag'}, region='us-test')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'region': resource2['region'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource3['region'],
                'resource_id': resource3['id'],
            },
            {
                'cost': 250, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource4['region'],
                'resource_id': resource4['id'],
            }
        ]

        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        body = {'tag': tag_key}
        code, response = self.client.clean_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)
        self.assertTrue(len(response['clean_expenses']) == 2)
        for e in response['clean_expenses']:
            self.assertIsNotNone(e.get('cluster_type_id'))
            self.assertTrue(tag_key in e.get('tags'))
        code, response = self.client.summary_expenses_get(
            self.org_id, time - 100, time + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 550)
        self.assertEqual(response['total_count'], 2)

    def test_raw_expenses_clusters(self):
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': 'awesome', 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc2['id'], tags={'tag': 'val2'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'tag': 'val'}, region='us-west')
        self.assertEqual(code, 201)
        code, resource4 = self.create_cloud_resource(
            self.cloud_acc1['id'], tags={'some': 'tag'}, region='us-test')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': self.cloud_acc2['id'],
                'region': resource2['region'],
                'resource_id': resource2['id'],
                'raw': [
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': self.cloud_acc2['id'],
                        'resource_id': resource2['cloud_resource_id']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': self.cloud_acc2['id'],
                        'resource_id': resource2['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 100, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource3['region'],
                'resource_id': resource3['id'],
                'raw': [
                    {
                        'name': 'raw 4',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 30,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource3['cloud_resource_id']
                    },
                    {
                        'name': 'raw 5',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 70,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource3['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 250, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource4['region'],
                'resource_id': resource4['id'],
                'raw': [
                    {
                        'name': 'raw 6',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 225,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource4['cloud_resource_id']
                    },
                    {
                        'name': 'raw 7',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 25,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource4['cloud_resource_id']
                    }
                ],
            }
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())

        code, response = self.client.raw_expenses_get(
            resource1['id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertTrue(len(response['raw_expenses']) == 1)
        self.assertEqual(response['total_cost'], 150)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 1'])

        code, response = self.client.raw_expenses_get(
            resource2['cluster_id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 300)
        self.assertTrue(len(response['raw_expenses']) == 2)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 2', 'raw 3'])

        code, response = self.client.raw_expenses_get(
            resource1['cluster_id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 250)
        self.assertTrue(len(response['raw_expenses']) == 3)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 1', 'raw 4', 'raw 5'])

    def test_raw_expenses_environments(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.client.environment_resource_create(
            self.org_id, {'name': 'res2', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': resource2['cloud_account_id'],
                'region': None,
                'resource_id': resource2['id'],
                'raw': [
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': resource2['cloud_account_id'],
                        'resource_id': resource2['cloud_resource_id']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': resource2['cloud_account_id'],
                        'resource_id': resource2['cloud_resource_id']
                    }
                ],
            },
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        time = int(dt.timestamp())
        code, response = self.client.raw_expenses_get(
            resource2['id'], time - 100, time + 100)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 300)
        self.assertTrue(len(response['raw_expenses']) == 2)
        for expense in response['raw_expenses']:
            self.assertIn(expense['name'], ['raw 2', 'raw 3'])

    def test_raw_expenses_deleted_environments(self):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='us-east')
        self.assertEqual(code, 201)
        code, resource2 = self.client.environment_resource_create(
            self.org_id, {'name': 'res2', 'resource_type': 'some_type'})
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': self.cloud_acc1['id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
                'raw': [
                    {
                        'name': 'raw 1',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 150,
                        'cloud_account_id': self.cloud_acc1['id'],
                        'resource_id': resource1['cloud_resource_id']
                    }
                ],
            },
            {
                'cost': 300, 'date': dt,
                'cloud_acc': resource2['cloud_account_id'],
                'region': None,
                'resource_id': resource2['id'],
                'raw': [
                    {
                        'name': 'raw 2',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 100,
                        'cloud_account_id': resource2['cloud_account_id'],
                        'resource_id': resource2['cloud_resource_id']
                    },
                    {
                        'name': 'raw 3',
                        'start_date': dt,
                        'end_date': dt + timedelta(days=1),
                        'cost': 200,
                        'cloud_account_id': resource2['cloud_account_id'],
                        'resource_id': resource2['cloud_resource_id']
                    }
                ],
            },
        ]
        for e in expenses:
            raw_data = e.get('raw')
            self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

        code, _ = self.client.environment_resource_delete(resource2['id'])
        self.assertEqual(code, 204)

        time = int(dt.timestamp())
        code, response = self.client.raw_expenses_get(
            resource2['id'], time - 100, time + 100)
        self.assertEqual(code, 404)

    def test_clean_expenses_invalid_filters(self):
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
            self.org_id, valid_aws_cloud_acc,
            auth_user_id=self.employee1['auth_user_id'])
        self.assertEqual(code, 201)
        ca_params2 = deepcopy(valid_aws_cloud_acc)
        ca_params2['name'] = 'awesome_cloud_acc'
        code, cloud_acc2 = self.create_cloud_account(
            self.org_id, ca_params2,
            auth_user_id=self.employee2['auth_user_id'])
        self.assertEqual(code, 201)
        _, organization2 = self.client.organization_create(
            {'name': "organization2"})
        auth_user_id_3 = self.gen_id()
        _, employee3 = self.client.employee_create(
            organization2['id'], {'name': 'name1', 'auth_user_id': auth_user_id_3})
        _, another_cloud_acc = self.create_cloud_account(
            organization2['id'], valid_aws_cloud_acc, auth_user_id=auth_user_id_3)
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        filters = {
            'cloud_account_id': [cloud_acc1['id'], '123']
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0470')
        self.assertEqual(
            response['error']['params'], ['cloud_account_id', ['123']])
        filters['cloud_account_id'] = [cloud_acc1['id'], cloud_acc2['id']]
        filters['owner_id'] = [
            self.employee1['id'], '789', self.employee2['id'], employee3['id']]
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 404)
        self.assertEqual(response['error']['error_code'], 'OE0470')
        self.assertEqual(
            response['error']['params'], ['owner_id', ['789', employee3['id']]])
        filters['owner_id'].remove('789')
        filters['owner_id'].remove(employee3['id'])
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)
        filters['owner_id'] = [self.nil_uuid]
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        self.assertEqual(code, 200)

    @freeze_time('2021-09-13 15:00:00')
    def test_get_old_active_clean_expenses(self):
        now = datetime.utcnow()
        now_ts = int(now.timestamp())
        today = now.replace(hour=0, minute=0, second=0)
        previuos_month_day = today.replace(month=today.month - 1, day=1)
        previuos_month_day_ts = int(previuos_month_day.timestamp())
        cloud_acc_id = self.cloud_acc1['id']
        employee_id = self.employee1['id']
        pool_id = self.org['pool_id']
        res_type = 'Instance'
        _, resource_1 = self.create_cloud_resource(
            cloud_acc_id, employee_id=employee_id,
            pool_id=pool_id, first_seen=previuos_month_day_ts,
            resource_type=res_type)
        _, resource_2 = self.create_cloud_resource(
            cloud_acc_id, employee_id=employee_id,
            pool_id=pool_id, first_seen=previuos_month_day_ts,
            resource_type=res_type)
        self._make_resources_active([resource_1['id'], resource_2['id']])
        raw_expenses = [
            {
                'name': 'raw 1',
                'start_date': previuos_month_day,
                'end_date': previuos_month_day + timedelta(hours=3),
                'cost': 50
            },
            {
                'name': 'raw 2',
                'start_date': today,
                'end_date': today + timedelta(hours=3),
                'cost': 100
            }
        ]
        old_expenses = [
            {
                'cost': 20, 'date': previuos_month_day,
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_1['id'],
            },
            {
                'cost': 20, 'date': previuos_month_day + timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_1['id'],
            },
            {
                'cost': 10, 'date': previuos_month_day + timedelta(days=2),
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_1['id'],
            }
        ]
        new_expenses = [
            {
                'cost': 40, 'date': today,
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_2['id'],
            },
            {
                'cost': 40, 'date': today - timedelta(days=1),
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_2['id'],
            },
            {
                'cost': 20, 'date': today - timedelta(days=2),
                'cloud_acc': self.cloud_acc1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'resource_id': resource_2['id'],
            }
        ]

        raw = self.raw_expenses.insert_many(raw_expenses)
        raw_ids = raw.inserted_ids
        for e in old_expenses:
            self.expenses.append({
                'resource_id': resource_1['id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        for e in new_expenses:
            self.expenses.append({
                'resource_id': resource_2['id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        start_date = int(today.replace(day=1, hour=0, minute=0,
                                       second=0).timestamp())
        code, response = self.client.clean_expenses_get(self.org['id'],
                                                        start_date,
                                                        now_ts)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 2)
        clean_expenses = response['clean_expenses']
        expected_result = {
            resource_1['id']: {
                'cost': 0,
                'active': True
            },
            resource_2['id']: {
                'cost': 100,
                'active': True
            }
        }
        for clean_expense in clean_expenses:
            res_cost_map = expected_result[clean_expense['resource_id']]
            self.assertEqual(res_cost_map['cost'], clean_expense['cost'])

    def test_clean_expenses_resource_type_identity(self):
        resource_type = 'Instance'
        code, cluster_type = self.client.cluster_type_create(
            self.org_id, {'name': resource_type, 'tag_key': 'tag'})
        self.assertEqual(code, 201)
        code, clustered_resource = self.create_cloud_resource(
            self.cloud_acc1['id'], resource_type=resource_type,
            tags={'tag': 'val'})
        self.assertEqual(code, 201)
        code, non_clustered_resource = self.create_cloud_resource(
            self.cloud_acc1['id'], resource_type=resource_type)
        self.assertEqual(code, 201)
        code, env_resource = self.client.environment_resource_create(
            self.org_id, {'name': 'some_name', 'resource_type': 'Instance'})
        self.assertEqual(code, 201)
        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 10, 'date': dt,
                'cloud_account_id': clustered_resource['cloud_account_id'],
                'resource_id': clustered_resource['id'],
                'sign': 1
            },
            {
                'cost': 20, 'date': dt,
                'cloud_account_id': non_clustered_resource['cloud_account_id'],
                'resource_id': non_clustered_resource['id'],
                'sign': 1
            },
            {
                'cost': 30, 'date': dt,
                'cloud_account_id': env_resource['cloud_account_id'],
                'resource_id': env_resource['id'],
                'sign': 1
            },
        ]
        for e in expenses:
            self.expenses.append(e)
        now = int(dt.timestamp())

        body = {'resource_type': '%s:regular' % resource_type}
        code, expenses = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(expenses['total_cost'], 20)
        self.assertEqual(expenses['total_count'], 1)

        body = {'resource_type': '%s:cluster' % resource_type}
        code, expenses = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(expenses['total_cost'], 10)
        self.assertEqual(expenses['total_count'], 1)

        body = {'resource_type': '%s:environment' % resource_type}
        code, expenses = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 200)
        self.assertEqual(expenses['total_cost'], 30)
        self.assertEqual(expenses['total_count'], 1)

        body = {'resource_type': '%s:unknown' % resource_type}
        code, resp = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0499')

        body = {'resource_type': resource_type}
        code, resp = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0218')

        body = {'type_resource_type': '%s:unknown' % resource_type}
        code, resp = self.client.clean_expenses_get(
            self.org_id, now - 100, now + 100, body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0212')

    def test_traffic_filters(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='name_1', first_seen=time, tags={'tag': 'val'},
            service_name='service_name_1', resource_type='resource_type_1')
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc2['id'], self.employee2['id'], self.org['pool_id'],
            name='name_2', first_seen=time, tags={'tag_2': 'val'},
            service_name='service_name_2', resource_type='resource_type_2')
        _, resource3 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='name_3', first_seen=time, tags={'tag': 'val'},
            service_name='service_name_1', resource_type='resource_type_1')
        expenses = [
            {
                'cost': 150, 'resource_id': resource1['id'],
                'date': day_in_month, 'cloud_acc': self.cloud_acc1['id'],
            },
            {
                'cost': 300, 'resource_id': resource2['id'],
                'date': day_in_month, 'cloud_acc': self.cloud_acc2['id'],
            },
            {
                'cost': 70, 'resource_id': resource3['id'],
                'date': day_in_month, 'cloud_acc': self.cloud_acc1['id'],
            },
        ]

        for e in expenses:
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource1['cloud_resource_id'],
                'date': datetime.fromtimestamp(time),
                'type': 1,
                'from': 'from_1',
                'to': 'to_1',
                'usage': 1,
                'cost': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource1['cloud_resource_id'],
                'date': datetime.fromtimestamp(time),
                'type': 1,
                'from': 'from_2',
                'to': 'to_1',
                'usage': 2,
                'cost': 2,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': resource2['cloud_resource_id'],
                'date': datetime.fromtimestamp(time),
                'type': 1,
                'from': 'from_2',
                'to': 'to_1',
                'usage': 3,
                'cost': 3,
                'sign': 1
            }
        ]

        for body in [
            {
                'traffic_from': ['from_1:aws_cnr', 'from_2:aws_cnr'],
                'traffic_to': 'to_1:aws_cnr'
            },
            {
                'traffic_to': 'to_1:aws_cnr'
            },
            {
                'traffic_from': 'ANY'
            },
        ]:
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 1, body)
            self.assertEqual(code, 200)
            clean_expenses = response['clean_expenses']
            self.assertEqual(len(clean_expenses), 2)
            expected_traf_ex_map = {
                resource1['id']: [
                    {'from': 'from_1', 'to': 'to_1', 'usage': 1, 'cost': 1},
                    {'from': 'from_2', 'to': 'to_1', 'usage': 2, 'cost': 2}
                ],
                resource2['id']: [
                    {'from': 'from_2', 'to': 'to_1', 'usage': 3, 'cost': 3}
                ]
            }
            for e in clean_expenses:
                self.assertEqual(
                    sorted(e['traffic_expenses'], key=lambda x: x['cost']),
                    expected_traf_ex_map[e['id']])

            code, response = self.client.summary_expenses_get(
                self.org_id, time, time + 1, body)
            self.assertEqual(code, 200)
            self.assertEqual(response['total_count'], 2)
            self.assertEqual(response['total_cost'], 450)

        body = {
            'traffic_from': 'from_1:aws_cnr',
            'traffic_to': 'to_1:aws_cnr'
        }
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, body)
        self.assertEqual(code, 200)
        clean_expenses = response['clean_expenses']
        self.assertEqual(len(clean_expenses), 1)
        expected_traf_ex_map = {
            resource1['id']: [
                {'from': 'from_1', 'to': 'to_1', 'usage': 1, 'cost': 1},
            ]
        }
        for e in clean_expenses:
            self.assertEqual(
                sorted(e['traffic_expenses'], key=lambda x: x['cost']),
                expected_traf_ex_map[e['id']])

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_count'], 1)
        self.assertEqual(response['total_cost'], 150)

        body = {'traffic_to': 'to_1:azure_cnr'}
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, body)
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 0)
        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, body)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 0)
        self.assertEqual(response['total_count'], 0)
        code, response = self.client.available_filters_get(
            self.org_id, time, time + 1)
        self.assertEqual(code, 200)
        self.assertFalse('traffic_from' not in response['filter_values'])
        self.assertFalse('traffic_to' not in response['filter_values'])

        code, response = self.client.available_filters_get(
            self.org_id, time, time + 1)
        self.assertEqual(code, 200)
        for k in [
            {'name': 'from_1', 'cloud_type': 'aws_cnr'},
            {'name': 'from_2', 'cloud_type': 'aws_cnr'},
            {'name': 'from_2', 'cloud_type': 'azure_cnr'}
        ]:
            self.assertTrue(k in response['filter_values']['traffic_from'])
        for k in [
            {'name': 'to_1', 'cloud_type': 'azure_cnr'},
            {'name': 'to_1', 'cloud_type': 'aws_cnr'}
        ]:
            self.assertTrue(k in response['filter_values']['traffic_to'])

        code, response = self.client.available_filters_get(
            self.org_id, time, time + 1, {'traffic_from': 'from_1:aws_cnr'})
        self.assertEqual(code, 200)
        self.assertEqual(response['filter_values']['traffic_from'], [])
        self.assertEqual(response['filter_values']['traffic_to'],
                         [{'name': 'to_1', 'cloud_type': 'aws_cnr'}, 'ANY'])
        code, response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, {'_id': resource1['id']})
        self.assertEqual(code, 200)
        self.assertEqual(len(response['clean_expenses']), 1)
        self.assertEqual(response['clean_expenses'][0]['id'], resource1['id'])

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1, {'_id': resource1['id']})
        self.assertEqual(code, 200)
        self.assertEqual(response['total_cost'], 150)
        self.assertEqual(response['total_count'], 1)

    def test_invalid_traffic_filter(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        for body in [
            {
                'traffic_from': 'reg1'
            },
            {
                'traffic_to': ['reg1:aws_cnr', 'reg2']
            }
        ]:
            code, response = self.client.clean_expenses_get(
                self.org_id, time, time + 1, body)
            self.assertEqual(code, 400)
            self.verify_error_code(response, 'OE0218')

    def prepare_some_expenses(self, day_in_month):
        time = int(day_in_month.timestamp())
        _, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res1', first_seen=time, last_seen=time + 1)
        _, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], self.employee1['id'], self.org['pool_id'],
            name='res2', first_seen=time, last_seen=time + 1)
        expenses = [
            {
                'cost': 150,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee1['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 1'}]
            },
            {
                'cost': 300,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-east',
                'resource_id': resource1['id'],
                'owner_id': self.employee2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 2'}]
            },
            {
                'cost': 70,
                'date': day_in_month,
                'cloud_acc': self.cloud_acc1['id'],
                'region': 'us-west',
                'resource_id': resource2['id'],
                'pool_id': self.org['pool_id'],
                'raw': [{'name': 'raw 4'}, {'name': 'raw 5'}, {'name': 'raw 6'}]
            },
            {
                'cost': 150,
                'date': day_in_month,
                'cloud_acc': 'fake cloud acc id',
                'region': 'us-east',
                'resource_id': 'res_3_id',
                'raw': [{'name': 'raw 7'}]
            }
        ]

        for e in expenses:
            raw_data = e.get('raw')
            raw = self.raw_expenses.insert_many(raw_data)
            self.expenses.append({
                'cost': e['cost'],
                'date': e['date'],
                'resource_id': e['resource_id'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })

    def test_fields_filter_positive(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())

        self.prepare_some_expenses(day_in_month)

        filters = {
            'field': ['cloud_resource_id', 'owner.id']
        }
        code, clean_response = self.client.clean_expenses_get(
            self.org_id, time, time + 1, filters)
        clean_expenses = clean_response['clean_expenses']
        for expense in clean_expenses:
            self.assertEqual(set(expense.keys()), {'cloud_resource_id', 'owner'})
            self.assertEqual(set(expense['owner'].keys()), {'id'})

    def test_summary_expenses_with_cluster_secret(self):
        day_in_month = datetime(2020, 1, 14)
        time = int(day_in_month.timestamp())
        self.prepare_some_expenses(day_in_month)

        def side_eff(*args, **kwargs):
            raise OptHTTPError(403, Err.OE0234, [])

        patch(
            'rest_api.rest_api_server.handlers.v1.base.'
            'BaseAuthHandler.check_permissions',
            side_effect=side_eff).start()
        patch('rest_api.rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.check_cluster_secret',
              return_value=True).start()

        code, response = self.client.summary_expenses_get(
            self.org_id, time, time + 1)
        self.assertEqual(code, 200)
        self.assertEqual(response['total_count'], 2)

    @patch('tools.cloud_adapter.clouds.azure.Azure.get_regions_coordinates')
    @patch('tools.cloud_adapter.clouds.aws.Aws.get_regions_coordinates')
    def test_region_expenses_duplicated_regions(
            self, p_aws_regions_map, p_azure_regions_map):
        code, resource1 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='region1')
        self.assertEqual(code, 201)
        code, resource2 = self.create_cloud_resource(
            self.cloud_acc1['id'], region='global')
        self.assertEqual(code, 201)
        code, resource3 = self.create_cloud_resource(
            self.cloud_acc2['id'], region='global')
        self.assertEqual(code, 201)

        dt = datetime.utcnow()
        expenses = [
            {
                'cost': 150, 'date': dt,
                'cloud_acc': resource1['cloud_account_id'],
                'region': resource1['region'],
                'resource_id': resource1['id'],
            },
            {
                'cost': 200, 'date': dt,
                'cloud_acc': resource2['cloud_account_id'],
                'region': resource2['region'],
                'resource_id': resource2['id'],
            },
            {
                'cost': 250, 'date': dt,
                'cloud_acc': resource3['cloud_account_id'],
                'region': resource3['region'],
                'resource_id': resource3['id'],
            }
        ]
        for e in expenses:
            self.expenses.append({
                'resource_id': e['resource_id'],
                'cost': e['cost'],
                'date': e['date'],
                'cloud_account_id': e['cloud_acc'],
                'sign': 1
            })
        p_aws_regions_map.return_value = {
            'region1': {'longitude': 1, 'latitude': 1},
            'global': {'longitude': 3, 'latitude': 3}
        }
        p_azure_regions_map.return_value = {
            'global': {'longitude': 3, 'latitude': 3}
        }
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=1)

        code, resp = self.client.region_expenses_get(
            self.org_id, int(start_date.timestamp()), int(end_date.timestamp()))
        self.assertEqual(code, 200)
        self.assertEqual(resp['expenses']['total'], 600)
        self.assertEqual(len(resp['expenses']['regions']), 3)
        for e in [
            {
                'name': 'region1', 'id': 'region1', 'total': 150,
                'previous_total': 0, 'longitude': 1, 'latitude': 1,
                'type': 'aws_cnr'
            },
            {
                'name': 'global', 'id': 'global', 'total': 200,
                'previous_total': 0, 'longitude': 3, 'latitude': 3,
                'type': 'aws_cnr'
            },
            {
                'name': 'global', 'id': 'global', 'total': 250,
                'previous_total': 0, 'longitude': 3, 'latitude': 3,
                'type': 'azure_cnr'
            }
        ]:
            self.assertTrue(e in resp['expenses']['regions'])
