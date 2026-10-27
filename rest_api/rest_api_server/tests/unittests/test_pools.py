import csv
import io
from datetime import datetime, timezone
import uuid
from sqlalchemy import and_
from unittest.mock import patch, ANY
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import (
    Checklist, OrganizationLimitHit
)
from rest_api.rest_api_server.utils import timestamp_to_day_start

from freezegun import freeze_time

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from tools.optscale_time import utcnow_timestamp


class PoolApiTestBase(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.auth_user_1 = self.gen_id()
        self.org_id = self.org['id']
        _, self.employee_1_1 = self.client.employee_create(
            self.org_id, {'name': 'employee_1_1',
                          'auth_user_id': self.auth_user_1})

        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        self.valid_cloud_acc_dict = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'bucket_name': 'name',
                'config_scheme': 'create_report'
            }
        }

    def _create_resource(self, cloud_account_id, employee_id=None,
                         pool_id=None, name=None, r_type=None):
        code, resource = self.cloud_resource_create(
            cloud_account_id, {
                'cloud_resource_id': self.gen_id(),
                'name': name if name else 'default_name',
                'resource_type': r_type if r_type else 'default_type',
                'employee_id': employee_id,
                'pool_id': pool_id
            })
        self.assertEqual(code, 201)
        return resource

    def add_recommendations(self, resource_id, modules, timestamp=None,
                            last_check=None, pool_id=None, checklist=True):
        if not timestamp:
            timestamp = utcnow_timestamp()

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
        last_seen = utcnow_timestamp()
        self.resources_collection.update_one(
            filter={
                '_id': resource_id
            },
            update={'$set': {
                'recommendations': recommendations,
                'active': True,
                'pool_id': pool_id,
                'last_seen': last_seen,
                '_last_seen_date': timestamp_to_day_start(last_seen)
            }}
        )


class TestPoolApi(PoolApiTestBase):

    def test_get(self):
        code, pool = self.client.pool_get(self.org['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual(pool['purpose'], 'business_unit')
        self.assertEqual(pool['name'], self.org['name'])
        code, _ = self.client.pool_expenses_export_create(self.org['pool_id'])
        self.assertEqual(code, 201)
        code, pool = self.client.pool_get(self.org['pool_id'])
        self.assertEqual(code, 200)
        self.assertIsNotNone(pool['expenses_export_link'])

    def test_create_subpool(self):
        code, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)

        code, pool = self.client.pool_get(pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(pool['name'], 'subpool')
        self.assertEqual(pool['parent_id'], self.org['pool_id'])

    def test_create_subpool_parent_from_another_org(self):
        code, new_org = self.client.organization_create({'name': 'org2'})
        self.assertEqual(code, 201)

        code, pool = self.client.pool_create(
            self.org_id, {'name': '1', 'parent_id': new_org['pool_id']})
        self.assertEqual(code, 400)
        self.verify_error_code(pool, 'OE0005')

    def test_patch(self):
        params = {
            'limit': 100,
        }
        code, ret = self.client.pool_update(self.org['pool_id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], params['limit'])

    def test_create_without_parent(self):
        code, pool = self.client.pool_create(self.org_id, {'name': 'test'})
        self.assertEqual(code, 201)
        self.assertEqual(pool['parent_id'], self.org['pool_id'])

    def test_delete_root_pool(self):
        code, ret = self.client.pool_delete(self.org['pool_id'])
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0447')

    def test_delete_pool(self):
        code, pool = self.client.pool_create(self.org_id, {'name': 'b name'})
        self.assertEqual(code, 201)

        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)

        code, _ = self.client.pool_get(pool['id'])
        self.assertEqual(code, 404)

    def test_delete_pool_with_export(self):
        code, pool = self.client.pool_create(self.org_id, {'name': 'b name'})
        self.assertEqual(code, 201)

        code, resp = self.client.pool_expenses_export_create(
            pool['id'])
        self.assertEqual(code, 201)

        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)

        code, resp = self.client.pool_expenses_export_data_get(
            self.export_id_from_link(resp['expenses_export_link']))
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_post_check_pool_exceed(self):
        code, org = self.client.organization_create({'name': "org"})
        self.assertEqual(code, 201)
        root_pool_id = org['pool_id']
        code, pool = self.client.pool_update(root_pool_id, {'limit': 200})
        self.assertEqual(code, 200)

        code, response = self.client.pool_create(
            org['id'],
            {'name': "child_bu", 'parent_id': root_pool_id, 'limit': 500})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0407')

        code, child_bu = self.client.pool_create(
            org['id'],
            {'name': "child_bu", 'parent_id': root_pool_id, 'limit': 100})
        self.assertEqual(code, 201)

        code, response = self.client.pool_update(
            child_bu['id'], {'limit': 500})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0407')

        code, response = self.client.pool_update(root_pool_id, {'limit': 10})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0414')

        code, response = self.client.pool_update(root_pool_id, {'limit': '100'})
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0223')

    def test_pool_details(self):
        code, pool = self.client.pool_get(self.org['pool_id'])
        self.assertEqual(code, 200)
        self.assertIsNone(pool.get('policies'))
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True)
        self.assertEqual(code, 200)
        self.assertIsNotNone(pool['policies'])
        self.assertEqual(len(pool['policies']), 0)
        self.client.pool_policy_create(
            self.org['pool_id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True)
        self.assertEqual(code, 200)
        self.assertIsNotNone(pool['policies'])
        self.assertEqual(len(pool['policies']), 1)
        code, sub_pool = self.client.pool_create(self.org_id, {
            'name': "sub", "parent_id": self.org['pool_id']})
        self.assertEqual(code, 201)

        self.client.pool_policy_create(
            sub_pool['id'], {
                'limit': 150,
                'type': 'ttl'
            }
        )

        code, sub_pool2 = self.client.pool_create(self.org_id, {
            'parent_id': sub_pool['id'], 'name': 'sub2'
        })
        self.client.pool_policy_create(
            sub_pool2['id'], {
                'limit': 100,
                'type': 'ttl'
            }
        )

        code, _ = self.client.pool_expenses_export_create(self.org['pool_id'])
        self.assertEqual(code, 201)
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True, children=True)
        self.assertEqual(code, 200)
        self.assertIsNotNone(pool['policies'])
        self.assertEqual(len(pool['policies']), 1)
        pool_children = pool['children']
        self.assertEqual(len(pool_children), 2)
        self.assertIsNotNone(pool_children[0]['policies'])
        self.assertEqual(len(pool_children[0]['policies']), 1)
        sub_pool_policy = pool_children[0]['policies'][0]
        self.assertIsNotNone(sub_pool_policy)
        self.assertEqual(sub_pool_policy['limit'], 150)
        self.assertIsNotNone(pool_children[1]['policies'])
        self.assertEqual(len(pool_children[1]['policies']), 1)
        sub_sub_pool_policy = pool_children[1]['policies'][0]
        self.assertIsNotNone(sub_sub_pool_policy)
        self.assertEqual(sub_sub_pool_policy['limit'], 100)
        self.assertIsNotNone(pool['expenses_export_link'])

    def test_update_pool_purpose(self):
        code, pool = self.client.pool_create(
            self.org_id, {'name': 'name'})
        self.assertEqual(code, 201)
        self.assertEqual(pool['purpose'], 'budget')
        code, response = self.client.pool_update(
            pool['id'], {'purpose': 'team'})
        self.assertEqual(code, 200)
        self.assertEqual(response['purpose'], 'team')

        code, response = self.client.pool_update(
            pool['id'], {'name': 'another name'})
        self.assertEqual(code, 200)
        self.assertEqual(response['name'], 'another name')

        code, response = self.client.pool_update(
            self.org['pool_id'], {'purpose': 'not_existing'})
        self.assertEqual(code, 400)

    def test_create_pool_invalid_values(self):
        # name not set
        code, ret = self.client.pool_create(self.org_id, {})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0216')

        # name filled with whitespaces
        code, ret = self.client.pool_create(self.org_id, {
            'name': '  '
        })
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0416')

        # name is not a string
        code, ret = self.client.pool_create(self.org_id, {'name': 123})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0214')

        # invalid parent_id
        code, ret = self.client.pool_create(self.org_id, {'name': '1',
                                                          'parent_id': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0214')
        code, ret = self.client.pool_create(self.org_id, {
            'name': '1', 'parent_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0005')

        # invalid purpose
        code, ret = self.client.pool_create(self.org_id, {'name': '1',
                                                          'purpose': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0287')

        # invalid default owner
        code, ret = self.client.pool_create(self.org_id, {'name': '1',
                                                          'default_owner_id': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0005')

        # invalid limit value
        code, ret = self.client.pool_create(self.org_id, {'limit': '1'})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0223')
        code, ret = self.client.pool_create(self.org_id, {'limit': -1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0224')

    def test_update_pool_invalid_values(self):
        code, pool = self.client.pool_create(self.org_id, {'name': '1'})
        self.assertEqual(code, 201)

        # name is None
        code, ret = self.client.pool_update(pool['id'], {'name': None})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0216')

        # name filled with whitespaces
        code, ret = self.client.pool_update(pool['id'], {
            'name': '  '
        })
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0416')

        # name is not a string
        code, ret = self.client.pool_update(pool['id'], {'name': 123})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0214')

        # invalid parent_id
        code, ret = self.client.pool_update(pool['id'],
                                            {'name': '1', 'parent_id': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0211')

        # invalid purpose
        code, ret = self.client.pool_update(pool['id'], {'purpose': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0287')

        # invalid default owner
        code, ret = self.client.pool_update(pool['id'],
                                            {'default_owner_id': 1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0005')

        # invalid limit value
        code, ret = self.client.pool_update(pool['id'], {'limit': '1'})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0223')
        code, ret = self.client.pool_update(pool['id'], {'limit': -1})
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0224')

    def test_pool_same_name_same_parent(self):
        name = 'my-best-bud'
        code, pool1 = self.client.pool_create(self.org_id, {'name': name})
        self.assertEqual(code, 201)

        code, pool2 = self.client.pool_create(self.org_id, {'name': name})
        self.assertEqual(code, 409)
        self.verify_error_code(pool2, 'OE0149')

    def test_pool_same_name_different_parent(self):
        name = 'my-best-bud'
        code, pool1 = self.client.pool_create(self.org_id, {'name': name})
        self.assertEqual(code, 201)

        code, pool2 = self.client.pool_create(
            self.org_id, {'name': name, 'parent_id': pool1['id']})
        self.assertEqual(code, 201)
        self.assertEqual(pool1['name'], pool2['name'])

    @patch('rest_api.rest_api_server.controllers.pool.'
           'PoolController.get_user_id')
    @patch('rest_api.rest_api_server.controllers.pool.'
           'PoolController._get_assignments_actions_by_token')
    def test_pool_auto_extension_with_no_limit(
            self, _p_actions_by_token, _p_user_id):
        code, resp = self.client.pool_create(self.org_id, {
            'name': 'pool_1',
            'parent_id': self.org['pool_id'],
            'auto_extension': True
        })
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

    def test_delete_pool_with_children(self):
        _, parent_pool = self.client.pool_create(self.org_id, {
            'name': 'parent'
        })
        _, child_pool = self.client.pool_create(self.org_id, {
            'name': 'child',
            'parent_id': parent_pool['id']
        })

        code, response = self.client.pool_delete(parent_pool['id'])
        self.assertEqual(code, 424)
        self.assertEqual(response['error']['error_code'], 'OE0411')
        code, response = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)
        code, response = self.client.pool_delete(parent_pool['id'])
        self.assertEqual(code, 204)

    @patch('rest_api.rest_api_server.controllers.pool.PoolController.'
           '_authorize_action_for_user')
    def test_edit_default_owner(self, p_auth):
        p_auth.return_value = True
        code, organization = self.client.organization_create({
            'name': 'name'
        })
        self.assertEqual(code, 201)
        org_pool_id = organization['pool_id']
        valid_employee = {
            'name': 'TestUser_%s' % self.gen_id()[:8],
            'auth_user_id': self.gen_id(),

        }
        code, employee = self.client.employee_create(organization['id'],
                                                     valid_employee)
        self.assertEqual(code, 201)
        code, response = self.client.pool_update(org_pool_id, {
            'default_owner_id': employee['id']
        })
        self.assertEqual(code, 200)
        self.assertEqual(response['default_owner_id'], employee['id'])
        self.assertEqual(response['default_owner_name'], employee['name'])
        code, response = self.client.pool_update(org_pool_id, {
            'default_owner_id': self.gen_id()
        })
        self.assertEqual(code, 400)
        self.verify_error_code(response, 'OE0005')
        p_auth.return_value = False
        code, response = self.client.pool_update(org_pool_id, {
            'default_owner_id': employee['id']
        })
        self.assertEqual(code, 403)
        self.verify_error_code(response, 'OE0379')

    def test_change_parent(self):
        code, parent1 = self.client.pool_create(self.org_id, {
            'name': 'parent1',
        })
        self.assertEqual(code, 201)

        code, parent2 = self.client.pool_create(self.org_id, {
            'name': 'parent2',
        })
        self.assertEqual(code, 201)

        code, child = self.client.pool_create(self.org_id, {
            'name': 'child',
            'parent_id': parent1['id']
        })
        self.assertEqual(code, 201)

        code, response = self.client.pool_update(child['id'], {
            'parent_id': parent2['id']
        })
        self.assertEqual(code, 400)
        self.assertEqual(response['error']['error_code'], 'OE0211')

    def test_unallocated(self):
        code, root = self.client.pool_update(self.org['pool_id'], {
            'limit': 1000,
        })
        self.assertEqual(code, 200)

        code, child1 = self.client.pool_create(self.org_id, {
            'name': "child_test1",
            'parent_id': root['id'],
            'limit': 200,
        })
        self.assertEqual(code, 201)

        code, child2 = self.client.pool_create(self.org_id, {
            'name': "child_test2",
            'parent_id': root['id'],
            'limit': 300,
        })
        self.assertEqual(code, 201)

        code, child3 = self.client.pool_create(self.org_id, {
            'name': "child_test3",
            'parent_id': root['id'],
            'limit': 400,
        })
        self.assertEqual(code, 201)

        code, child1_child = self.client.pool_create(self.org_id, {
            'name': "child_test4",
            'parent_id': child1['id'],
            'limit': 100,
        })
        self.assertEqual(code, 201)

        code, organization_root_get = self.client.pool_get(root['id'])
        self.assertEqual(code, 200)
        self.assertEqual(organization_root_get['limit'], 1000)
        self.assertEqual(organization_root_get['unallocated_limit'], 100)

        code, _ = self.client.pool_delete(child3['id'])
        self.assertEqual(code, 204)

        code, organization_root_get = self.client.pool_get(root['id'])
        self.assertEqual(code, 200)
        self.assertEqual(organization_root_get['limit'], 1000)
        self.assertEqual(organization_root_get['unallocated_limit'], 500)

    def test_get_organization_children(self):
        _, org = self.client.organization_create({'name': 'org name'})
        auth_user_1 = self.gen_id()
        _, employee = self.client.employee_create(
            org['id'], {'name': 'employee',
                        'auth_user_id': auth_user_1})
        _, org_pool = self.client.pool_update(org['pool_id'],
                                              {'limit': 600})

        code, pool1 = self.client.pool_create(
            org['id'], {'name': 'b1', 'parent_id': org_pool['id'],
                        'limit': 400})
        self.assertEqual(code, 201)
        code, pool2 = self.client.pool_create(
            org['id'], {'name': 'b2', 'parent_id': org_pool['id'],
                        'limit': 200})
        self.assertEqual(code, 201)
        code, pool1_1 = self.client.pool_create(
            org['id'], {'name': 'b1_1', 'parent_id': pool1['id'],
                        'limit': 200})
        self.assertEqual(code, 201)
        code, pool1_1_1 = self.client.pool_create(
            org['id'], {'name': 'b1_1_1', 'parent_id': pool1_1['id']})
        self.assertEqual(code, 201)
        code, cloud_acc = self.create_cloud_account(
            org['id'], {
                'name': 'my cloud_acc',
                'type': 'aws_cnr',
                'config': {
                    'access_key_id': 'key',
                    'secret_access_key': 'secret',
                }
            }, auth_user_id=auth_user_1)
        code, response = self.client.rules_list(org['id'])
        created_cloud_rule = response['rules'][0]
        _, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.set_allowed_pair(auth_user_1, created_cloud_pool['id'])

        cost_map = {
            org_pool['id']: 200,
            pool1['id']: 20,
            pool1_1['id']: 30,
        }
        day_in_month = datetime(2020, 1, 10)

        for pool_id, cost in cost_map.items():
            resource = {
                '_id': str(uuid.uuid4()),
                'cloud_account_id': cloud_acc['id'],
                'cloud_resource_id': str(uuid.uuid4()),
                'pool_id': pool_id,
                'employee_id': self.employee_1_1['id'],
                'name': 'name',
                'resource_type': 'Instance',
                'first_seen': int(day_in_month.timestamp()),
                'last_seen': int(day_in_month.timestamp()),
                '_first_seen_date': day_in_month,
                '_last_seen_date': day_in_month,
                'deleted_at': 0
            }
            self.resources_collection.insert_one(resource)
            self.expenses.append({
                'resource_id': resource['_id'],
                'cost': cost,
                'date': day_in_month,
                'cloud_account_id': cloud_acc['id'],
                'sign': 1,
            })
        children_map = {
            created_cloud_pool['id']: org_pool['id'],
            pool1['id']: org_pool['id'],
            pool2['id']: org_pool['id'],
            pool1_1['id']: pool1['id'],
            pool1_1_1['id']: pool1_1['id'],
        }
        with freeze_time(datetime(2020, 1, 20)):
            code, org_pool = self.client.pool_get(
                org_pool['id'], details=True, children=True)
            self.assertEqual(code, 200)
            self.assertIsNotNone(org_pool['limit'])
            self.assertIsNotNone(org_pool['unallocated_limit'])
            self.assertEqual(org_pool['cost'], 250)  # 200 + 20 + 30
            self.assertEqual(org_pool['forecast'], 550)  # 250+(250/10)*12
            self.assertEqual(len(org_pool['children']), 5)
            for child in org_pool['children']:
                self.assertIsNotNone(child['limit'])
                self.assertEqual(children_map[child['id']],
                                 child['parent_id'])
                if child['id'] == pool1['id']:
                    self.assertEqual(child['cost'], 50)  # 20 + 30
                    self.assertEqual(child['forecast'], 110)
                elif child['id'] == pool1_1['id']:
                    self.assertEqual(child['cost'], 30)  # 30
                    self.assertEqual(child['forecast'], 66)
                else:
                    self.assertEqual(child['cost'], 0)
                    self.assertEqual(child['forecast'], 0)
        children_map = {
            org_pool['id']: [created_cloud_pool['id'], pool1['id'], pool2['id'],
                             pool1_1['id'], pool1_1_1['id']],
            created_cloud_pool['id']: [],
            pool1['id']: [pool1_1['id'], pool1_1_1['id']],
            pool2['id']: [],
            pool1_1['id']: [pool1_1_1['id']],
            pool1_1_1['id']: []
        }

        for pool_id, children in children_map.items():
            code, pool = self.client.pool_get(
                pool_id, children=True)
            self.assertEqual(len(pool['children']), len(children))

    def test_get_deleted_resource(self):
        _, org = self.client.organization_create({'name': 'org name'})
        auth_user_1 = self.gen_id()
        _, employee = self.client.employee_create(
            org['id'], {'name': 'employee',
                        'auth_user_id': auth_user_1})
        _, org_pool = self.client.pool_update(org['pool_id'],
                                              {'limit': 600})

        code, cloud_acc = self.create_cloud_account(
            org['id'], {
                'name': 'my cloud_acc',
                'type': 'aws_cnr',
                'config': {
                    'access_key_id': 'key',
                    'secret_access_key': 'secret',
                }
            }, auth_user_id=auth_user_1)
        code, response = self.client.rules_list(org['id'])
        created_cloud_rule = response['rules'][0]
        _, created_cloud_pool = self.client.pool_get(
            created_cloud_rule['pool_id'])
        self.set_allowed_pair(auth_user_1, created_cloud_pool['id'])
        day_in_month = datetime(2020, 1, 10)
        resource = {
            '_id': str(uuid.uuid4()),
            'cloud_account_id': cloud_acc['id'],
            'cloud_resource_id': str(uuid.uuid4()),
            'pool_id': org_pool['id'],
            'employee_id': self.employee_1_1['id'],
            'name': 'name',
            'resource_type': 'Instance',
            'first_seen': int(day_in_month.timestamp()),
            'last_seen': int(day_in_month.timestamp()),
            '_first_seen_date': day_in_month,
            '_last_seen_date': day_in_month,
            'deleted_at': 1
        }
        self.resources_collection.insert_one(resource)
        self.expenses.append({
            'resource_id': resource['_id'],
            'cost': 11,
            'date': day_in_month,
            'cloud_account_id': cloud_acc['id'],
            'sign': 1,
        })
        code, pool = self.client.pool_get(org_pool['id'], children=True)
        self.assertEqual(pool.get('cost', 0), 0)

    def test_get_with_details_and_removed_children(self):
        get_expenses = patch(
            'rest_api.rest_api_server.controllers.pool.PoolController.'
            'get_pool_expenses', return_value={}).start()
        code, org = self.client.organization_create({'name': 'org name'})
        _, org_pool = self.client.pool_update(org['pool_id'],
                                              {'limit': 600})
        code, child1 = self.client.pool_create(org['id'], {
            'name': 'ch1', 'parent_id': org_pool['id'], 'limit': 200})
        self.assertEqual(code, 201)
        code, child_of_child1 = self.client.pool_create(org['id'], {
            'name': 'ch-o-ch1', 'parent_id': child1['id'], 'limit': 100})
        self.assertEqual(code, 201)

        code, child2 = self.client.pool_create(org['id'], {
            'name': 'ch2', 'parent_id': org_pool['id'], 'limit': 200})
        self.assertEqual(code, 201)
        code, child_of_child2 = self.client.pool_create(org['id'], {
            'name': 'ch-o-ch2', 'parent_id': child2['id'], 'limit': 100})
        self.assertEqual(code, 201)

        code, _ = self.client.pool_delete(child_of_child2['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.pool_delete(child2['id'])
        self.assertEqual(code, 204)
        code, _ = self.client.pool_get(child2['id'])
        self.assertEqual(code, 404)

        code, pool_info = self.client.pool_get(org_pool['id'], details=True,
                                               children=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(pool_info['children']), 2)
        self.assertTrue(get_expenses.called)

    def test_change_root_pool_purpose(self):
        code, pool = self.client.pool_update(
            self.org['pool_id'], {'purpose': 'budget'})
        self.assertEqual(code, 400)
        self.verify_error_code(pool, 'OE0449')

    def test_change_root_pool_name(self):
        code, pool = self.client.pool_update(
            self.org['pool_id'], {'name': 'another name'})
        self.assertEqual(code, 400)
        self.verify_error_code(pool, 'OE0449')

    def test_pool_details_recommendations(self):
        cloud = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        _, cloud_account = self.create_cloud_account(
            self.org_id, cloud, auth_user_id=self.auth_user_1)
        code, resource = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id',
                'resource_type': 'test',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ], pool_id=self.org['pool_id'])

        code, resource2 = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_2',
                'resource_type': 'test_2',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(resource2['id'], [
            {'name': 'module1', 'saving': 30},
            {'name': 'module2', 'saving': 20},
        ], pool_id=self.org['pool_id'], checklist=False)

        code, resource3 = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_3',
                'resource_type': 'test_3',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(resource3['id'], [
            {'name': 'module2', 'saving': 1000},
        ], checklist=False)
        _, res3 = self.client.cloud_resource_get(resource3['id'])
        self.assertEqual(res3['recommendations']['modules'][0]['saving'], 1000)
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True)
        self.assertEqual(pool['total_recommendations'], 4)
        self.assertEqual(pool['saving'], 80)

        self.resources_collection.update_many(
            filter={
                '_id': {'$in': [resource['id'], resource2['id']]}
            },
            update={'$set': {
                'pool_id': None
            }}
        )
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True)
        self.assertEqual(pool['total_recommendations'], 0)
        self.assertEqual(pool['saving'], 0)

    def test_pool_details_recommendations_subpools(self):
        cloud = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        checklist_timestamp = utcnow_timestamp()
        _, cloud_account = self.create_cloud_account(
            self.org_id, cloud, auth_user_id=self.auth_user_1)
        code, resource = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id',
                'resource_type': 'test',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(resource['id'], [
            {'name': 'module1', 'saving': 10},
            {'name': 'module2', 'saving': 20},
        ], pool_id=self.org['pool_id'], timestamp=checklist_timestamp)

        code, pool1 = self.client.pool_create(self.org_id, {
            'name': 'subpool1', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)
        code, pool2 = self.client.pool_create(self.org_id, {
            'name': 'subpool2', 'parent_id': pool1['id'],
        })
        self.assertEqual(code, 201)

        code, resource1 = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_1',
                'resource_type': 'test1',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(
            resource1['id'], [{'name': 'module1', 'saving': 30}],
            pool_id=pool1['id'], checklist=False,
            timestamp=checklist_timestamp)

        code, resource2 = self.cloud_resource_create(
            cloud_account['id'], {
                'cloud_resource_id': 'res_id_2',
                'resource_type': 'test2',
            })
        self.assertEqual(code, 201)
        self.add_recommendations(
            resource2['id'], [{'name': 'module1', 'saving': 40}],
            pool_id=pool2['id'], checklist=False,
            timestamp=checklist_timestamp)

        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True)
        self.assertEqual(pool['total_recommendations'], 4)
        self.assertEqual(pool['saving'], 100)

        code, pool = self.client.pool_get(
            pool1['id'], details=True)
        self.assertEqual(pool['total_recommendations'], 2)
        self.assertEqual(pool['saving'], 70)

        code, pool = self.client.pool_get(
            pool2['id'], details=True)
        self.assertEqual(pool['total_recommendations'], 1)
        self.assertEqual(pool['saving'], 40)

    def test_duplicate_path_param(self):
        body = {
            'name': 'budg',
            'parent_id': self.org['pool_id'],
            'organization_id': str(uuid.uuid4())
        }
        code, resp = self.client.post(
            'organizations/%s/pools' % self.org_id, body)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0456')

    def test_delete_parent_without_default_owner(self):
        code, _ = self.client.pool_update(
            self.org['pool_id'], {'default_owner_id': None})
        self.assertEqual(code, 200)
        code, employee = self.client.employee_create(
            self.org_id,
            {'name': 'default employee', 'auth_user_id': self.gen_id()}
        )
        self.assertEqual(code, 201)
        code, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.assertEqual(code, 201)
        code, child_pool = self.client.pool_create(self.org_id, {
            'name': 'ch1', 'parent_id': self.org['pool_id']})
        self.assertEqual(code, 201)
        self._create_resource(
            cloud_account['id'], employee['id'], child_pool['id'])
        code, resp = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 424)
        self.verify_error_code(resp, 'OE0459')

    def test_delete_pool_reassign_cleanup(self):
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        user1_id = self.gen_id()
        user2_id = self.gen_id()
        code, employee1 = self.client.employee_create(
            self.org_id, {'name': 'employee1', 'auth_user_id': user1_id})
        patch('rest_api.rest_api_server.controllers.pool.PoolController.'
              '_authorize_action_for_user').start()
        r = self.client.pool_update(
            self.org['pool_id'], {'default_owner_id': employee1['id']})
        code, employee2 = self.client.employee_create(
            self.org_id, {'name': 'employee2', 'auth_user_id': user2_id})
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        code, child_pool = self.client.pool_create(self.org_id, {
            'name': 'ch1', 'parent_id': self.org['pool_id']})
        self.assertEqual(code, 201)
        resource = self._create_resource(
            cloud_account['id'], employee2['id'], child_pool['id'])
        self._mock_auth_user(user2_id)
        patch('rest_api.rest_api_server.controllers.assignment.'
              'AssignmentController._authorize_action_for_pool',
              return_value=True).start()
        code, request = self.client.assignment_request_create(self.org_id, {
            'resource_id': resource['id'],
            'approver_id': employee1['id'],
        })
        self.assertEqual(code, 201)
        _, ar = self.client.assignment_request_list(self.org_id)
        self.assertEqual(len(ar['assignment_requests']['outgoing']), 1)
        self.assertEqual(
            ar['assignment_requests']['outgoing'][0]['source_pool_id'],
            child_pool['id'])
        code, alert = self.client.alert_create(self.org_id, {
            'pool_id': child_pool['id'],
            'contacts': [{'employee_id': employee1['id']}],
            'threshold': 100
        })
        self.assertEqual(code, 201)

        user_assignments = [{
            'assignment_id': self.gen_id(),
            'assignment_resource': self.org_id,
            'assignment_resource_type': 2,
            'role_id': 3,
            'role_name': 'Manager',
            'role_scope': None}]
        patch(
            'rest_api.rest_api_server.controllers.invite.'
            'InviteController.get_invite_expiration_days',
            return_value=30).start()
        patch(
            'rest_api.rest_api_server.controllers.invite.'
            'InviteController.check_user_exists',
            return_value=(True, {})).start()
        patch(
            'rest_api.rest_api_server.controllers.invite.'
            'InviteController.get_user_auth_assignments',
            return_value=user_assignments).start()
        patch(
            'rest_api.rest_api_server.handlers.v1.base.'
            'BaseAuthHandler._get_user_info',
            return_value={
                'display_name': 'default',
                'email': 'email@email.com'
            }).start()
        patch('rest_api.rest_api_server.controllers.invite.'
              'InviteController.check_user_exists',
              return_value=(False, {})).start()
        code, invites = self.client.invite_create({
            'invites': {
                'some@email.com': [
                    {'scope_id': child_pool['id'], 'scope_type': 'pool',
                     'purpose': 'optscale_engineer'}
                ]
            }
        })
        self.assertEqual(code, 201)

        code, _ = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)

        code, _ = self.client.alert_get(alert['id'])
        self.assertEqual(code, 404)
        _, ar = self.client.assignment_request_list(self.org_id)
        self.assertEqual(len(ar['assignment_requests']['outgoing']), 0)
        patch(
            'rest_api.rest_api_server.handlers.v1.base.'
            'BaseAuthHandler._get_user_info',
            return_value={
                'display_name': 'default',
                'email': 'some@email.com'
            }).start()
        c, r = self.client.invite_get(invites['invites'][0]['id'])
        self.assertEqual(len(r['invite_assignments']), 1)
        self.assertEqual(r['invite_assignments'][0]['scope_id'], self.org_id)

    def test_delete_pool_reassign_resources(self):
        user1_id = self.gen_id()
        user2_id = self.gen_id()
        user3_id = self.gen_id()
        code, employee1 = self.client.employee_create(
            self.org_id, {'name': 'employee1', 'auth_user_id': user1_id})
        patch('rest_api.rest_api_server.controllers.pool.PoolController.'
              '_authorize_action_for_user').start()
        self.client.pool_update(
            self.org['pool_id'], {'default_owner_id': employee1['id']})
        _, employee2 = self.client.employee_create(
            self.org_id, {'name': 'employee2', 'auth_user_id': user2_id})
        _, employee3 = self.client.employee_create(
            self.org_id, {'name': 'employee3', 'auth_user_id': user3_id})
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        code, child_pool = self.client.pool_create(self.org_id, {
            'name': 'ch1', 'parent_id': self.org['pool_id']})
        self.assertEqual(code, 201)

        self.set_allowed_pair(user3_id, self.org['pool_id'])

        resource = self._create_resource(
            cloud_account['id'], employee2['id'], child_pool['id'])
        resource2 = self._create_resource(
            cloud_account['id'], employee3['id'], child_pool['id'])
        self.assertEqual(resource['employee_id'], employee2['id'])
        self.assertEqual(resource['pool_id'], child_pool['id'])
        code, _ = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)
        code, resource = self.client.cloud_resource_get(resource['id'])
        self.assertEqual(code, 200)
        # changed pool, reassigned to employee1
        self.assertEqual(resource['employee_id'], employee1['id'])
        self.assertEqual(resource['pool_id'], self.org['pool_id'])

        code, resource = self.client.cloud_resource_get(resource2['id'])
        self.assertEqual(code, 200)
        # changed pool, not reassigned to another owner
        self.assertEqual(resource['employee_id'], employee3['id'])
        self.assertEqual(resource['pool_id'], self.org['pool_id'])

    def test_delete_pool_redirect_rules(self):
        user1_id = self.gen_id()
        user2_id = self.gen_id()
        user3_id = self.gen_id()
        code, employee1 = self.client.employee_create(
            self.org_id, {'name': 'employee1', 'auth_user_id': user1_id})
        patch('rest_api.rest_api_server.controllers.pool.PoolController.'
              '_authorize_action_for_user').start()
        self.client.pool_update(
            self.org['pool_id'], {'default_owner_id': employee1['id']})
        _, employee2 = self.client.employee_create(
            self.org_id, {'name': 'employee2', 'auth_user_id': user2_id})
        _, employee3 = self.client.employee_create(
            self.org_id, {'name': 'employee3', 'auth_user_id': user3_id})
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        code, child_pool = self.client.pool_create(self.org_id, {
            'name': 'ch1', 'parent_id': self.org['pool_id']})
        self.assertEqual(code, 201)

        self._mock_auth_user(user1_id)
        patch('rest_api.rest_api_server.controllers.assignment.AssignmentController'
              '._authorize_action_for_pool', return_value=True).start()
        code, rule1 = self.client.rules_create(self.org_id, {
            'name': 'rule_%s' % employee2['name'],
            'pool_id': child_pool['id'],
            'owner_id': employee2['id'],
            'conditions': [
                {"type": "name_starts_with", "meta_info": employee2['name']}]
        })
        self.assertEqual(code, 201)
        code, rule2 = self.client.rules_create(self.org_id, {
            'name': 'rule_%s' % employee3['name'],
            'pool_id': child_pool['id'],
            'owner_id': employee3['id'],
            'conditions': [
                {"type": "name_starts_with", "meta_info": employee3['name']}]
        })
        self.assertEqual(code, 201)
        self.set_allowed_pair(user3_id, self.org['pool_id'])

        code, _ = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)

        code, resp = self.client.rule_get(rule1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['owner_id'], employee1['id'])
        self.assertEqual(resp['pool_id'], self.org['pool_id'])

        code, resp = self.client.rule_get(rule2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['owner_id'], employee3['id'])
        self.assertEqual(resp['pool_id'], self.org['pool_id'])

    def test_delete_pool_reassign_event(self):
        user1_id = self.gen_id()
        user2_id = self.gen_id()
        code, employee1 = self.client.employee_create(
            self.org_id, {'name': 'employee1', 'auth_user_id': user1_id})
        patch('rest_api.rest_api_server.controllers.pool.PoolController.'
              '_authorize_action_for_user').start()
        self.client.pool_update(
            self.org['pool_id'], {'default_owner_id': employee1['id']})
        _, employee2 = self.client.employee_create(
            self.org_id, {'name': 'employee2', 'auth_user_id': user2_id})
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        code, child_pool = self.client.pool_create(self.org_id, {
            'name': 'ch1', 'parent_id': self.org['pool_id']})
        self.assertEqual(code, 201)

        resource = self._create_resource(
            cloud_account['id'], employee2['id'], child_pool['id'])
        self.assertEqual(resource['employee_id'], employee2['id'])
        resource2 = self._create_resource(
            cloud_account['id'], employee2['id'], child_pool['id'])
        self.assertEqual(resource2['employee_id'], employee2['id'])
        self._mock_auth_user(user1_id)
        patch('rest_api.rest_api_server.controllers.assignment.AssignmentController'
              '._authorize_action_for_pool', return_value=True).start()
        code, _ = self.client.rules_create(self.org_id, {
            'name': 'rule_%s' % employee2['name'],
            'pool_id': child_pool['id'],
            'owner_id': employee2['id'],
            'conditions': [
                {"type": "name_starts_with", "meta_info": employee2['name']}]
        })
        self.assertEqual(code, 201)

        user_name = 'John'
        self.p_get_user_info.return_value = {
            'display_name': user_name, 'id': self._user_id,
            'email': 'example@hystax.com'}
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.pool_delete(child_pool['id'])
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, child_pool['id'], 'pool',
            'pool_deleted', ANY)
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_pool_events(self):
        user_name = 'John'
        self.p_get_user_info.return_value = {
            'display_name': user_name, 'id': self._user_id,
            'email': 'example@hystax.com'}
        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)
        expected_evt_args = {
            'pool_name': pool['name'],
            'pool_id': pool['id'],
            'organization_id': self.org_id,
            'organization_name': self.org['name'],
            'user_name': user_name,
            'user_email': 'example@hystax.com'
        }
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, pool['id'], 'pool',
            'pool_created', {
                'object_name': pool['name']
            })
        p_publish_activities.assert_called_once_with(*activity_param_tuples)

        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.pool_update(pool['id'], {'purpose': 'team'})
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, pool['id'], 'pool',
            'pool_updated', {
                'object_name': pool['name'],
                'params': 'purpose: team'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

        p_publish_activities = patch(
            'rest_api.rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)
        expected_evt_args['new_pool_name'] = self.org['name']
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, pool['id'], 'pool',
            'pool_deleted', {
                'object_name': pool['name'],
                'res_count': 0,
                'new_pool_name': self.org['name'],
                'rules_cnt': 0
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_patch_auto_extension_no_permission_in_root(self):
        self._mock_auth_user(self.gen_id())
        code, _ = self.client.pool_update(self.org['pool_id'], {
            'limit': 50
        })
        self.assertEqual(code, 200)
        code, pool_1 = self.client.pool_create(self.org_id, {
            'name': 'pool_1_1', 'parent_id': self.org['pool_id'], 'limit': 20
        })
        self.assertEqual(code, 201)
        code, pool_2 = self.client.pool_create(self.org_id, {
            'name': 'pool_2_1', 'parent_id': pool_1['id'], 'limit': 10
        })
        self.assertEqual(code, 201)

        patch('rest_api.rest_api_server.controllers.pool.'
              'PoolController._get_assignments_actions_by_token',
              return_value={
                  'MANAGE_POOLS': [
                      ['pool', pool_1['id']]
                  ]
              }).start()
        code, ret = self.client.pool_update(pool_2['id'], {
            'limit': 25,
            'auto_extension': True
        })
        self.assertEqual(code, 200)
        code, ret = self.client.pool_get(pool_2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], 25)
        code, ret = self.client.pool_get(pool_1['id'])
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], 25)
        code, ret = self.client.pool_get(self.org['pool_id'])
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], 50)

        code, ret = self.client.pool_update(pool_2['id'], {
            'limit': 55,
            'auto_extension': True
        })
        self.assertEqual(code, 403)
        self.verify_error_code(ret, 'OE0471')
        code, ret = self.client.pool_get(pool_2['id'])
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], 25)

    def test_patch_auto_extension(self):
        patch('rest_api.rest_api_server.controllers.pool.'
              'PoolController._get_assignments_actions_by_token',
              return_value={
                  'MANAGE_POOLS': [
                      ['organization', self.org_id]
                  ]
              }).start()
        code, _ = self.client.pool_update(self.org['pool_id'], {
            'limit': 15
        })
        self._mock_auth_user(self.gen_id())
        code, pool_1 = self.client.pool_create(self.org_id, {
            'name': 'pool_1', 'parent_id': self.org['pool_id'], 'limit': 10
        })
        self.assertEqual(code, 201)
        code, pool_2 = self.client.pool_create(self.org_id, {
            'name': 'pool_2', 'parent_id': self.org['pool_id'], 'limit': 4
        })
        self.assertEqual(code, 201)
        code, pool_1_1 = self.client.pool_create(self.org_id, {
            'name': 'pool_1_1', 'parent_id': pool_1['id'], 'limit': 2
        })
        self.assertEqual(code, 201)
        code, pool_1_2 = self.client.pool_create(self.org_id, {
            'name': 'pool_1_2', 'parent_id': pool_1['id'], 'limit': 2
        })
        self.assertEqual(code, 201)
        params = {
            'limit': 10,
            'auto_extension': True
        }
        code, ret = self.client.pool_update(pool_1_1['id'], params)
        self.assertEqual(code, 200)
        self.assertEqual(ret['limit'], params['limit'])

        for pool_id, limit in {
            pool_1_1['id']: 10, pool_1_2['id']: 2, pool_1['id']: 12,
            pool_2['id']: 4, self.org['pool_id']: 16
        }.items():
            code, pool = self.client.pool_get(pool_id)
            self.assertEqual(code, 200)
            self.assertEqual(pool['limit'], limit)

        params = {
            'limit': 5,
            'auto_extension': True
        }
        code, ret = self.client.pool_update(pool_1['id'], params)
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0414')

    @patch('rest_api.rest_api_server.controllers.pool.PoolController.get_user_id')
    @patch('rest_api.rest_api_server.controllers.pool.PoolController.'
           '_get_assignments_actions_by_token')
    def test_create_auto_extension(self, p_actions_by_token, p_user_id):
        p_user_id.return_value = self.auth_user_1
        p_actions_by_token.return_value = {
            'MANAGE_POOLS': [
                ['organization', self.org_id]
            ]
        }

        code, _ = self.client.pool_update(self.org['pool_id'], {
            'limit': 10
        })
        self._mock_auth_user(self.auth_user_1)

        code, pool_1 = self.client.pool_create(self.org_id, {
            'name': 'pool_1', 'parent_id': self.org['pool_id'], 'limit': 10
        })
        self.assertEqual(code, 201)
        self.assertEqual(pool_1['limit'], 10)

        code, pool_2 = self.client.pool_create(self.org_id, {
            'name': 'pool_2', 'parent_id': self.org['pool_id'], 'limit': 20,
            'auto_extension': True
        })
        self.assertEqual(code, 201)
        self.assertEqual(pool_2['limit'], 20)

        code, pool_1_1 = self.client.pool_create(self.org_id, {
            'name': 'pool_1_1', 'parent_id': pool_1['id'], 'limit': 30,
            'auto_extension': True
        })
        self.assertEqual(code, 201)
        self.assertEqual(pool_1_1['limit'], 30)

        code, pool_1_2 = self.client.pool_create(self.org_id, {
            'name': 'pool_1_2', 'parent_id': pool_1['id'], 'limit': 40,
            'auto_extension': True
        })
        self.assertEqual(code, 201)
        self.assertEqual(pool_1_2['limit'], 40)

        for pool_id, limit in {
            pool_1_1['id']: 30, pool_1_2['id']: 40, pool_1['id']: 70,
            pool_2['id']: 20, self.org['pool_id']: 90
        }.items():
            code, pool = self.client.pool_get(pool_id)
            self.assertEqual(code, 200)
            self.assertEqual(pool['limit'], limit)

    def test_delete_org_constraint_on_pool_deleting(self):
        code, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)
        constr = self.create_org_constraint(self.org_id, pool['id'])

        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)
        code, resp = self.client.organization_constraint_get(constr['id'])
        self.assertEqual(code, 404)
        self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_delete_org_limit_hit_on_pool_deleting(self):
        code, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)
        self.create_org_limit_hit(self.org_id, pool['id'],
                                  filters={'pool_id': [pool['id']]})

        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        hits = session.query(OrganizationLimitHit).filter(and_(
            OrganizationLimitHit.organization_id == self.org_id,
            OrganizationLimitHit.deleted.is_(False)
        )).one_or_none()
        self.assertEqual(hits, None)

    def test_delete_org_limit_hit_on_pool_deleting_with_subpools(self):
        code, pool = self.client.pool_create(self.org_id, {
            'name': 'subpool', 'parent_id': self.org['pool_id'],
        })
        self.assertEqual(code, 201)
        self.create_org_limit_hit(self.org_id, pool['id'],
                                  filters={'pool_id': [pool['id'] + '+']})

        code, _ = self.client.pool_delete(pool['id'])
        self.assertEqual(code, 204)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        hits = session.query(OrganizationLimitHit).filter(and_(
            OrganizationLimitHit.organization_id == self.org_id,
            OrganizationLimitHit.deleted.is_(False)
        )).one_or_none()
        self.assertEqual(hits, None)

    def test_get_pool_children_only(self):
        code, org = self.client.organization_create({'name': 'org name'})
        _, org_pool = self.client.pool_update(org['pool_id'],
                                              {'limit': 600})
        code, child1 = self.client.pool_create(org['id'], {
            'name': 'ch1', 'parent_id': org_pool['id'], 'limit': 200})
        self.assertEqual(code, 201)
        code, child_of_child1 = self.client.pool_create(org['id'], {
            'name': 'ch-o-ch1', 'parent_id': child1['id'], 'limit': 100})
        self.assertEqual(code, 201)

        code, pools = self.client.pool_get(org['pool_id'],
                                           children=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(pools['children']), 2)
        root_pool_map = {
            'id': org_pool['id'],
            'name': org_pool['name'],
            'purpose': org_pool['purpose']
        }
        self.assertEqual({'id': pools['id'], 'name': pools['name'],
                          'purpose': pools['purpose']}, root_pool_map)

    def test_pool_get_date_range_validation(self):
        pool_id = self.org['pool_id']

        code, resp = self.client.pool_get(pool_id, start_date=1000000)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0561')

        code, resp = self.client.pool_get(pool_id, end_date=1000000)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0561')

        code, resp = self.client.pool_get(
            pool_id, start_date=2000000, end_date=1000000)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

        code, resp = self.client.pool_get(
            pool_id, start_date=-1, end_date=1000000)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0224')

        code, resp = self.client.pool_get(
            pool_id, start_date=0, end_date=7776001)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0574')

    def test_pool_get_date_range_without_details(self):
        pool_id = self.org['pool_id']
        start_ts = 1000000
        end_ts = 2000000

        code, pool = self.client.pool_get(
            pool_id, start_date=start_ts, end_date=end_ts)
        self.assertEqual(code, 200)
        self.assertEqual(pool['expense_start_date'], start_ts)
        self.assertEqual(pool['expense_end_date'], end_ts)
        self.assertNotIn('cost', pool)

    def test_pool_get_date_range_with_details(self):
        _, cloud_acc = self.create_cloud_account(
            self.org_id,
            {'name': 'test_acc', 'type': 'aws_cnr',
             'config': {'access_key_id': 'key', 'secret_access_key': 'secret'}},
            auth_user_id=self.auth_user_1)
        resource = self._create_resource(
            cloud_acc['id'], pool_id=self.org['pool_id'])

        for date, cost in [
            (datetime(2021, 1, 5), 100),
            (datetime(2021, 1, 15), 50),
            (datetime(2021, 1, 25), 30),
        ]:
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': cost,
                'date': date,
                'cloud_account_id': cloud_acc['id'],
                'sign': 1,
            })

        range_start = datetime(2021, 1, 10)
        range_end = datetime(2021, 1, 31)
        with freeze_time(datetime(2021, 2, 15)):
            code, pool = self.client.pool_get(
                self.org['pool_id'], details=True,
                start_date=int(range_start.timestamp()),
                end_date=int(range_end.timestamp()))

        self.assertEqual(code, 200)
        self.assertEqual(pool['cost'], 80)
        self.assertEqual(pool['expense_start_date'], int(range_start.timestamp()))
        self.assertEqual(pool['expense_end_date'], int(range_end.timestamp()))

    def test_pool_get_date_range_hierarchy(self):
        _, cloud_acc = self.create_cloud_account(
            self.org_id,
            {'name': 'test_acc', 'type': 'aws_cnr',
             'config': {'access_key_id': 'key', 'secret_access_key': 'secret'}},
            auth_user_id=self.auth_user_1)
        _, child = self.client.pool_create(
            self.org_id, {'name': 'child', 'parent_id': self.org['pool_id']})

        for pool_id, expense_dates in [
            (self.org['pool_id'], [(datetime(2021, 1, 15), 40)]),
            (child['id'], [
                (datetime(2021, 1, 5), 999),  # out of date range
                (datetime(2021, 1, 15), 60)
            ]),
        ]:
            resource = self._create_resource(
                cloud_acc['id'], pool_id=pool_id,
                employee_id=self.employee_1_1['id']
            )
            for date, cost in expense_dates:
                self.expenses.append({
                    'resource_id': resource['id'],
                    'cost': cost,
                    'date': date,
                    'cloud_account_id': cloud_acc['id'],
                    'sign': 1,
                })

        range_start = datetime(2021, 1, 10)
        range_end = datetime(2021, 1, 31)
        code, pool = self.client.pool_get(
            self.org['pool_id'], details=True, children=True,
            start_date=int(range_start.timestamp()),
            end_date=int(range_end.timestamp()))

        self.assertEqual(code, 200)
        self.assertEqual(pool['cost'], 100)
        child_data = next(c for c in pool['children'] if c['id'] == child['id'])
        self.assertEqual(child_data['cost'], 60)

        # all month
        with freeze_time(range_end):
            code, pool = self.client.pool_get(
                self.org['pool_id'], details=True)
        self.assertEqual(code, 200)
        self.assertEqual(pool['cost'], 1099)

    def test_pool_get_date_range_forecast_current_month(self):
        _, cloud_acc = self.create_cloud_account(
            self.org_id,
            {'name': 'test_acc', 'type': 'aws_cnr',
             'config': {'access_key_id': 'key', 'secret_access_key': 'secret'}},
            auth_user_id=self.auth_user_1)
        resource = self._create_resource(
            cloud_acc['id'], pool_id=self.org['pool_id'])

        for date, cost in [
            (datetime(2021, 1, 15), 50),
            (datetime(2021, 2, 5), 200),
        ]:
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': cost,
                'date': date,
                'cloud_account_id': cloud_acc['id'],
                'sign': 1,
            })

        with freeze_time(datetime(2021, 2, 15)):
            # current month
            code, pool = self.client.pool_get(
                self.org['pool_id'], details=True)
            self.assertEqual(code, 200)
            self.assertEqual(pool['cost'], 200)
            self.assertEqual(pool['forecast'], 312.9)

            # prev month
            range_start = datetime(2021, 1, 1)
            range_end = datetime(2021, 1, 31)
            code, pool = self.client.pool_get(
                self.org['pool_id'], details=True,
                start_date=int(range_start.timestamp()),
                end_date=int(range_end.timestamp()))
            self.assertEqual(code, 200)
            self.assertEqual(pool['cost'], 50)
            self.assertEqual(pool['forecast'], 312.9)


class TestPoolExpensesReportApi(PoolApiTestBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_cloud_acc_dict,
            auth_user_id=self.auth_user_1)
        self.start_date = int(datetime(
            2021, 1, 1, tzinfo=timezone.utc).timestamp())
        self.end_date = int(datetime(
            2021, 1, 31, tzinfo=timezone.utc).timestamp())

    def _parse_csv(self, body):
        reader = csv.DictReader(io.StringIO(body))
        return list(reader)

    def test_missing_param(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, None, self.end_date, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.start_date, None, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.start_date, self.end_date, None)
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0216')

    def test_invalid_format(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.start_date, self.end_date, 'pdf')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0473')

    def test_end_before_start(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.end_date, self.start_date, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

    def test_unknown_org(self):
        code, resp = self.client.pool_expenses_report_get(
            str(uuid.uuid4()), self.start_date, self.end_date, 'csv')
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_pool_expenses_report_date_range_validation(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, 2000000, 1000000, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0446')

        code, resp = self.client.pool_expenses_report_get(
            self.org_id, -1, 1000000, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0224')

        code, resp = self.client.pool_expenses_report_get(
            self.org_id, 0, 7776001, 'csv')
        self.assertEqual(code, 400)
        self.verify_error_code(resp, 'OE0574')

    def test_csv_root_pool_always_included(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.start_date, self.end_date, 'csv')
        self.assertEqual(code, 200)
        rows = self._parse_csv(resp)
        pool_ids = [r['Pool ID'] for r in rows]
        self.assertIn(self.org['pool_id'], pool_ids)

    def test_xlsx_ok(self):
        code, resp = self.client.pool_expenses_report_get(
            self.org_id, self.start_date, self.end_date, 'xlsx')
        self.assertEqual(code, 200)

    def test_csv_level_hierarchy_costs(self):
        root_id = self.org['pool_id']
        _, marketing = self.client.pool_create(
            self.org_id, {'name': 'Marketing', 'parent_id': root_id})
        _, engineering = self.client.pool_create(
            self.org_id, {'name': 'Engineering', 'parent_id': root_id})
        _, dev = self.client.pool_create(
            self.org_id, {'name': 'Dev', 'parent_id': engineering['id']})
        _, qa = self.client.pool_create(
            self.org_id, {'name': 'QA', 'parent_id': engineering['id']})
        _, release = self.client.pool_create(
            self.org_id, {'name': 'Release 3.4', 'parent_id': qa['id']})

        for pool_id, cost in [
            (root_id, 50.0),
            (marketing['id'], 1200.0),
            (engineering['id'], 500.0),
            (dev['id'], 200.0),
            (qa['id'], 300.0),
            (release['id'], 100.0),
        ]:
            resource = self._create_resource(
                self.cloud_acc['id'], employee_id=self.employee_1_1['id'],
                pool_id=pool_id)
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': cost,
                'date': datetime(2021, 1, 15),
                'cloud_account_id': self.cloud_acc['id'],
                'sign': 1,
            })

        with freeze_time(datetime(2021, 2, 1)):
            code, body = self.client.pool_expenses_report_get(
                self.org_id, self.start_date, self.end_date, 'csv')
        self.assertEqual(code, 200)
        rows = self._parse_csv(body)

        headers = list(rows[0].keys())
        self.assertIn('Level 4', headers)
        self.assertNotIn('Level 5', headers)

        by_id = {r['Pool ID']: r for r in rows}

        def check(pool_id, expected_path, direct, subtree):
            row = by_id[pool_id]
            for i, name in enumerate(expected_path, start=1):
                self.assertEqual(row['Level %d' % i], name)
            for i in range(len(expected_path) + 1, 5):
                self.assertEqual(row['Level %d' % i], '')
            self.assertEqual(float(row['Direct expense']), direct)
            self.assertEqual(float(row['Subtree expense']), subtree)

        org_name = self.org['name']
        check(root_id, [org_name], 50.0, 2350.0)
        check(marketing['id'], [org_name, 'Marketing'], 1200.0, 1200.0)
        check(engineering['id'], [org_name, 'Engineering'], 500.0, 1100.0)
        check(dev['id'], [org_name, 'Engineering', 'Dev'], 200.0, 200.0)
        check(qa['id'], [org_name, 'Engineering', 'QA'], 300.0, 400.0)
        check(release['id'], [org_name, 'Engineering', 'QA', 'Release 3.4'],
              100.0, 100.0)

    def test_csv_dfs_ordering(self):
        names = ['gamma', 'alpha', 'delta', 'beta']
        children = {}
        for name in names:
            _, pool = self.client.pool_create(
                self.org_id, {'name': name, 'parent_id': self.org['pool_id']})
            children[name] = pool

        expenses_by_pool = {
            self.org['pool_id']: 100.0,
            children['alpha']['id']: 40.0,
            children['delta']['id']: 20.0,
            children['gamma']['id']: 10.0,
        }
        for pool_id, cost in expenses_by_pool.items():
            resource = self._create_resource(
                self.cloud_acc['id'], employee_id=self.employee_1_1['id'],
                pool_id=pool_id)
            self.expenses.append({
                'resource_id': resource['id'],
                'cost': cost,
                'date': datetime(2021, 1, 15),
                'cloud_account_id': self.cloud_acc['id'],
                'sign': 1,
            })

        with freeze_time(datetime(2021, 2, 1)):
            code, resp = self.client.pool_expenses_report_get(
                self.org_id, self.start_date, self.end_date, 'csv')
        self.assertEqual(code, 200)
        rows = self._parse_csv(resp)
        ids = [r['Pool ID'] for r in rows]

        root_idx = ids.index(self.org['pool_id'])
        alpha_idx = ids.index(children['alpha']['id'])
        beta_idx = ids.index(children['beta']['id'])
        delta_idx = ids.index(children['delta']['id'])
        gamma_idx = ids.index(children['gamma']['id'])

        self.assertLess(root_idx, alpha_idx)
        self.assertLess(alpha_idx, beta_idx)
        self.assertLess(beta_idx, delta_idx)
        self.assertLess(delta_idx, gamma_idx)

        by_id = {r['Pool ID']: r for r in rows}
        root_row = by_id[self.org['pool_id']]
        self.assertEqual(float(root_row['Direct expense']), 100.0)
        self.assertEqual(float(root_row['Subtree expense']), 170.0)

        self.assertEqual(float(
            by_id[children['alpha']['id']]['Direct expense']), 40.0)
        self.assertEqual(
            float(by_id[children['alpha']['id']]['Subtree expense']), 40.0)
        self.assertEqual(
            float(by_id[children['beta']['id']]['Direct expense']), 0.0)
        self.assertEqual(
            float(by_id[children['beta']['id']]['Subtree expense']), 0.0)
        self.assertEqual(
            float(by_id[children['delta']['id']]['Direct expense']), 20.0)
        self.assertEqual(
            float(by_id[children['gamma']['id']]['Direct expense']), 10.0)

    def test_csv_injection_escaped(self):
        inj = '=HYPERLINK("http://evil","x")'
        _, inj_pool = self.client.pool_create(
            self.org_id,
            {'name': inj, 'parent_id': self.org['pool_id']})
        with freeze_time(datetime(2021, 2, 1)):
            code, body = self.client.pool_expenses_report_get(
                self.org_id, self.start_date, self.end_date, 'csv')
        self.assertEqual(code, 200)
        rows = self._parse_csv(body)
        pool_id_map = {r['Pool ID']: r for r in rows}
        inj_row = pool_id_map[inj_pool['id']]
        self.assertEqual(inj_row['Level 2'], f"'{inj}")
