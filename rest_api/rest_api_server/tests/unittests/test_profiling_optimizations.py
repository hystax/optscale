import uuid
from rest_api.rest_api_server.tests.unittests.test_profiling_base import TestProfilingBase
from unittest.mock import patch
from datetime import datetime
from rest_api.rest_api_server.models.db_factory import DBFactory, DBType
from rest_api.rest_api_server.models.db_base import BaseDB
from rest_api.rest_api_server.models.models import Checklist


class TestProfilingOptimizationsApi(TestProfilingBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create({'name': "organization"})
        self.valid_task = {
            'name': 'My test project',
            'key': 'test_project'
        }
        auth_user = str(uuid.uuid4())
        _, self.employee = self.client.employee_create(
            self.org['id'], {'name': 'name1', 'auth_user_id': auth_user})
        patch('rest_api.rest_api_server.controllers.base.BaseController.'
              'get_user_id', return_value=auth_user).start()

    @staticmethod
    def add_checklist(organization_id, date_ts):
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        session = BaseDB.session(engine)()
        record = Checklist(
            organization_id=organization_id,
            last_run=date_ts,
            last_completed=date_ts
        )
        session.add(record)
        session.commit()
        return record

    def add_recommendations(self, checklist, module, data=None, options=None,
                            error=None):
        self.mongo_client.restapi.checklists.insert_one({
            'created_at': checklist.last_completed,
            'organization_id': checklist.organization_id,
            'module': module,
            'data': data or [],
            'options': options,
            'error': error,
        })

    def test_task_optimizations_invalid_params(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        code, resp = self.client.task_optimizations_get(
            str(uuid.uuid4()), task['id'])
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

        code, resp = self.client.task_optimizations_get(
            self.org['id'], str(uuid.uuid4()))
        self.assertEqual(code, 404)
        self.verify_error_code(resp, 'OE0002')

    def test_task_optimizations_empty(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'total_saving': 0, 'optimizations': {}, 'total_count': 0,
            'dismissed_optimizations': {}, 'excluded_optimizations': {}})

    def test_task_recommendations(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        dt = int(datetime.utcnow().timestamp())
        checklist = self.add_checklist(self.org['id'], dt)
        ca_id = str(uuid.uuid4())
        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 1},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '2', 'saving': 2},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '3', 'saving': 3},
        ]
        f_options = {'days': 7, 'excl': []}
        self.add_recommendations(checklist, 'first', data, options=f_options)

        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 8},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '2', 'saving': 8},
        ]
        self.add_recommendations(checklist, 'second', data)

        self._create_run(self.org['id'], task['id'], ['4'],
                         start=dt - 2, finish=dt)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'total_saving': 0,
            'optimizations': {
                'first': {
                    'count': 0,
                    'items': [],
                    'options': {'days': 7, 'excl': []},
                    'saving': 0,
                    'cloud_accounts': []
                },
                'second': {
                    'count': 0,
                    'items': [],
                    'options': {},
                    'saving': 0,
                    'cloud_accounts': []
                }
            },
            'dismissed_optimizations': {},
            'excluded_optimizations': {},
            'total_count': 0})

        self._create_run(self.org['id'], task['id'], ['1'],
                         start=dt - 2, finish=dt)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 9)
        self.assertEqual(resp['total_count'], 2)
        optimizations = resp['optimizations']
        self.assertEqual(len(optimizations), 2)
        self.assertEqual(optimizations['first']['count'], 1)
        self.assertEqual(optimizations['first']['saving'], 1)
        self.assertEqual(optimizations['first']['options'], f_options)
        self.assertEqual(len(optimizations['first']['items']), 1)
        self.assertEqual(optimizations['second']['count'], 1)
        self.assertEqual(optimizations['second']['saving'], 8)
        self.assertEqual(optimizations['second']['options'], {})
        self.assertEqual(len(optimizations['second']['items']), 1)

        self._create_run(self.org['id'], task['id'], ['3'],
                         start=dt - 2, finish=dt)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 12)
        self.assertEqual(resp['total_count'], 3)
        optimizations = resp['optimizations']
        self.assertEqual(len(optimizations), 2)
        self.assertEqual(optimizations['first']['count'], 2)
        self.assertEqual(optimizations['first']['saving'], 4)
        self.assertEqual(len(optimizations['first']['items']), 2)
        self.assertEqual(optimizations['second']['count'], 1)
        self.assertEqual(optimizations['second']['saving'], 8)
        self.assertEqual(len(optimizations['second']['items']), 1)

    def test_task_recommendations_dismissed(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        dt = int(datetime.utcnow().timestamp())
        checklist = self.add_checklist(self.org['id'], dt)
        ca_id = str(uuid.uuid4())
        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 1, 'is_dismissed': True},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '2', 'saving': 2, 'is_dismissed': True},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '3', 'saving': 3, 'is_dismissed': True},
        ]
        f_options = {'days': 7, 'excl': []}
        self.add_recommendations(checklist, 'first', data, options=f_options)

        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 8, 'is_dismissed': True},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '2', 'saving': 8, 'is_dismissed': True},
        ]
        self.add_recommendations(checklist, 'second', data)

        self._create_run(self.org['id'], task['id'], ['1'],
                         start=dt - 2, finish=dt)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 0)
        self.assertEqual(resp['total_count'], 0)
        optimizations = resp['optimizations']
        self.assertEqual(len(optimizations), 2)
        self.assertEqual(optimizations['first']['count'], 0)
        self.assertEqual(optimizations['first']['saving'], 0)
        self.assertEqual(optimizations['first']['options'], f_options)
        self.assertEqual(len(optimizations['first']['items']), 0)
        self.assertEqual(optimizations['second']['count'], 0)
        self.assertEqual(optimizations['second']['saving'], 0)
        self.assertEqual(optimizations['second']['options'], {})
        self.assertEqual(len(optimizations['second']['items']), 0)
        dismissed = resp['dismissed_optimizations']
        self.assertEqual(len(dismissed), 2)
        self.assertEqual(dismissed['first']['count'], 1)
        self.assertEqual(dismissed['first']['saving'], 1)
        self.assertEqual(dismissed['second']['count'], 1)
        self.assertEqual(dismissed['second']['saving'], 8)

        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'], status='dismissed', types=['first'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 0)
        self.assertEqual(resp['total_count'], 0)
        dismissed = resp['dismissed_optimizations']
        self.assertEqual(len(dismissed), 2)
        self.assertEqual(dismissed['first']['count'], 1)
        self.assertEqual(dismissed['first']['saving'], 1)
        self.assertEqual(len(dismissed['first']['items']), 1)

    def test_task_optimizations_threshold(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        dt = int(datetime.utcnow().timestamp())
        checklist = self.add_checklist(self.org['id'], dt)
        ca_id = str(uuid.uuid4())
        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 1},
        ]
        self.add_recommendations(checklist, 'first', data)
        start = dt - 7 * 86400 - 1
        self._create_run(self.org['id'], task['id'], ['1'],
                         start=start, finish=start + 1)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp, {
            'total_saving': 0,
            'optimizations': {
                'first': {
                    'count': 0, 'items': [], 'options': {}, 'saving': 0,
                    'cloud_accounts': []
                }
            },
            'dismissed_optimizations': {},
            'excluded_optimizations': {},
            'total_count': 0
        })

        start = dt - 7 * 86400 + 5
        self._create_run(self.org['id'], task['id'], ['1'],
                         start=start, finish=start + 1)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 1)
        self.assertEqual(resp['total_count'], 1)
        optimizations = resp['optimizations']
        self.assertEqual(len(optimizations), 1)
        self.assertEqual(optimizations['first']['count'], 1)
        self.assertEqual(optimizations['first']['saving'], 1)
        self.assertEqual(len(optimizations['first']['items']), 1)

    def test_task_optimizations_excluded_and_dismissed(self):
        code, task = self.client.task_create(
            self.org['id'], self.valid_task)
        self.assertEqual(code, 201)
        dt = int(datetime.utcnow().timestamp())
        checklist = self.add_checklist(self.org['id'], dt)
        ca_id = str(uuid.uuid4())
        data = [
            {'cloud_account_id': ca_id, 'cloud_resource_id': '1', 'saving': 1},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '2', 'saving': 2,
             'is_excluded': True},
            {'cloud_account_id': ca_id, 'cloud_resource_id': '3', 'saving': 3,
             'is_dismissed': True},
        ]
        self.add_recommendations(checklist, 'first', data)
        self._create_run(self.org['id'], task['id'], ['1'],
                         start=dt - 1, finish=dt)
        code, resp = self.client.task_optimizations_get(
            self.org['id'], task['id'])
        self.assertEqual(code, 200)
        self.assertEqual(resp['total_saving'], 1)
        optimizations = resp['optimizations']
        self.assertEqual(len(optimizations), 1)
        self.assertEqual(len(optimizations['first']['items']), 1)
        self.assertEqual(
            optimizations['first']['items'][0]['cloud_resource_id'], '1')
