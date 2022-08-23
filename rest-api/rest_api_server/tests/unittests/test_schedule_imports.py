import uuid
from datetime import datetime
from unittest.mock import patch

from rest_api_server.models.db_factory import DBFactory, DBType
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.models import CloudAccount
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api_server.utils import MAX_32_INT, encode_config


class TestScheduleImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        patch('rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()

    def test_schedule_imports_without_cloud_acc(self):
        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 0)

    def test_schedule_imports_wrong_period(self):
        code, ret = self.client.schedule_import('a')
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'period should be integer')

        code, ret = self.client.schedule_import(-1)
        self.assertEqual(code, 400)
        self.assertEqual(
            ret['error']['reason'],
            'Value of "period" should be between 0 and %s' % MAX_32_INT
        )

        code, ret = self.client.schedule_import(None)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'period is not provided')

    def test_schedule_unexpected(self):
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'period': 1, 'str': 1})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'Unexpected parameters: str')

    def _create_cloud_acc_object(self, import_period, auto_import=True,
                                 config={}, org_id=None):
        if org_id is None:
            org_id = self.org_id
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        cloud_acc = CloudAccount(
            name=str(uuid.uuid4()),
            created_at=int(datetime.utcnow().timestamp()),
            deleted_at=0,
            config=encode_config(config),
            organization_id=org_id,
            auto_import=auto_import,
            import_period=import_period,
        )
        session.add(cloud_acc)
        session.commit()
        return cloud_acc.id

    def test_schedule_imports(self):
        cloud_acc1 = self._create_cloud_acc_object(import_period=0)
        cloud_acc2 = self._create_cloud_acc_object(import_period=6)
        cloud_acc3 = self._create_cloud_acc_object(import_period=0)

        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 2)
        for _import in ret['report_imports']:
            self.assertIn(_import['cloud_account_id'], [cloud_acc1, cloud_acc3])

        cloud_acc4 = self._create_cloud_acc_object(
            import_period=6, auto_import=False)
        code, ret = self.client.schedule_import(6)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)
        self.assertEqual(
            ret['report_imports'][0]['cloud_account_id'], cloud_acc2)

    def test_dont_schedule_for_linked_aws(self):
        main_cloud_acc = self._create_cloud_acc_object(import_period=0)
        linked_cloud_acc = self._create_cloud_acc_object(
            import_period=0, config={"linked": True})

        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)
        self.assertEqual(ret['report_imports'][0]['cloud_account_id'],
                         main_cloud_acc)

    def test_schedule_imports_for_deleted_org(self):
        code, org2 = self.client.organization_create({'name': 'org2'})
        self.assertEqual(code, 201)
        ca1 = self._create_cloud_acc_object(import_period=0, org_id=org2['id'])
        ca2 = self._create_cloud_acc_object(import_period=0, org_id=self.org_id)

        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 2)
        self.delete_organization(org2['id'])

        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)
        self.assertEqual(ret['report_imports'][0]['cloud_account_id'], ca2)
