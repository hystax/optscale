import os
from datetime import datetime, timedelta
from unittest.mock import patch, ANY

from rest_api_server.models.enums import ImportStates
from rest_api_server.models.db_factory import DBFactory, DBType
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.models import ReportImport
from rest_api_server.tests.unittests.test_api_base import TestApiBase
from freezegun import freeze_time


class TestReportImportsApi(TestApiBase):

    def setUp(self, version='v2'):
        os.environ['ASYNC_TEST_TIMEOUT'] = '20'
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "organization"})
        self.org_id = self.org['id']
        valid_aws_cloud_acc = {
            'name': 'my cloud_acc',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.user_id_1 = self.gen_id()
        _, self.employee_1 = self.client.employee_create(
            self.org_id, {'name': 'Eliot Alderson', 'auth_user_id': self.user_id_1})

        patch('rest_api_server.controllers.report_import.ReportImportBaseController.create').start()
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, valid_aws_cloud_acc, auth_user_id=self.user_id_1)
        self.cloud_acc_id = self.cloud_acc['id']

        self.user_id_2 = self.gen_id()
        _, self.employee_2 = self.client.employee_create(
            self.org_id,
            {'name': 'Eliot Alderson_2', 'auth_user_id': self.user_id_2})
        valid_aws_cloud_acc['name'] = 'new name'
        _, cloud_acc2 = self.create_cloud_account(
            self.org_id, valid_aws_cloud_acc, auth_user_id=self.user_id_2)
        self.cloud_acc2_id = cloud_acc2['id']
        patch('rest_api_server.controllers.report_import.'
              'ReportImportBaseController.publish_task').start()
        self.p_get_user_info.return_value = {}

    def _create_import_object(self, state=ImportStates.SCHEDULED,
                              cloud_acc_id=None, is_manual=False,
                              is_recalculation=False):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        cloud_acc_id = cloud_acc_id if cloud_acc_id else self.cloud_acc_id
        _import = ReportImport(
            created_at=datetime.utcnow(),
            deleted_at=0,
            cloud_account_id=cloud_acc_id,
            state=state,
            is_recalculation=is_recalculation
        )
        if is_manual:
            _import.import_file = "Test_File_Info"
        session.add(_import)
        session.commit()
        return _import.id

    def test_report_update(self):
        import_id = self._create_import_object()
        code, _import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)
        self.assertEqual(_import['state'], ImportStates.SCHEDULED.value)
        self.assertEqual(_import['state_reason'], None)
        self.assertEqual(_import['updated_at'], 0)

        update = {
            'state': ImportStates.FAILED.value,
            'state_reason': 'test' * 200,
        }
        now = datetime.utcnow()
        with freeze_time(now):
            code, _import = self.client.report_import_update(import_id, update)
        self.assertEqual(code, 200)
        self.assertEqual(_import['state'], ImportStates.FAILED.value)
        self.assertEqual(_import['state_reason'], 'test' * 200)
        self.assertEqual(_import['updated_at'], int(now.timestamp()))

    def test_report_send_event(self):
        import_id_initial_failed = self._create_import_object()
        import_id_initial_success = self._create_import_object()
        import_id_second = self._create_import_object()
        success_update = {
            'state': ImportStates.COMPLETED.value,
        }
        failed_update = {
            'state': ImportStates.FAILED.value,
            'state_reason': "report_import failed"
        }
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _import = self.client.report_import_update(
            import_id_initial_failed, failed_update)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            ANY, _import['id'], 'report_import',
            'report_import_failed', {
                'object_name': self.cloud_acc['name'],
                'cloud_account_id': self.cloud_acc['id'],
                'level': 'ERROR',
                'error_reason': ANY
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _import = self.client.report_import_update(
            import_id_initial_success, success_update)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            ANY, _import['id'], 'report_import',
            'report_import_completed', {
                'object_name': self.cloud_acc['name'],
                'cloud_account_id': self.cloud_acc['id'],
                'level': 'INFO'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _import = self.client.report_import_update(
            import_id_second, success_update)
        self.assertEqual(code, 200)
        self.assertEqual(p_publish_activities.called, False)
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        import_manual_id = self._create_import_object(is_manual=True)
        code, _import = self.client.report_import_update(
            import_manual_id, failed_update)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            ANY, _import['id'], 'report_import',
            'report_import_failed', {
                'object_name': self.cloud_acc['name'],
                'cloud_account_id': self.cloud_acc['id'],
                'level': 'ERROR',
                'error_reason': ANY
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_update_immutables(self):
        import_id = self._create_import_object()
        code, _import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)

        for param in ['deleted_at', 'id', 'created_at', 'cloud_account_id',
                      'import_file']:
            update = {param: 1}
            code, ret = self.client.report_import_update(import_id, update)
            self.assertEqual(code, 400)
            self.assertEqual(ret['error']['reason'],
                             'Parameter "{}" is immutable'.format(param))

    def test_update_invalid_params(self):
        import_id = self._create_import_object()
        code, _import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)

        for value in ['', 1, 'str', None]:
            update = {'state': value}
            code, ret = self.client.report_import_update(import_id, update)
            self.assertEqual(code, 400)

        update = {'state_reason': 1}
        code, ret = self.client.report_import_update(import_id, update)
        self.assertEqual(code, 400)

    def test_report_import_list(self):
        import_id1 = self._create_import_object()
        import_id2 = self._create_import_object(state=ImportStates.COMPLETED)
        import_id3 = self._create_import_object(state=ImportStates.IN_PROGRESS)
        import_id4 = self._create_import_object(state=ImportStates.FAILED)
        import_id5 = self._create_import_object(state=ImportStates.FAILED,
                                                cloud_acc_id=self.cloud_acc2_id)

        code, res = self.client.report_import_list(self.cloud_acc_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['report_imports']), 3)
        for import_ret in res['report_imports']:
            self.assertIn(import_ret['id'],
                          [import_id1, import_id3, import_id4])

        code, res = self.client.report_import_list(self.cloud_acc_id,
                                                   show_completed=True)
        self.assertEqual(code, 200)
        self.assertEqual(len(res['report_imports']), 4)
        for import_ret in res['report_imports']:
            self.assertIn(import_ret['id'],
                          [import_id1, import_id2, import_id3, import_id4])

    def test_report_imports_for_deleted_cloud_acc(self):
        import_id = self._create_import_object()
        self.client.cloud_account_delete(self.cloud_acc_id)
        code, _ = self.client.report_import_get(import_id)
        self.assertEqual(code, 404)
        code, _ = self.client.report_import_list(self.cloud_acc_id)
        self.assertEqual(code, 404)

    def test_edit_report_import_failed_recalculation_event(self):
        import_id = self._create_import_object(is_recalculation=True)
        code, report_import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)
        self.assertTrue(report_import['is_recalculation'])
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        failed_cause = "report_import failed"
        failed_update = {
            'state': ImportStates.FAILED.value,
            'state_reason': failed_cause
        }
        code, failed_updated_report = self.client.report_import_update(
            import_id, failed_update)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, ANY, 'report_import',
            'recalculation_failed', {
                'object_name': self.cloud_acc['name'],
                'cloud_account_id': self.cloud_acc['id'],
                'level': 'ERROR',
                'error_reason': failed_cause
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_edit_report_import_completed_recalculation_event(self):
        import_id = self._create_import_object(is_recalculation=True)
        code, report_import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)
        self.assertTrue(report_import['is_recalculation'])
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        completed_update = {
            'state': ImportStates.COMPLETED.value
        }
        code, failed_updated_report = self.client.report_import_update(
            import_id, completed_update)
        self.assertEqual(code, 200)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, ANY, 'report_import',
            'recalculation_completed', {
                'object_name': self.cloud_acc['name'],
                'cloud_account_id': self.cloud_acc['id'],
                'level': 'INFO'
            })
        p_publish_activities.assert_called_once_with(
            *activity_param_tuples, add_token=True
        )

    def test_report_schedule_checklist(self):
        success_update = {
            'state': ImportStates.COMPLETED.value,
        }
        failed_update = {
            'state': ImportStates.FAILED.value,
            'state_reason': "report_import failed"
        }
        p_schedule_checklist = patch(
            'rest_api_server.controllers.checklist.'
            'ChecklistController.schedule_next_run'
        ).start()

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object()
        code, _ = self.client.report_import_update(import_id, failed_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_not_called()

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object()
        code, _ = self.client.report_import_update(import_id, success_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_called_once_with(self.org_id)

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object()
        code, _ = self.client.report_import_update(import_id, success_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_not_called()

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object(
            is_manual=True, cloud_acc_id=self.cloud_acc2_id)
        code, _ = self.client.report_import_update(import_id, failed_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_not_called()

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object(
            is_manual=True, cloud_acc_id=self.cloud_acc2_id)
        code, _ = self.client.report_import_update(import_id, success_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_called_once_with(self.org_id)

        p_schedule_checklist.reset_mock()
        import_id = self._create_import_object(
            is_manual=True, cloud_acc_id=self.cloud_acc2_id)
        code, _ = self.client.report_import_update(import_id, success_update)
        self.assertEqual(code, 200)
        p_schedule_checklist.assert_not_called()

    def test_show_active(self):
        import_id = self._create_import_object(state=ImportStates.IN_PROGRESS)
        code, _import = self.client.report_import_get(import_id)
        self.assertEqual(code, 200)
        self.assertEqual(_import['state'], ImportStates.IN_PROGRESS.value)
        code, resp = self.client.report_import_list(
            self.cloud_acc_id, show_active=True)
        self.assertEqual(code, 200)
        self.assertEqual(resp['report_imports'], [])

        self.client.report_import_update(import_id, {})
        code, resp = self.client.report_import_list(
            self.cloud_acc_id, show_active=True)
        self.assertEqual(code, 200)
        imports = resp['report_imports']
        self.assertEqual(len(imports), 1)
        self.assertEqual(imports[0]['id'], import_id)

        with freeze_time(datetime.utcnow() + timedelta(minutes=31)):
            code, resp = self.client.report_import_list(
                self.cloud_acc_id, show_active=True)
        self.assertEqual(code, 200)
        self.assertEqual(resp['report_imports'], [])
