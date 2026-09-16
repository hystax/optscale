import uuid
from datetime import datetime, timedelta
from unittest.mock import patch
from freezegun import freeze_time

from rest_api.rest_api_server.controllers.report_import import (
    DEFAULT_QUEUE_MESSAGE_EXPIRATION_SECONDS,
    DEFAULT_NOT_PROCESSED_REPORT_THRESHOLD_SECONDS,
)
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import CloudAccount
from rest_api.rest_api_server.models.enums import (
    CloudTypes
)
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from rest_api.rest_api_server.utils import MAX_32_INT, encode_config
import tools.optscale_time as opttime


class TestScheduleImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        _, self.org2 = self.client.organization_create(
            {'name': "organization2"})
        self.org_id2 = self.org2['id']
        patch('rest_api.rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        patch(
            'optscale_client.config_client.client.Client.report_imports_setting',
            return_value={
                'not_processed_threshold_secs': DEFAULT_NOT_PROCESSED_REPORT_THRESHOLD_SECONDS,
                'message_expiration_secs': DEFAULT_QUEUE_MESSAGE_EXPIRATION_SECONDS,
            }
        ).start()

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

    def test_schedule_imports_argument_required(self):
        code, ret = self.client.schedule_import(None)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'period, organization_id or cloud_account_id is required')

    def test_schedule_unexpected(self):
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'str': 1, 'cloud_account_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'Unexpected parameters: str')

    def test_schedule_exclusive_period(self):
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'period': 1, 'cloud_account_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "period should be used exclusively")

    def test_schedule_invalid_priority(self):
        for i in [-1, 0, 99]:
            code, ret = self.client.post(self.client.schedule_import_url(),
                                         {'cloud_account_id': str(uuid.uuid4()), 'priority': i})
            self.assertEqual(code, 400)
            self.assertEqual(ret['error']['reason'],
                             "Priority should be 1...9")

    def _create_cloud_acc_object(self, import_period=None, auto_import=True,
                                 config=None, org_id=None, cloud_type=CloudTypes.AWS_CNR):
        if config is None:
            config = dict()
        if org_id is None:
            org_id = self.org_id
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        cloud_acc = CloudAccount(
            name=str(uuid.uuid4()),
            created_at=opttime.utcnow_timestamp(),
            deleted_at=0,
            config=encode_config(config),
            organization_id=org_id,
            auto_import=auto_import,
            import_period=import_period,
            type=cloud_type
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

    def test_schedule_imports_org_id(self):
        self._create_cloud_acc_object(org_id=self.org_id)
        self._create_cloud_acc_object(org_id=self.org_id)
        self._create_cloud_acc_object(org_id=self.org_id2)
        code, ret = self.client.schedule_import(organization_id=self.org_id)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 2)

    def test_schedule_imports_org_id_specify_cloud(self):
        self._create_cloud_acc_object(org_id=self.org_id)
        self._create_cloud_acc_object(org_id=self.org_id)
        self._create_cloud_acc_object(org_id=self.org_id, cloud_type=CloudTypes.GCP_CNR)
        code, ret = self.client.schedule_import(organization_id=self.org_id,
                                                cloud_account_type='gcp_cnr')
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)

    def test_schedule_imports_invalid_cloud_type(self):
        self._create_cloud_acc_object(org_id=self.org_id)
        code, ret = self.client.schedule_import(organization_id=self.org_id,
                                                cloud_account_type='invalid')
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         "invalid cloud account type: invalid")

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
        for i in ret['report_imports']:
            self.client.report_import_update(i['id'], {'state': 'failed'})
        self.delete_organization(org2['id'])

        code, ret = self.client.schedule_import(0)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)
        self.assertEqual(ret['report_imports'][0]['cloud_account_id'], ca2)

    def test_schedule_org_id_with_ca_id(self):
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'organization_id': self.org_id, 'cloud_account_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'Cannot use organization_id with cloud_account_id')
        self.assertEqual(ret['error']['error_code'],
                         'OE0528')

    def test_schedule_org_account_type_without_org_id(self):
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'cloud_account_type': CloudTypes.AWS_CNR.value,
                                      'cloud_account_id': str(uuid.uuid4())})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['reason'],
                         'Cannot use cloud_account_type without organization_id')
        self.assertEqual(ret['error']['error_code'],
                         'OE0529')

    def test_create_scheduled_duplicate(self):
        code, org2 = self.client.organization_create({'name': 'org2'})
        self.assertEqual(code, 201)
        self._create_cloud_acc_object(import_period=0, org_id=org2['id'])
        code, ret = self.client.schedule_import(0)

        self.assertEqual(len(ret['report_imports']), 1)
        code, ret = self.client.schedule_import(0)
        self.assertEqual(len(ret['report_imports']), 0)
        with freeze_time(opttime.utcnow() + timedelta(hours=3)):
            code, resp = self.client.schedule_import(0)
            self.assertEqual(len(resp['report_imports']), 1)
            code, ret = self.client.schedule_import(0)
            self.assertEqual(len(ret['report_imports']), 0)
            for r in resp['report_imports']:
                self.client.report_import_update(r['id'], {'state': 'completed'})
            code, ret = self.client.schedule_import(0)
            self.assertEqual(len(ret['report_imports']), 1)

    def test_import_from_negative(self):
        code, ret = self.client.schedule_import(0, import_from=1000000)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0561')
        code, ret = self.client.schedule_import(0, import_to=1000000)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0561')
        code, ret = self.client.schedule_import(0, reimport=True)
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0561')

    def test_import_range_param_validation(self):
        ca_id = self._create_cloud_acc_object()
        code, ret = self.client.schedule_import(cloud_account_id=ca_id,
                                                import_to='xxx')
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0223')

        code, ret = self.client.schedule_import(cloud_account_id=ca_id,
                                                import_to='xxx')
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0223')

        code, ret = self.client.schedule_import(cloud_account_id=ca_id,
                                                reimport='xxx')
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0226')

    def test_reimport_not_boolean(self):
        ca_id = self._create_cloud_acc_object()
        code, ret = self.client.post(self.client.schedule_import_url(),
                                     {'cloud_account_id': ca_id,
                                      'reimport': 'yes'})
        self.assertEqual(code, 400)
        self.assertEqual(ret['error']['error_code'], 'OE0226')

    def test_schedule_with_import_params(self):
        ca_id = self._create_cloud_acc_object()
        ts = int(datetime(2026, 3, 1).timestamp())
        code, ret = self.client.schedule_import(
            cloud_account_id=ca_id,
            import_from=ts,
            import_to=ts + 86400 * 30,
            reimport=True)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)
        self.assertEqual(ret['report_imports'][0]['cloud_account_id'], ca_id)

    def test_import_from_greater_than_import_to(self):
        ca_id = self._create_cloud_acc_object()
        ts = int(datetime(2026, 3, 15).timestamp())
        code, ret = self.client.schedule_import(
            cloud_account_id=ca_id,
            import_from=ts,
            import_to=ts - 86400)
        self.assertEqual(code, 400)
        self.verify_error_code(ret, 'OE0446')

    def test_schedule_reimport_only(self):
        ca_id = self._create_cloud_acc_object()
        code, ret = self.client.schedule_import(
            cloud_account_id=ca_id, reimport=True)
        self.assertEqual(code, 201)
        self.assertEqual(len(ret['report_imports']), 1)

    def test_create_active_duplicate(self):
        code, org2 = self.client.organization_create({'name': 'org2'})
        self._create_cloud_acc_object(import_period=0, org_id=org2['id'])
        self.assertEqual(code, 201)
        code, ret = self.client.schedule_import(0)
        imp = ret['report_imports'][0]
        self.client.report_import_update(imp['id'], {'state': 'in_progress'})
        code, ret = self.client.schedule_import(0)
        self.assertEqual(len(ret['report_imports']), 0)
        with freeze_time(opttime.utcnow() + timedelta(hours=10)):
            self.client.report_import_update(imp['id'], {})
            code, ret = self.client.schedule_import(0)
            self.assertEqual(len(ret['report_imports']), 0)
        with freeze_time(opttime.utcnow() + timedelta(hours=10, minutes=31)):
            code, ret = self.client.schedule_import(0)
            self.assertEqual(len(ret['report_imports']), 1)
