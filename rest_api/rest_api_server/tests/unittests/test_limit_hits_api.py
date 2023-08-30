import uuid
from unittest.mock import patch

from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.enums import ConstraintTypes, ConstraintLimitStates
from rest_api.rest_api_server.models.models import ConstraintLimitHit

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestLimitHitsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)

        _, self.org = self.client.organization_create({'name': "partner"})
        self.client.pool_update(self.org['pool_id'], {'limit': 20})
        self.org_id = self.org['id']
        self.valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        patch('tools.cloud_adapter.clouds.aws.Aws.configure_report').start()
        patch('tools.cloud_adapter.clouds.aws.Aws.validate_credentials',
              return_value={'account_id': '1', 'warnings': []}).start()
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'John', 'auth_user_id': self.user_id})
        code, self.cloud_acc = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, auth_user_id=self.user_id)
        self.cloud_acc_id = self.cloud_acc['id']

        _, self.pool = self.client.pool_create(self.org_id, {
            'name': 'pool', 'limit': 10, 'parent_id': self.org['pool_id']
        })
        self._mock_auth_user(self.user_id)

    def generate_resources(self, count=1):
        valid_resource = {
            'cloud_resource_id': 'res_id',
            'name': 'resource',
            'resource_type': 'test',
            'pool_id': self.pool['id'],
            'employee_id': self.employee['id'],
            'tags': {
                'key': 'value'
            }
        }

        res = []
        for val in range(count):
            valid_resource.update({
                'cloud_resource_id': 'resource_%s' % val,
            })
            code, resource = self.cloud_resource_create(
                self.cloud_acc_id, valid_resource)
            res.append(resource)
        return res

    def generate_limit_hits(self, resource, count=1,
                            limit_type=ConstraintTypes.TTL):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        res = []
        ttl_value = 1234 if limit_type == ConstraintTypes.TTL else None
        expense_value = 1234 if limit_type != ConstraintTypes.TTL else None
        for val in range(count):
            limit_hit = ConstraintLimitHit(
                resource_id=resource['id'],
                pool_id=resource['pool_id'],
                type=limit_type,
                constraint_limit=123,
                ttl_value=ttl_value,
                expense_value=expense_value,
                organization_id=self.org_id,
            )
            session.add(limit_hit)
            res.append(limit_hit)
        session.commit()
        return list(map(lambda x: x.to_dict(), res))

    def test_pool_limit_heats_wrong_pool(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource))
        code, resp = self.client.pool_limit_hits_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_resource_limit_heats_wrong_res(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource))
        code, resp = self.client.resource_limit_hits_list(str(uuid.uuid4()))
        self.assertEqual(code, 404)

    def test_pool_limit_empty(self):
        code, resp = self.client.pool_limit_hits_list(self.pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(0, len(resp['limit_hits']))

        self.generate_resources(1)
        code, resp = self.client.pool_limit_hits_list(self.pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(0, len(resp['limit_hits']))

    def test_pool_limit_hits(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource))
        resource_id = hits[0]['resource_id']
        code, resp = self.client.pool_limit_hits_list(self.pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits), len(resp['limit_hits']))
        self.assertEqual(resource_id, resp['limit_hits'][0]['resource_id'])

        for resource in resources:
            hits.extend(self.generate_limit_hits(resource, count=2))
        code, resp = self.client.pool_limit_hits_list(self.pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits), len(resp['limit_hits']))
        for val in resp['limit_hits']:
            self.assertEqual(resource_id, val['resource_id'])

    def test_pool_limit_hits_several(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource, count=5))
        resource_id = hits[0]['resource_id']
        code, resp = self.client.pool_limit_hits_list(self.pool['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits), len(resp['limit_hits']))
        self.assertEqual(resource_id, resp['limit_hits'][0]['resource_id'])

    def test_resource_limit_hits(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource))
        resource_id = hits[0]['resource_id']

        code, resp = self.client.resource_limit_hits_list(resources[0]['id'])
        self.assertEqual(code, 200)
        self.assertEqual(1, len(resp['limit_hits']))
        self.assertEqual(resource_id, resp['limit_hits'][0]['resource_id'])

    def test_resource_daily_limit(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(
                resource, limit_type=ConstraintTypes.DAILY_EXPENSE_LIMIT))
        resource_id = hits[0]['resource_id']

        code, resp = self.client.resource_limit_hits_list(resources[0]['id'])
        self.assertEqual(code, 200)
        self.assertEqual(1, len(resp['limit_hits']))
        limit_hit = resp['limit_hits'][0]
        self.assertEqual(resource_id, resp['limit_hits'][0]['resource_id'])
        self.assertEqual(limit_hit['state'], ConstraintLimitStates.RED.value)

    def test_resource_limit_hits_several(self):
        resources = self.generate_resources(1)
        hits = []
        for resource in resources:
            hits.extend(self.generate_limit_hits(resource, count=5))
        resource_id = hits[0]['resource_id']

        code, resp = self.client.resource_limit_hits_list(resources[0]['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits), len(resp['limit_hits']))
        self.assertEqual(resource_id, resp['limit_hits'][0]['resource_id'])
