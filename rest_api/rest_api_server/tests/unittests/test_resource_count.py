from datetime import datetime, timezone
from unittest.mock import patch
from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase


class TestResourcesCountApi(TestApiBase):

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
        _, self.employee1 = self.client.employee_create(
            self.org_id, {'name': 'name1', 'auth_user_id': self.auth_user_id_1})
        _, self.employee2 = self.client.employee_create(
            self.org_id, {'name': 'name2', 'auth_user_id': self.auth_user_id_2})
        _, self.cloud_acc1 = self.create_cloud_account(
            self.org_id, cloud_acc1, auth_user_id=self.auth_user_id_1)
        _, self.cloud_acc2 = self.create_cloud_account(
            self.org_id, cloud_acc2, auth_user_id=self.auth_user_id_2)

        _, self.sub_pool1 = self.client.pool_create(self.org_id, {
            'name': 'sub1',
            'parent_id': self.org['pool_id'],
        })
        _, self.sub_pool2 = self.client.pool_create(self.org_id, {
            'name': 'sub2',
            'parent_id': self.sub_pool1['id'],
        })

        self.day1 = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp())
        self.day2 = self.day1 + 86400
        self.day3 = self.day2 + 86400
        self.day4 = self.day3 + 86400
        self.day1_inside = self.day1 + 50000
        self.day2_inside = self.day2 + 50000
        self.day3_inside = self.day3 + 50000
        self.day4_inside = self.day4 + 50000
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee1['id'])

    @staticmethod
    def extract_fields(obj, fields):
        return {x: obj[x] for x in fields}

    def _create_resource(self, cloud_account_id, name=None, r_type=None,
                         count=1, **kwargs):
        resources = []
        for i in range(0, count, 1):
            code, resource = self.cloud_resource_create(
                cloud_account_id, {
                    'cloud_resource_id': self.gen_id(),
                    'name': name if name else 'default_name',
                    'resource_type': r_type if r_type else 'default_type',
                    **kwargs
                })
            self.assertEqual(code, 201)
            resources.append(resource)
        return resources

    def _add_extra_fields(self, resources, **kwargs):
        resource_ids = [x['id'] for x in resources]
        self.resources_collection.update_many(
            filter={
                '_id': {'$in': resource_ids}
            },
            update={'$set': kwargs})

    def test_breakdown_filter_by_cloud_acc(self):
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day2 - 1, count=5)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type2', first_seen=self.day2,
            last_seen=self.day2_inside, count=5)
        self._create_resource(
            self.cloud_acc2['id'], r_type='type3', first_seen=self.day1_inside,
            last_seen=self.day2_inside, count=5)
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'cloud_account_id')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {
                self.cloud_acc1['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.cloud_acc1, ['id', 'name', 'type'])
                },
                self.cloud_acc2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.cloud_acc2, ['id', 'name', 'type'])
                }},
            str(self.day2): {
                self.cloud_acc1['id']: {
                    'count': 5, 'created': 5, 'deleted_day_before': 5,
                    **self.extract_fields(
                        self.cloud_acc1, ['id', 'name', 'type'])
                },
                self.cloud_acc2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.cloud_acc2, ['id', 'name', 'type'])
                }}
        }
        self.assertEqual(res['count'], 15)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {
            self.cloud_acc1['id']: {
                'total': 10, 'average': 5, **self.extract_fields(
                    self.cloud_acc1, ['id', 'name', 'type'])
            },
            self.cloud_acc2['id']: {
                'total': 5, 'average': 5, **self.extract_fields(
                    self.cloud_acc2, ['id', 'name', 'type'])
            }}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'cloud_account_id': self.cloud_acc1['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 0, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 0, 'created': 0,
                                       'deleted_day_before': 5},
                             'type2': {'count': 5, 'created': 5,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 10)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 5, 'average': 2.5},
                  'type2': {'total': 5, 'average': 2.5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'cloud_account_id': self.cloud_acc2['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type3': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

    def test_breakdown_filter_by_employee_id(self):
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day2 - 1, employee_id=self.employee1['id'],
            pool_id=self.sub_pool1['id'], count=5)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type2', first_seen=self.day2,
            last_seen=self.day2_inside, employee_id=self.employee1['id'],
            pool_id=self.sub_pool1['id'], count=5)
        self._create_resource(
            self.cloud_acc2['id'], r_type='type3', first_seen=self.day1_inside,
            last_seen=self.day2_inside, employee_id=self.employee2['id'],
            pool_id=self.sub_pool2['id'], count=5)
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'employee_id')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {
                self.employee1['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(self.employee1, ['id', 'name'])
                },
                self.employee2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(self.employee2, ['id', 'name'])
                }},
            str(self.day2): {
                self.employee1['id']: {
                    'count': 5, 'created': 5, 'deleted_day_before': 5,
                    **self.extract_fields(self.employee1, ['id', 'name'])
                },
                self.employee2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(self.employee2, ['id', 'name'])
                }}
        }
        self.assertEqual(res['count'], 15)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {
            self.employee1['id']: {
                'total': 10, 'average': 5, **self.extract_fields(
                    self.employee1, ['id', 'name'])
            },
            self.employee2['id']: {
                'total': 5, 'average': 5, **self.extract_fields(
                    self.employee2, ['id', 'name'])
            }}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'owner_id': self.employee1['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 0, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 0, 'created': 0,
                                       'deleted_day_before': 5},
                             'type2': {'count': 5, 'created': 5,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 10)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 5, 'average': 2.5},
                  'type2': {'total': 5, 'average': 2.5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'owner_id': self.employee2['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type3': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

    def test_breakdown_filter_by_pool_id(self):
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day2 - 1, employee_id=self.employee1['id'],
            pool_id=self.sub_pool1['id'], count=5)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type2', first_seen=self.day2,
            last_seen=self.day2_inside, employee_id=self.employee1['id'],
            pool_id=self.sub_pool1['id'], count=5)
        self._create_resource(
            self.cloud_acc2['id'], r_type='type3', first_seen=self.day1_inside,
            last_seen=self.day2_inside, employee_id=self.employee2['id'],
            pool_id=self.sub_pool2['id'], count=5)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'pool_id')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {
                self.sub_pool1['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.sub_pool1, ['id', 'name', 'purpose'])
                },
                self.sub_pool2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.sub_pool2, ['id', 'name', 'purpose'])
                }},
            str(self.day2): {
                self.sub_pool1['id']: {
                    'count': 5, 'created': 5, 'deleted_day_before': 5,
                    **self.extract_fields(
                        self.sub_pool1, ['id', 'name', 'purpose'])
                },
                self.sub_pool2['id']: {
                    'count': 5, 'created': 0, 'deleted_day_before': 0,
                    **self.extract_fields(
                        self.sub_pool2, ['id', 'name', 'purpose'])
                }}
        }
        self.assertEqual(res['count'], 15)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {
            self.sub_pool1['id']: {
                'total': 10, 'average': 5, **self.extract_fields(
                    self.sub_pool1, ['id', 'name', 'purpose'])
            },
            self.sub_pool2['id']: {
                'total': 5, 'average': 5, **self.extract_fields(
                    self.sub_pool2, ['id', 'name', 'purpose'])
            }}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'pool_id': self.pool_id_with_subpools(self.org['pool_id'])})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 0, 'created': 0,
                                       'deleted_day_before': 0},
                             'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 0, 'created': 0,
                                       'deleted_day_before': 5},
                             'type2': {'count': 5, 'created': 5,
                                       'deleted_day_before': 0},
                             'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 15)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 5, 'average': 2.5},
                  'type2': {'total': 5, 'average': 2.5},
                  'type3': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'pool_id': self.org['pool_id']})
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 0)
        counts = {}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'pool_id': self.sub_pool1['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 0, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 0, 'created': 0,
                                       'deleted_day_before': 5},
                             'type2': {'count': 5, 'created': 5,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 10)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 5, 'average': 2.5},
                  'type2': {'total': 5, 'average': 2.5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'pool_id': self.sub_pool2['id']})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type3': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type3': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

    def test_filter_by_bool_params(self):
        res1 = self._create_resource(
            self.cloud_acc1['id'], first_seen=self.day1, last_seen=self.day2,
            r_type='type1', count=3)
        res2 = self._create_resource(
            self.cloud_acc1['id'], first_seen=self.day1, last_seen=self.day2,
            r_type='type2', count=5)
        self._add_extra_fields(res1, recommendations={
            'run_timestamp': datetime.utcnow().timestamp()})

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'recommendations': True})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 3)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 3, 'average': 3}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'recommendations': False})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type2': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type2': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type2': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

        self._add_extra_fields(res2, constraint_violated=True)
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'constraint_violated': True})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type2': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type2': {'count': 5, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type2': {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'constraint_violated': False})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 3)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 3, 'average': 3}}
        self.assertEqual(res['counts'], counts)

        self._make_resources_active([x['id'] for x in res2[:2]])
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'active': True})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type2': {'count': 2, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type2': {'count': 2, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 2)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type2': {'total': 2, 'average': 2}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'active': False})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}},
            str(self.day2): {'type1': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0},
                             'type2': {'count': 3, 'created': 0,
                                       'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 6)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'type1': {'total': 3, 'average': 3},
                  'type2': {'total': 3, 'average': 3}}
        self.assertEqual(res['counts'], counts)

    def test_clusters_environments(self):
        type_name = 'type1'
        self._create_resource(
            self.cloud_acc1['id'], first_seen=self.day1, last_seen=self.day2,
            r_type=type_name, count=5)
        tag_key = 'my_tag'
        code, cluster_resource = self.client.cluster_type_create(
            self.org_id, {'name': type_name, 'tag_key': tag_key})
        self.assertEqual(code, 201)
        self._create_resource(
            self.cloud_acc1['id'], first_seen=self.day1,
            last_seen=self.day2_inside, tags={tag_key: 'val1'}, count=2)
        self._create_resource(
            self.cloud_acc1['id'], first_seen=self.day1,
            last_seen=self.day2_inside, tags={tag_key: 'val2'}, count=3)
        code, env_resource = self.environment_resource_create(
            self.org_id, {'name': 'some_name', 'resource_type': type_name})
        self.assertEqual(code, 201)
        self._add_extra_fields(
            [cluster_resource, env_resource], first_seen=self.day1,
            last_seen=self.day2_inside)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'resource_type': '%s:regular' % type_name})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {type_name: {'count': 5, 'created': 0,
                                         'deleted_day_before': 0}},
            str(self.day2): {type_name: {'count': 5, 'created': 0,
                                         'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {type_name: {'total': 5, 'average': 5}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'resource_type': '%s:environment' % type_name})
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'%s:environment' % type_name: {
                'count': 1, 'created': 0, 'deleted_day_before': 0}},
            str(self.day2): {'%s:environment' % type_name: {
                'count': 1, 'created': 0, 'deleted_day_before': 0}}
        }
        self.assertEqual(res['count'], 1)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {'%s:environment' % type_name: {'total': 1, 'average': 1}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type',
            {'resource_type': '%s:cluster' % type_name})
        _, filt_res = self.client.available_filters_get(
            self.org_id, self.day1, self.day2_inside,
            {'resource_type': '%s:cluster' % type_name}
        )
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'%s:cluster' % type_name: {
                'count': 2, 'created': 0, 'deleted_day_before': 0}},
            str(self.day2): {'%s:cluster' % type_name: {
                'count': 2, 'created': 0, 'deleted_day_before': 0}}
        }
        cloud_accounts = self.get_all_org_cloud_accounts(self.org_id)
        self.assertEqual(res['count'], 2)
        self.assertEqual(res['breakdown'], breakdown)
        self.assertEqual(len(filt_res['filter_values']['cloud_account']),
                         len(cloud_accounts + [None]))
        counts = {'%s:cluster' % type_name: {'total': 2, 'average': 2}}
        self.assertEqual(res['counts'], counts)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'resource_type')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {type_name: {'count': 5, 'created': 0,
                                         'deleted_day_before': 0},
                             '%s:cluster' % type_name: {
                                 'count': 2, 'created': 0,
                                 'deleted_day_before': 0},
                             '%s:environment' % type_name: {
                                 'count': 1, 'created': 0,
                                 'deleted_day_before': 0}},
            str(self.day2): {type_name: {'count': 5, 'created': 0,
                                         'deleted_day_before': 0},
                             '%s:cluster' % type_name: {
                                 'count': 2, 'created': 0,
                                 'deleted_day_before': 0},
                             '%s:environment' % type_name: {
                                 'count': 1, 'created': 0,
                                 'deleted_day_before': 0}},
        }
        self.assertEqual(res['count'], 8)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {type_name: {'total': 5, 'average': 5},
                  '%s:cluster' % type_name: {'total': 2, 'average': 2},
                  '%s:environment' % type_name: {'total': 1,
                                                 'average': 1}}
        self.assertEqual(res['counts'], counts)

    def test_crossed_breakdown(self):
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day2_inside, count=2)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day2,
            last_seen=self.day2_inside, count=3)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day2,
            last_seen=self.day4_inside, count=4)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day4,
            last_seen=self.day4_inside, count=11)

        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day3_inside, 'cloud_account_id')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {self.cloud_acc1['id']: {
                'count': 2, 'created': 0, 'deleted_day_before': 0,
                **self.extract_fields(
                    self.cloud_acc1, ['id', 'name', 'type'])
            }},
            str(self.day2): {self.cloud_acc1['id']: {
                'count': 9, 'created': 7, 'deleted_day_before': 0,
                **self.extract_fields(
                    self.cloud_acc1, ['id', 'name', 'type'])
            }},
            str(self.day3): {self.cloud_acc1['id']: {
                'count': 4, 'created': 0, 'deleted_day_before': 5,
                **self.extract_fields(
                    self.cloud_acc1, ['id', 'name', 'type'])
            }}
        }
        self.assertEqual(res['count'], 9)
        self.assertEqual(res['breakdown'], breakdown)
        counts = {
            self.cloud_acc1['id']: {
                'total': 9, 'average': 5,
                **self.extract_fields(self.cloud_acc1, ['id', 'name', 'type'])
            }
        }
        self.assertEqual(res['counts'], counts)

    def test_invalid_breakdown(self):
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'bad_breakdown')
        self.assertEqual(code, 400)
        self.verify_error_code(res, 'OE0217')

    def test_no_resources(self):
        day = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())
        day2 = day + 86400
        code, res = self.client.resources_count_get(
            self.org_id, day, day2, 'cloud_account_id')
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 0)

    def test_no_breakdown_by(self):
        day = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp())
        day2 = day + 86400
        code, res = self.client.resources_count_get(
            self.org_id, day, day2)
        self.assertEqual(code, 200)
        self.assertIsNone(res.get('breakdown_by'))

    def test_breakdown_created_removed(self):
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day1_inside, count=1)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day2,
            last_seen=self.day2_inside, count=2)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day2,
            last_seen=self.day3, count=4)
        self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day3, count=8)
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day3, 'resource_type')
        self.assertEqual(code, 200)
        breakdown = {
            str(self.day1): {'type1': {
                'count': 9,  # 1 + 8
                'created': 0,
                'deleted_day_before': 0}},
            str(self.day2): {'type1': {
                'count': 14,  # 2 + 4 + 8
                'created': 6,  # 2 + 4
                'deleted_day_before': 1}},
            str(self.day3): {'type1': {
                'count': 12,  # 4 + 8
                'created': 0,
                'deleted_day_before': 2}},
        }
        self.assertEqual(res['count'], 15)
        self.assertEqual(res['breakdown'], breakdown)

    def test_breakdown_traffic_filters(self):
        res1 = self._create_resource(
            self.cloud_acc1['id'], r_type='type1', first_seen=self.day1,
            last_seen=self.day2 - 1)[0]
        res2 = self._create_resource(
            self.cloud_acc1['id'], r_type='type2', first_seen=self.day2,
            last_seen=self.day2_inside)[0]
        res3 = self._create_resource(
            self.cloud_acc2['id'], r_type='type3', first_seen=self.day1_inside,
            last_seen=self.day2_inside)[0]
        self.traffic_expenses = [
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res1['cloud_resource_id'],
                'date': self.day1,
                'type': 1,
                'from': 'from_1',
                'to': 'to_1',
                'usage': 1,
                'cost': 1,
                'sign': 1
            },
            {
                'cloud_account_id': self.cloud_acc1['id'],
                'resource_id': res2['cloud_resource_id'],
                'date': self.day2,
                'type': 1,
                'from': 'from_2',
                'to': 'to_1',
                'usage': 1,
                'cost': 1,
                'sign': 1
            }
        ]

        for body in [
            {'traffic_from': 'ANY'},
            {'traffic_to': 'ANY'},
            {'traffic_to': 'to_1:aws_cnr'},
            {'traffic_from': ['from_1:aws_cnr', 'from_2:aws_cnr']}
        ]:
            code, res = self.client.resources_count_get(
                self.org_id, self.day1, self.day2_inside,
                'cloud_account_id', body)
            self.assertEqual(code, 200)
            self.assertEqual(res['count'], 2)
            self.assertEqual(res['counts'], {
                self.cloud_acc1['id']: {
                    'total': 2,
                    'id': self.cloud_acc1['id'],
                    'name': self.cloud_acc1['name'],
                    'type': self.cloud_acc1['type'],
                    'average': 1.0
                }
            })

        for body in [
            {'traffic_from': 'from_1:aws_cnr'},
            {'traffic_from': 'from_2:aws_cnr'}
        ]:
            code, res = self.client.resources_count_get(
                self.org_id, self.day1, self.day2_inside,
                'cloud_account_id', body)
            self.assertEqual(code, 200)
            self.assertEqual(res['count'], 1)
            self.assertEqual(res['counts'], {
                self.cloud_acc1['id']: {
                    'total': 1,
                    'id': self.cloud_acc1['id'],
                    'name': self.cloud_acc1['name'],
                    'type': self.cloud_acc1['type'],
                    'average': 0.5
                }
            })
        code, res = self.client.resources_count_get(
            self.org_id, self.day1, self.day2_inside, 'cloud_account_id')
        self.assertEqual(code, 200)
        self.assertEqual(res['count'], 3)
