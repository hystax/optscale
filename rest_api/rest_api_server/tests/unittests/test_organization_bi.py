import os
import json
import uuid
from cryptography.fernet import Fernet

from unittest.mock import patch

from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.db_factory import DBType, DBFactory
from rest_api.rest_api_server.models.enums import (
    BITypes,
    BIOrganizationStatuses,
)
from rest_api.rest_api_server.models.models import OrganizationBI
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import encrypt_bi_meta


class TestOrganizationBI(TestApiBase):
    def create_org_bi(
            self, organization_id, type_, name, days=1,
            status=BIOrganizationStatuses.ACTIVE, last_status_error=None):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        meta = json.dumps(self.meta)
        org_bi = OrganizationBI(
            organization_id=organization_id,
            type=type_,
            name=name,
            days=days,
            status=status,
            meta=encrypt_bi_meta(meta),
            last_status_error=last_status_error
        )
        session.add(org_bi)
        session.commit()
        return org_bi.to_dict()

    def setUp(self, version="v2"):
        super().setUp(version)

        encr_key = Fernet.generate_key()
        patch('rest_api.rest_api_server.utils.get_bi_encryption_key',
              return_value=encr_key).start()

        self.meta = {
            'access_key_id': 'access_key_id',
            'secret_access_key': 'secret_access_key',
            'bucket': 'bucket'
        }

        _, self.org = self.client.organization_create({"name": "partner"})
        self.org_id_1 = self.org["id"]
        self.org_bi_1 = self.create_org_bi(
            self.org_id_1, BITypes.AWS_RAW_EXPORT, "partner", 180
        )

        _, self.org2 = self.client.organization_create({"name": "partner_2"})
        self.org_id_2 = self.org2["id"]

    def test_create_bi(self):
        ret, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 'aws', **self.meta)
        self.assertEqual(201, ret)
        self.assertNotIn('secret_access_key', res['meta'])

        account_name = 'storage-account'
        meta = {
            'container': 'container',
            'connection_string': 'test;AccountName={};test'.format(account_name),
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(201, ret)
        self.assertNotIn('connection_string', res['meta'])
        self.assertEqual(res['meta']['storage_account'], account_name)

    def test_create_bi_meta(self):
        # AWS
        meta = {
            'access_key_id': 'access_key_id',
            'secret_access_key': 'secret_access_key',
            'bucket': 'bucket',
            's3_prefix': 's3_prefix'
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 'aws', **meta)
        self.assertEqual(201, ret)
        self.assertNotIn('secret_access_key', res['meta'])

        meta.pop('s3_prefix')
        for key in meta:
            params = meta.copy()
            params.pop(key)
            ret, res = self.client.bi_create(
                self.org_id_1, 'AWS_RAW_EXPORT', 'aws', **params)
            self.assertEqual(400, ret)
            self.assertEqual(res['error']['error_code'], 'OE0216')

        meta['impostor'] = 'impostor'
        ret, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 'aws', **meta)
        self.assertEqual(400, ret)
        self.assertEqual(res['error']['error_code'], 'OE0546')

        # AZURE
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(400, ret)
        self.assertEqual(res['error']['error_code'], 'OE0546')

        meta = {
            'container': 'container',
            'connection_string': 'connection_string'
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(400, ret)
        self.assertNotIn(res['error']['error_code'], 'OE0149')

        meta = {
            'container': 'container',
            'connection_string': 'test;AccountName=test;test'
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(201, ret)
        self.assertNotIn('connection_string', res['meta'])

        for key in meta:
            params = meta.copy()
            params.pop(key)
            ret, res = self.client.bi_create(
                self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **params)
            self.assertEqual(400, ret)
            self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_create_meta_invalid_type_params(self):
        # AWS
        meta = {
            'access_key_id': 'access_key_id',
            'secret_access_key': 'secret_access_key',
            'bucket': 'bucket',
            's3_prefix': 's3_prefix'
        }
        for k, v in meta.items():
            params = meta.copy()
            for p in [{'test': 'test'}, 123]:
                params[k] = p
                ret, res = self.client.bi_create(
                    self.org_id_1, 'AWS_RAW_EXPORT', 'aws', **params)
                self.assertEqual(400, ret)
                self.assertEqual(res['error']['error_code'], 'OE0214')

        # AZURE
        meta = {
            'container': 'container',
            'connection_string': 'connection_string'
        }
        for k, v in meta.items():
            params = meta.copy()
            for p in [{'test': 'test'}, 123]:
                params[k] = p
                ret, res = self.client.bi_create(
                    self.org_id_1, 'AZURE_RAW_EXPORT', 'aws', **params)
                self.assertEqual(400, ret)
                self.assertEqual(res['error']['error_code'], 'OE0214')

    def test_create_without_name(self):
        org_name = 'test_org'
        code, org = self.client.organization_create({"name": org_name})
        self.assertEqual(code, 201)
        ret, res = self.client.bi_create(
            org['id'], 'AWS_RAW_EXPORT', None, **self.meta)
        self.assertEqual(code, 201)
        self.assertEqual(res['name'], org_name)

    def test_create_invalid_name(self):
        ret, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 123, **self.meta)
        self.assertEqual(400, ret)
        self.assertEqual(res['error']['error_code'], 'OE0214')

    def test_create_invalid_days(self):
        ret, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 'name', 'days', **self.meta)
        self.assertEqual(400, ret)
        self.assertEqual(res['error']['error_code'], 'OE0223')

    def test_create_invalid_type(self):
        ret, res = self.client.bi_create(
            self.org_id_1, 'type', 'name', 190, **self.meta)
        self.assertEqual(400, ret)
        self.assertEqual(res['error']['error_code'], 'OE0174')

    def test_create_unexpected(self):
        body = {
            'type': 'AWS_RAW_EXPORT',
            'name': 'test',
            'meta': self.meta,
        }
        for key in ['status', 'last_run', 'next_run', 'last_completed',
                    'last_status_error', 'impostor']:
            params = body.copy()
            params[key] = 'test'
            code, res = self.client.post(
                self.client.bi_url(org_id=self.org['id']), params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_create_meta_missing(self):
        code, res = self.client.bi_create(
            self.org_id_1, 'AWS_RAW_EXPORT', 'test')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0216')

    def test_bi_with_same_name(self):
        name = 'bi_name'
        ret, res = self.client.bi_create(
            self.org_id_1,
            BITypes.AWS_RAW_EXPORT.value,
            name,
            **self.meta
        )
        self.assertEqual(201, ret)

        ret, res = self.client.bi_create(
            self.org_id_1,
            BITypes.AWS_RAW_EXPORT.value,
            name,
            **self.meta
        )
        self.assertEqual(409, ret)
        self.assertEqual(res['error']['error_code'], 'OE0149')

    def test_update_to_bi_with_same_name(self):
        name = 'bi_name'
        ret, res = self.client.bi_create(
            self.org_id_1,
            BITypes.AWS_RAW_EXPORT.value,
            name,
            **self.meta
        )
        self.assertEqual(201, ret)

        ret, res = self.client.bi_create(
            self.org_id_1,
            BITypes.AWS_RAW_EXPORT.value,
            'bi_name1',
            **self.meta
        )
        self.assertEqual(201, ret)

        body = {'name': name}
        ret, res = self.client.bi_update(res['id'], body)
        self.assertEqual(409, ret)
        self.assertEqual(res['error']['error_code'], 'OE0149')

    def test_create_invalid_org(self):
        code, org = self.client.organization_create({"name": "test2"})
        self.assertEqual(code, 201)
        code, _ = self.client.organization_delete(org['id'])
        for value in [org['id'], 'impostor']:
            code, res = self.client.bi_create(
                value, 'AWS_RAW_EXPORT', 'name', 190, **self.meta)
            self.assertEqual(code, 404)
            self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_invalid_org(self):
        code, org = self.client.organization_create({"name": "test2"})
        self.assertEqual(code, 201)
        code, _ = self.client.organization_delete(org['id'])
        for value in [org['id'], 'impostor']:
            code, res = self.client.bi_list(value)
            self.assertEqual(code, 404)
            self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_get_invalid_bi_id(self):
        bi = self.create_org_bi(self.org_id_1, 'AWS_RAW_EXPORT', 'test_bi', 2)
        code, _ = self.client.bi_delete(bi['id'])
        self.assertEqual(code, 204)
        for value in ['impostor', bi['id']]:
            code, resp = self.client.bi_get(value)
            self.assertEqual(code, 404)
            self.assertEqual(resp['error']['error_code'], 'OE0002')

    def test_organization_bis_list(self):
        ret, res = self.client.bi_list(org_id=self.org_id_1)
        self.assertEqual(200, ret)
        self.assertEqual(1, len(res["organization_bis"]))
        bi = res["organization_bis"][0]
        self.assertEqual(BITypes.AWS_RAW_EXPORT.value, bi["type"])
        self.assertIn('secret_access_key', bi['meta'])

        ret, res = self.client.bi_list(org_id=self.org_id_2)
        self.assertEqual(200, ret)
        self.assertEqual(0, len(res["organization_bis"]))
        self.assertIn('secret_access_key', bi['meta'])

        patch('rest_api.rest_api_server.handlers.v2.organization_bis.'
              'OrganizationBIAsyncCollectionHandler.check_cluster_secret',
              return_value=False).start()
        ret, res = self.client.bi_list(org_id=self.org_id_1)
        self.assertEqual(200, ret)
        self.assertEqual(1, len(res["organization_bis"]))
        self.assertNotIn('secret_access_key', res["organization_bis"][0]['meta'])

    def test_bi_list(self):
        _ = self.create_org_bi(self.org_id_2, BITypes.AWS_RAW_EXPORT, "test", 180)
        ret, res = self.client.bi_list()
        self.assertEqual(200, ret)
        self.assertEqual(2, len(res["organization_bis"]))
        self.assertIn('secret_access_key', res["organization_bis"][0]['meta'])

    def test_bi_item_get(self):
        ret, res = self.client.bi_get(self.org_bi_1['id'])
        self.assertEqual(200, ret)
        self.assertEqual(BITypes.AWS_RAW_EXPORT.value, res["type"])
        self.assertIn('secret_access_key', res['meta'])
        files = [
            'bucket/expenses/{}_expenses.csv'.format(res['id']),
            'bucket/recommendations/{}_recommendations.csv'.format(res['id']),
            'bucket/resources/{}_resources.csv'.format(res['id'])]
        self.assertEqual(res['files'], files)

        patch('rest_api.rest_api_server.handlers.v2.organization_bis.'
              'BIAsyncItemHandler.check_cluster_secret',
              return_value=False).start()
        ret, res = self.client.bi_get(self.org_bi_1['id'])
        self.assertEqual(200, ret)
        self.assertEqual(BITypes.AWS_RAW_EXPORT.value, res["type"])
        self.assertNotIn('secret_access_key', res['meta'])
        files = [
            'bucket/expenses/{}_expenses.csv'.format(res['id']),
            'bucket/recommendations/{}_recommendations.csv'.format(res['id']),
            'bucket/resources/{}_resources.csv'.format(res['id'])]
        self.assertEqual(res['files'], files)

    def test_get_item_azure(self):
        account_name = 'test'
        container = 'container'
        meta = {
            'container': container,
            'connection_string': 'test;AccountName={};test'.format(account_name)
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(201, ret)

        ret, res = self.client.bi_get(res['id'])
        self.assertEqual(200, ret)
        files = [
            '{0}/{1}/{2}_expenses.csv'.format(account_name, container, res['id']),
            '{0}/{1}/{2}_recommendations.csv'.format(
                account_name, container, res['id']),
            '{0}/{1}/{2}_resources.csv'.format(
                account_name, container, res['id'])]
        self.assertEqual(res['files'], files)

    def test_bi_item_delete(self):
        bi = self.create_org_bi(
            self.org_bi_1['id'], 'AWS_RAW_EXPORT', 'bi_name', 1)

        code, res = self.client.bi_delete(bi['id'])
        self.assertEqual(204, code)

    def test_bi_update(self):
        ret, res = self.client.bi_get(self.org_bi_1['id'])
        self.assertEqual(200, ret)

        for param, value in [('next_run', 1), ('last_run', 1),
                             ('last_completed', 1), ('name', 'new_name'),
                             ('days', 1)]:
            ret, res = self.client.bi_update(self.org_bi_1['id'],
                                             {param: value})
            self.assertIn('secret_access_key', res['meta'])
            self.assertEqual(200, ret)
            self.assertEqual(value, res[param])

        meta = self.meta.copy()
        meta['bucket'] = 'updated'
        ret, res = self.client.bi_update(self.org_bi_1['id'],
                                         {'meta': meta})
        self.assertEqual(200, ret)
        self.assertEqual(meta['bucket'], res['meta']['bucket'])
        self.assertIn('secret_access_key', res['meta'])

        patch('rest_api.rest_api_server.handlers.v2.organization_bis.'
              'BIAsyncItemHandler.check_cluster_secret',
              return_value=False).start()
        ret, res = self.client.bi_update(self.org_bi_1['id'],
                                         {'meta': meta})
        self.assertEqual(200, ret)
        self.assertNotIn('secret_access_key', res['meta'])

    def test_update_meta_invalid_type_params(self):
        # AWS
        bi = self.create_org_bi(self.org_id_1, 'AWS_RAW_EXPORT', 'aws_bi_1')
        meta = {
            'access_key_id': 'access_key_id',
            'secret_access_key': 'secret_access_key',
            'bucket': 'bucket',
            's3_prefix': 's3_prefix'
        }
        for k, v in meta.items():
            params = meta.copy()
            for p in [{'test': 'test'}, 123]:
                params[k] = p
                ret, res = self.client.bi_update(bi['id'], {'meta': params})
                self.assertEqual(400, ret)
                self.assertEqual(res['error']['error_code'], 'OE0214')

        # AZURE
        bi = self.create_org_bi(self.org_id_1, 'AZURE_RAW_EXPORT', 'azure_bi_1')
        meta = {
            'container': 'container',
            'connection_string': 'connection_string'
        }
        for k, v in meta.items():
            params = meta.copy()
            for p in [{'test': 'test'}, 123]:
                params[k] = p
                ret, res = self.client.bi_update(bi['id'], {'meta': params})
                self.assertEqual(400, ret)
                self.assertEqual(res['error']['error_code'], 'OE0214')

    def test_update_unexpected(self):
        for param in ['organization_id', 'impostor', 'id', 'created_at', 'type']:
            ret, res = self.client.bi_update(
                self.org_bi_1['id'], {param: 'test'})
            self.assertEqual(400, ret)
            self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_update_invalid_bi_id(self):
        ret, res = self.client.bi_update('missing', {'name': 'test'})
        self.assertEqual(404, ret)
        self.assertEqual(res['error']['error_code'], 'OE0002')

        patch('rest_api.rest_api_server.handlers.v2.organization_bis.'
              'BIAsyncItemHandler.check_cluster_secret',
              return_value=False).start()
        ret, res = self.client.bi_update('missing', {'name': 'test'})
        self.assertEqual(404, ret)
        self.assertEqual(res['error']['error_code'], 'OE0002')

    def test_organization_bis_invalid_org_id(self):
        ret, res = self.client.bi_list(org_id="invalid_org_id")
        self.assertEqual(404, ret)
        self.verify_error_code(res, "OE0002")

    def test_bi_item_get_invalid_id(self):
        ret, res = self.client.bi_get("invalid_id")
        self.assertEqual(404, ret)
        self.verify_error_code(res, "OE0002")

    def test_bi_update_invalid_body(self):
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.SUCCESS)
        for body, e_code, e_resp in [
            (
                {
                    "status": BIOrganizationStatuses.SUCCESS,
                    "last_status_error": "error",
                },
                424, "OE0523",
            ),
            ({"next_run": -1}, 400, "OE0224"),
            ({"last_run": -1}, 400, "OE0224"),
            ({"last_completed": -1}, 400, "OE0224"),
            ({"days": -1}, 400, "OE0224"),
            ({"name": -1}, 400, "OE0214"),
            ({"meta": "not a dict"}, 400, "OE0344"),
            ({"meta": {"connection_string": "impostor"}}, 400, "OE0546"),
            ({"last_status_error": -1}, 400, "OE0214"),
            ({"status": -1}, 400, "OE0214"),
        ]:
            ret, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(e_code, ret)
            self.verify_error_code(res, e_resp)

    def test_bi_transitions(self):
        # ACTIVE
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.ACTIVE)
        for state in ['RUNNING', 'FAILED', 'SUCCESS']:
            body = {'status': state}
            if state == 'FAILED':
                body['last_status_error'] = 'error'
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 424)
            self.verify_error_code(res, "OE0521")

        for state in ['ACTIVE', 'QUEUED']:
            bi = self.create_org_bi(
                self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
                status=BIOrganizationStatuses.ACTIVE)
            body = {'status': state}
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 200)
            self.assertEqual(res['status'], state)

        # QUEUED
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.QUEUED)
        for state in ['ACTIVE', 'FAILED', 'SUCCESS']:
            body = {'status': state}
            if state == 'FAILED':
                body['last_status_error'] = 'error'
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 424)
            self.verify_error_code(res, "OE0521")

        for state in ['RUNNING', 'QUEUED']:
            bi = self.create_org_bi(
                self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
                status=BIOrganizationStatuses.QUEUED)
            body = {'status': state}
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 200)
            self.assertEqual(res['status'], state)

        # RUNNING
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.RUNNING)
        for state in ['ACTIVE']:
            body = {'status': state}
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 424)
            self.verify_error_code(res, "OE0521")

        for state in ['RUNNING', 'QUEUED', 'SUCCESS', 'FAILED']:
            bi = self.create_org_bi(
                self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
                status=BIOrganizationStatuses.RUNNING)
            body = {'status': state}
            if state == 'FAILED':
                body['last_status_error'] = 'error'
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 200)
            self.assertEqual(res['status'], state)

        # SUCCESS
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.SUCCESS)
        for state in ['ACTIVE', 'RUNNING', 'FAILED']:
            body = {'status': state}
            if state == 'FAILED':
                body['last_status_error'] = 'error'
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 424)
            self.verify_error_code(res, "OE0521")

        for state in ['QUEUED', 'SUCCESS']:
            bi = self.create_org_bi(
                self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
                status=BIOrganizationStatuses.SUCCESS)
            body = {'status': state}
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 200)
            self.assertEqual(res['status'], state)

        # FAILED
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.FAILED)
        for state in ['ACTIVE', 'RUNNING', 'SUCCESS']:
            body = {'status': state}
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 424)
            self.verify_error_code(res, "OE0521")

        for state in ['QUEUED', 'FAILED']:
            bi = self.create_org_bi(
                self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
                status=BIOrganizationStatuses.FAILED)
            body = {'status': state}
            if state == 'FAILED':
                body['last_status_error'] = 'error'
            code, res = self.client.bi_update(bi['id'], body)
            self.assertEqual(code, 200)
            self.assertEqual(res['status'], state)

    def test_update_last_status_error(self):
        """
        validating some state transitions focusing on 'last_status_error'.
        'last_status_error' must be set for FAILED
        'last_status_error' is reset to None for SUCCESS automatically
        """
        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.RUNNING)
        body = {'status': 'FAILED', 'last_status_error': 'error'}
        code, res = self.client.bi_update(bi['id'], body)
        self.assertEqual(code, 200)
        self.assertEqual(res['status'], 'FAILED')

        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.RUNNING)
        body = {'status': 'FAILED'}
        code, res = self.client.bi_update(bi['id'], body)
        self.assertEqual(code, 424)
        self.assertEqual(res['error']['error_code'], 'OE0525')

        bi = self.create_org_bi(
            self.org_id_1, 'AWS_RAW_EXPORT', str(uuid.uuid4()),
            status=BIOrganizationStatuses.RUNNING, last_status_error='error')
        body = {'status': 'SUCCESS'}
        code, res = self.client.bi_update(bi['id'], body)
        self.assertEqual(code, 200)
        self.assertEqual(res['status'], 'SUCCESS')
        self.assertEqual(res['last_status_error'], None)

    def test_update_azure_bi(self):
        meta = {
            'container': 'container',
            'connection_string': 'test;AccountName=test;test'
        }
        ret, res = self.client.bi_create(
            self.org_id_1, 'AZURE_RAW_EXPORT', 'azure', **meta)
        self.assertEqual(201, ret)
        self.assertNotIn('connection_string', res['meta'])

        account_name = 'storage_acc'
        meta = {
            'container': 'container',
            'connection_string': 'test;AccountName={};test'.format(account_name)
        }
        ret, res = self.client.bi_update(res['id'], params={'meta': meta})
        self.assertEqual(200, ret)
        self.assertEqual(res['meta']['storage_account'], account_name)
        self.assertIn('connection_string', res['meta'])

        patch('rest_api.rest_api_server.handlers.v2.organization_bis.'
              'BIAsyncItemHandler.check_cluster_secret',
              return_value=False).start()
        ret, res = self.client.bi_update(res['id'], params={'meta': meta})
        self.assertEqual(200, ret)
        self.assertEqual(res['meta']['storage_account'], account_name)
        self.assertNotIn('connection_string', res['meta'])

    def test_bis_methods(self):
        code, _ = self.client.patch(self.client.bi_url(
            org_id=self.org_id_1), {})
        self.assertEqual(code, 405)
        code, _ = self.client.delete(self.client.bi_url(org_id=self.org_id_1))
        self.assertEqual(code, 405)
        code, _ = self.client.post(self.client.bi_url(), {})
        self.assertEqual(code, 405)
        code, _ = self.client.patch(self.client.bi_url(), {})
        self.assertEqual(code, 405)
        code, _ = self.client.delete(self.client.bi_url())
        self.assertEqual(code, 405)
        code, _ = self.client.post(self.client.bi_url(
            id_=self.org_bi_1['id']), {})
        self.assertEqual(code, 405)
