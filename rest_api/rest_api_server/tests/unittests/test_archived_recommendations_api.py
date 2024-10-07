import uuid
from datetime import datetime
from unittest.mock import patch

from rest_api.rest_api_server.handlers.v2.archived_recommendations import (
    ArchivedRecommendationsCountAsyncHandler)
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase

DAY_TS = 24 * 60 * 60
TWO_WEEK_TS = 14 * DAY_TS
DEFAULT_PRECISION = ArchivedRecommendationsCountAsyncHandler.DEFAULT_PRECISION
SUPPORTED_PRECISIONS = ArchivedRecommendationsCountAsyncHandler.SUPPORTED_PRECISIONS


class TestArchivedRecommendationsBase(TestApiBase):

    def setUp(self, version='v2'):
        super().setUp(version)
        _, self.org = self.client.organization_create(
            {'name': "partner"})
        self.org_id = self.org['id']
        patch('rest_api.rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()

        creds = {
            'name': 'aws',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'name', 'auth_user_id': self.user_id})
        _, self.cloud_acc = self.create_cloud_account(
            self.org_id, creds, auth_user_id=self.user_id)

        self.end_date = int(datetime.utcnow().timestamp())
        self.start_date = self.end_date - TWO_WEEK_TS
        self.instance = {
            'cloud_resource_id': 'i-9323123124',
            'resource_name': 'my test instance',
            'resource_id': '58bef498-9f06-4c0f-aac0-312b22fcb9ee',
            'cloud_account_id': self.cloud_acc['id'],
            'cloud_account_name': self.cloud_acc['name'],
            'cloud_type': self.cloud_acc['type'],
            'total_cost': 20,
            'first_seen': 1600077735,
            'last_seen': 1600078565,
            'saving': 150
        }
        self.instance2 = {
            'cloud_resource_id': 'i-8212012013',
            'resource_name': 'my another test instance',
            'resource_id': 'a4f2adbb-aae2-4355-b933-cc6730a2edca',
            'cloud_account_id': self.cloud_acc['id'],
            'cloud_account_name': self.cloud_acc['name'],
            'cloud_type': self.cloud_acc['type'],
            'total_cost': 10,
            'first_seen': 1600077735,
            'last_seen': 1600078565,
            'saving': 140
        }

    def _add_archive_recommendation(self, organization_id, module, reason,
                                    data, archived_at=None):
        if not archived_at:
            archived_at = int(datetime.utcnow().timestamp())
        record = {
            'module': module,
            'organization_id': organization_id,
            'archived_at': archived_at,
            'reason': reason,
            **data
        }
        self.archived_recommendations_collection.insert_one(record)
        return record


class TestBreakdownArchivedRecommendationsApi(TestArchivedRecommendationsBase):
    def test_breakdown_nonexistent_organization(self):
        code, res = self.client.breakdown_archived_recommendations_get(
            str(uuid.uuid4()), start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 404)

    def test_breakdown_empty(self):
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertIsNone(res.get('limit'))
        self.assertEqual(res.get('breakdown'), [])

    def test_breakdown_empty_limit(self):
        limit = 1
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params={'limit': limit})
        self.assertEqual(code, 200)
        self.assertEqual(res.get('limit'), limit)
        self.assertEqual(res.get('breakdown'), [])

    def test_breakdown_unexpected_parameters(self):
        for params in [
            {'key': 'value'},
            {'archived_at': self.start_date}
        ]:
            code, res = self.client.breakdown_archived_recommendations_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date,
                params=params)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_breakdown_another_org_data(self):
        self._add_archive_recommendation(
            str(uuid.uuid4()), 'module', 'reason', self.instance,
            self.start_date + DAY_TS)
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('breakdown'), [])

    def test_breakdown_incorrect_dates_range(self):
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.end_date, end_date=self.start_date,
            params={'key': 'value'})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0446')

    def test_breakdown_incorrect_dates(self):
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=-1, end_date=self.start_date)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_breakdown_dates(self):
        params = {
            'organization_id': self.org_id,
            'module': 'module',
            'reason': 'reason',
            'data': self.instance
        }

        for val in [
            (self.end_date, 0),
            (self.start_date - DAY_TS, 0),
            (self.end_date + DAY_TS, 0),
            (self.start_date, 1),  # only lower bound in range
        ]:
            archived_at, records_count = val
            self._add_archive_recommendation(**params, archived_at=archived_at)
            code, res = self.client.breakdown_archived_recommendations_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date)
            self.assertEqual(code, 200)
            self.assertEqual(len(res.get('breakdown')), records_count)

    def test_breakdown_limit(self):
        params = {
            'organization_id': self.org_id,
            'module': 'module',
            'reason': 'reason',
            'data': self.instance
        }
        records_count = 10
        for i in range(1, records_count + 1):
            self._add_archive_recommendation(
                **params, archived_at=self.start_date + DAY_TS * i)

        for val in [
            (1, 1),
            (5, 5),
            (records_count * 2, records_count)
        ]:
            limit, expected = val
            params = {'limit': limit}
            code, res = self.client.breakdown_archived_recommendations_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date,
                params=params)
            self.assertEqual(code, 200)
            self.assertEqual(len(res['breakdown']), expected)

        params = {'limit': 0}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_breakdown(self):
        count_per_reason = 5
        insertions = [
            ('module_1', ['reason_1_1', 'reason_1_2']),
            ('module_2', ['reason_2_1']),
        ]
        for val in insertions:
            module, reasons = val
            for reason in reasons:
                for i in range(1, count_per_reason + 1):
                    self._add_archive_recommendation(
                        self.org_id, module, reason, self.instance,
                        self.start_date + DAY_TS * i)

        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         sum(list(map(lambda x: len(x[1]), insertions))) * count_per_reason)
        self.assertTrue(all(map(lambda x: x['count'] == 1, res['breakdown'])))
        self.assertEqual(res['start_date'], self.start_date)
        self.assertEqual(res['end_date'], self.end_date)
        for k in ['count', 'module', 'reason', 'archived_at']:
            self.assertIsNotNone(res['breakdown'][0].get(k))

        module, reasons = insertions[0]
        params = {'type': module}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         len(reasons) * count_per_reason)

        params = {'reason': reasons[0]}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         count_per_reason)
        for rec in res['breakdown']:
            self.assertEqual(rec['reason'], params['reason'])

        params = {'reason': reasons}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         len(reasons) * count_per_reason)
        for rec in res['breakdown']:
            self.assertTrue(rec['reason'] in params['reason'])

        params = {'type': module, 'reason': reasons}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         len(reasons) * count_per_reason)
        for rec in res['breakdown']:
            self.assertTrue(rec['reason'] in params['reason'])
            self.assertEqual(rec['module'], params['type'])

        module_1, reasons_1 = insertions[0]
        module_2, reasons_2 = insertions[1]
        params = {'type': module_1, 'reason': reasons_2}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])), 0)

    def test_breakdown_breakdown(self):
        count_per_reason = 5
        insertions = [
            ('module_1', ['reason_1_1', 'reason_1_2']),
            ('module_2', ['reason_2_1']),
        ]
        for val in insertions:
            module, reasons = val
            for reason in reasons:
                for i in range(1, count_per_reason + 1):
                    self._add_archive_recommendation(
                        self.org_id, module, reason, self.instance,
                        self.start_date + DAY_TS)

        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(len(res.get('breakdown', [])),
                         sum(list(map(lambda x: len(x[1]), insertions))))
        self.assertTrue(all(map(lambda x: x['count'] == count_per_reason, res['breakdown'])))


class TestArchivedRecommendationsDetailsApi(TestArchivedRecommendationsBase):
    def setUp(self, version='v2'):
        super().setUp(version=version)
        patch(
            'rest_api.rest_api_server.controllers.archived_recommendation.'
            'ArchivedRecommendationsDetailsController._build_pipeline',
            wraps=self.patched_build_pipeline).start()

    def patched_build_pipeline(self, match_filter, limit=None, start_from=0):
        # mongo mock is unable to slice using $count as limit so hardcoded it
        # to good enough value
        if limit is None:
            limit = 2 ^ 32 - 1
        res = [
            {'$match': {'$and': match_filter}},
            {'$project': {
                '_id': 0,
            }},
            {'$group': {
                '_id': None,
                'items': {'$push': '$$ROOT'},
                'count': {'$sum': 1}
            }},
            {"$project": {
                '_id': 0,
                "items": {"$slice": ['$items', start_from, limit]},
                'count': 1
            }},
        ]
        return res

    def test_details_nonexistent_organization(self):
        code, res = self.client.archived_recommendations_details_get(
            str(uuid.uuid4()), type='module', reason='reason', archived_at=123)
        self.assertEqual(code, 404)

    def test_details_empty(self):
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type='module', reason='reason', archived_at=123)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 0)
        self.assertEqual(res['items'], [])

    def test_details_unexpected_parameters(self):
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type='module', reason='reason', archived_at=123,
            key='value')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_details_another_org_data(self):
        module = 'module'
        reason = 'reason'
        archived_at = self.start_date + DAY_TS
        self._add_archive_recommendation(
            str(uuid.uuid4()), module, reason, self.instance,
            archived_at)
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type=module, reason=reason, archived_at=archived_at)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 0)
        self.assertEqual(res['items'], [])

    def test_details_incorrect_date(self):
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type='module', reason='reason', archived_at=-123)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_breakdown_limit(self):
        params = {
            'organization_id': self.org_id,
            'module': 'module',
            'reason': 'reason',
            'data': self.instance
        }
        records_count = 10
        for i in range(1, records_count + 1):
            self._add_archive_recommendation(
                **params, archived_at=self.start_date + DAY_TS * i)

        for val in [
            (1, 1),
            (5, 5),
            (records_count * 2, records_count)
        ]:
            limit, expected = val
            params = {'limit': limit}
            code, res = self.client.breakdown_archived_recommendations_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date,
                params=params)
            self.assertEqual(code, 200)
            self.assertEqual(len(res['breakdown']), expected)

        params = {'limit': 0}
        code, res = self.client.breakdown_archived_recommendations_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_details(self):
        count_per_reason = 5
        insertions = [
            ('module_1', ['reason_1_1', 'reason_1_2']),
            ('module_2', ['reason_2_1']),
        ]
        for val in insertions:
            module, reasons = val
            for reason in reasons:
                i = 1
                for _ in range(count_per_reason):
                    self._add_archive_recommendation(
                        self.org_id, module, reason, self.instance,
                        self.start_date + DAY_TS * i)

        for val in insertions:
            module, reasons = val
            for reason in reasons:
                i = 1
                code, res = self.client.archived_recommendations_details_get(
                    self.org_id, type=module, reason=reason,
                    archived_at=self.start_date + DAY_TS * i)
                self.assertEqual(code, 200)
                self.assertEqual(res['count'], count_per_reason)
                self.assertEqual(len(res['items']), count_per_reason)
                for item in res['items']:
                    self.assertEqual(item['module'], module)
                    self.assertEqual(item['reason'], reason)
                    self.assertEqual(item['archived_at'], self.start_date + DAY_TS * i)

    def test_details_limit(self):
        count = 15
        limit = 10
        module = 'module'
        reason = 'reason'
        for i in range(count):
            self._add_archive_recommendation(
                self.org_id, module, reason, self.instance,
                self.start_date)
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type=module, reason=reason,
            archived_at=self.start_date, limit=limit)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], count)
        self.assertEqual(len(res['items']), limit)
        self.assertEqual(res['limit'], limit)

        for limit in [0, -1]:
            code, res = self.client.archived_recommendations_details_get(
                self.org_id, type=module, reason=reason,
                archived_at=self.start_date, limit=limit)
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_details_start_from(self):
        count = 15
        module = 'module'
        reason = 'reason'
        for i in range(count):
            self._add_archive_recommendation(
                self.org_id, module, reason, self.instance,
                self.start_date)
        for i in range(count):
            code, res = self.client.archived_recommendations_details_get(
                self.org_id, type=module, reason=reason,
                archived_at=self.start_date, start_from=i)
            self.assertEqual(code, 200)
            self.assertEqual(res['count'], count)
            self.assertEqual(len(res['items']), count - i)

        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type=module, reason=reason,
            archived_at=self.start_date, start_from=-1)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_details_dates(self):
        self._add_archive_recommendation(
            self.org_id, 'module', 'reason', self.instance, self.start_date)
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 1)
        self.assertEqual(len(res['items']), 1)

        code, res = self.client.archived_recommendations_details_get(
            self.org_id, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 1)
        self.assertEqual(len(res['items']), 1)

        code, res = self.client.archived_recommendations_details_get(
            self.org_id, start_date=self.start_date)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 1)
        self.assertEqual(len(res['items']), 1)

    def test_details_invalid_dates(self):
        for param in ['start_date', 'end_date']:
            code, res = self.client.archived_recommendations_details_get(
                self.org_id, **{param: 'test'})
            self.assertEqual(code, 400)
            self.assertEqual(res['error']['error_code'], 'OE0217')

    def test_details_format(self):
        self._add_archive_recommendation(
            self.org_id, 'module', 'reason', self.instance, self.start_date)
        code, res = self.client.archived_recommendations_details_get(
                self.org_id, format='json')
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 1)
        self.assertEqual(len(res['items']), 1)

    def test_details_invalid_format(self):
        code, res = self.client.archived_recommendations_details_get(
                self.org_id, format='test')
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0473')

    def test_details_pages(self):
        count = 15
        limit = 5
        module = 'module'
        reason = 'reason'
        for i in range(count):
            self.instance['page'] = i // limit
            self._add_archive_recommendation(
                self.org_id, module, reason, self.instance,
                self.start_date)
        for i in range(0, count, limit):
            code, res = self.client.archived_recommendations_details_get(
                self.org_id, type=module, reason=reason,
                archived_at=self.start_date, start_from=i, limit=limit)
            self.assertEqual(code, 200)
            self.assertEqual(res['count'], count)
            self.assertEqual(len(res['items']), limit)
            for item in res['items']:
                self.assertEqual(item['page'], i // limit)

        start_from = 12
        code, res = self.client.archived_recommendations_details_get(
            self.org_id, type=module, reason=reason,
            archived_at=self.start_date, start_from=start_from, limit=limit)
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], count)
        self.assertEqual(len(res['items']), count - start_from)


class TestArchivedRecommendationsCountApi(TestArchivedRecommendationsBase):
    def test_count_nonexistent_organization(self):
        code, res = self.client.archived_recommendations_count_get(
            str(uuid.uuid4()), start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 404)

    def test_count_empty(self):
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertFalse(res.get('breakdown', {}) == {})
        points = tuple(str(x) for x in range(
            self.start_date, self.end_date, DEFAULT_PRECISION))
        for point in res.get('breakdown', {}).keys():
            self.assertTrue(point in points)

    def test_count_unexpected_parameters(self):
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params={'key': 'value'})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0212')

    def test_count_another_org_data(self):
        self._add_archive_recommendation(
            str(uuid.uuid4()), 'module', 'reason', self.instance,
            self.start_date + DAY_TS)
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        points = tuple(str(x) for x in range(
            self.start_date, self.end_date, DEFAULT_PRECISION))
        for point in res.get('breakdown', {}).keys():
            self.assertTrue(point in points)

    def test_count_incorrect_dates_range(self):
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.end_date, end_date=self.start_date)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0446')

    def test_count_incorrect_precision(self):
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params={'precision': 123})
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0520')

    def test_count_incorrect_dates(self):
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=-1, end_date=self.start_date)
        self.assertEqual(code, 400)
        self.assertEqual(res['error']['error_code'], 'OE0224')

    def test_count_dates(self):
        params = {
            'organization_id': self.org_id,
            'module': 'module',
            'reason': 'reason',
            'data': self.instance
        }

        for val in [
            (self.end_date, 0),
            (self.start_date - DAY_TS, 0),
            (self.end_date + DAY_TS, 0),
            (self.start_date, 1),  # only lower bound in range
        ]:
            archived_at, records_count = val
            self._add_archive_recommendation(**params, archived_at=archived_at)
            code, res = self.client.archived_recommendations_count_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date)
            self.assertEqual(code, 200)
            self.assertEqual(res.get('count'), records_count)

    def test_count_filters(self):
        count_per_reason = (self.end_date - self.start_date) // DEFAULT_PRECISION
        insertions = [
            ('module_1', ['reason_1_1', 'reason_1_2']),
            ('module_2', ['reason_2_1']),
        ]
        modules = []
        reasons = []
        for val in insertions:
            module_, reasons_ = val
            modules.append(module_)
            reasons.extend(reasons_)
            for reason in reasons_:
                for i in range(count_per_reason):
                    self._add_archive_recommendation(
                        self.org_id, module_, reason, self.instance,
                        self.start_date + DAY_TS * i)

        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), len(reasons) * count_per_reason)
        self.assertEqual(len(res.get('breakdown')), count_per_reason)
        self.assertTrue(all(map(
            lambda x: len(x) == len(insertions), res['breakdown'].values())))
        for ts, data in res['breakdown'].items():
            self.assertTrue((int(ts) - self.start_date) % DAY_TS == 0)
            for module_, reasons_ in data.items():
                self.assertTrue(module_ in modules)
                self.assertTrue(all(map(lambda x: x in reasons, reasons_.keys())))
                self.assertTrue(all(map(lambda x: x == 1, reasons_.values())))
        self.assertEqual(res['start_date'], self.start_date)
        self.assertEqual(res['end_date'], self.end_date)

        module, reasons = insertions[0]
        params = {'type': module}
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), len(reasons) * count_per_reason)
        self.assertEqual(len(res.get('breakdown')), count_per_reason)
        for ts, data in res['breakdown'].items():
            self.assertTrue((int(ts) - self.start_date) % DAY_TS == 0)
            for module_, reasons_ in data.items():
                self.assertEqual(module_, module)

        params = {'reason': reasons[0]}
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), count_per_reason)
        self.assertEqual(len(res.get('breakdown')), count_per_reason)

        params = {'reason': reasons}
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), len(reasons) * count_per_reason)
        self.assertEqual(len(res.get('breakdown')), count_per_reason)

        params = {'type': module, 'reason': reasons}
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), len(reasons) * count_per_reason)
        self.assertEqual(len(res.get('breakdown')), count_per_reason)

        module_1, reasons_1 = insertions[0]
        module_2, reasons_2 = insertions[1]
        params = {'type': module_1, 'reason': reasons_2}
        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date,
            params=params)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), 0)

    def test_count_breakdown(self):
        count_per_reason = (self.end_date - self.start_date) // DEFAULT_PRECISION
        insertions = [
            ('module_1', ['reason_1_1', 'reason_1_2']),
            ('module_2', ['reason_2_1']),
        ]
        modules = []
        reasons = []
        for val in insertions:
            module_, reasons_ = val
            modules.append(module_)
            reasons.extend(reasons_)
            for reason in reasons_:
                for i in range(1, count_per_reason + 1):
                    self._add_archive_recommendation(
                        self.org_id, module_, reason, self.instance,
                        self.start_date + DAY_TS)

        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(code, 200)
        self.assertEqual(res.get('count'), count_per_reason * len(reasons))
        nonempty_breakdowns = {
            k: v for k, v in res.get('breakdown', {}).items() if v}
        self.assertEqual(len(nonempty_breakdowns), 1)
        breakdown = nonempty_breakdowns.pop(str(self.start_date + DAY_TS), None)
        self.assertIsNotNone(breakdown)
        for module, reasons_data in breakdown.items():
            self.assertTrue(module in modules)
            for reason, count in reasons_data.items():
                self.assertTrue(reason in reasons)
                self.assertEqual(count, count_per_reason)

    def test_count_precision(self):
        module = 'module'
        reason = 'reason'
        min_precision = min(SUPPORTED_PRECISIONS)
        total_records = (self.end_date - self.start_date) // min_precision
        for ts in range(self.start_date, self.end_date, min_precision):
            self._add_archive_recommendation(
                self.org_id, module, reason, self.instance, ts)
        for precision in SUPPORTED_PRECISIONS:
            code, res = self.client.archived_recommendations_count_get(
                self.org_id, start_date=self.start_date, end_date=self.end_date,
                params={'precision': precision})
            self.assertEqual(code, 200)
            self.assertEqual(res.get('count'), total_records)
            breakdown = res.get('breakdown', {})
            points_count = (self.end_date - self.start_date) // precision
            self.assertEqual(len(breakdown), points_count)
            records_per_point = precision // min_precision
            for point, modules_data in breakdown.items():
                self.assertEqual(modules_data[module][reason], records_per_point)
                self.assertTrue(int(point) < self.end_date)

        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.end_date - DEFAULT_PRECISION,
            end_date=self.end_date, params={'precision': DEFAULT_PRECISION})
        self.assertEqual(code, 200)
        modules_data = res.get('breakdown', {}).get(
            str(self.end_date - DEFAULT_PRECISION), {})
        self.assertNotEqual(modules_data, {})

        code, res = self.client.archived_recommendations_count_get(
            self.org_id, start_date=self.end_date - 1, end_date=self.end_date)
        self.assertEqual(code, 200)
