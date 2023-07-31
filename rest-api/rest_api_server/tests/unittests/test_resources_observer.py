import uuid
from datetime import datetime, timedelta
from freezegun import freeze_time
from unittest.mock import patch, ANY, call

from rest_api_server.models.db_factory import DBType, DBFactory
from rest_api_server.models.db_base import BaseDB
from rest_api_server.models.enums import ConstraintLimitStates, ConstraintTypes
from rest_api_server.tests.unittests.test_api_base import TestApiBase

from cloud_adapter.model import InstanceResource

NEWLY_DISCOVERED_TIME = 300  # 5 min
PROCESS_RESOURCES = ('rest_api_server.controllers.limit_hit.'
                     'LimitHitsController.process_resources')


class TestObserver(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        db = DBFactory(DBType.Test, None).db
        engine = db.engine
        self.session = BaseDB.session(engine)()
        _, self.org = self.client.organization_create(
            {'name': "partner_test"})
        self.valid_aws_creds = {
            'name': 'my creds',
            'type': 'aws_cnr',
            'config': {
                'access_key_id': 'key',
                'secret_access_key': 'secret',
                'config_scheme': 'create_report'
            }
        }
        self.org_id = self.org['id']
        self.user_id = self.gen_id()
        _, self.employee = self.client.employee_create(
            self.org_id, {'name': 'Eliot Alderson', 'auth_user_id': self.user_id})
        self.update_default_owner_for_pool(self.org['pool_id'],
                                           self.employee['id'])
        patch('rest_api_server.controllers.cloud_account.'
              'CloudAccountController._configure_report').start()
        _, cloud_account = self.create_cloud_account(
            self.org_id, self.valid_aws_creds, auth_user_id=self.user_id)
        self.cloud_acc_id = cloud_account['id']
        _, self.pool = self.client.pool_get(self.org['pool_id'])
        self.pool_name = self.pool['name']
        self.pool_id = self.org['pool_id']
        self.instances = self.get_instances(self.org_id)
        user_roles = [{
            "user_id": self.user_id,
            "role_purpose": 'optscale_manager'
        }]
        self.p_get_roles_info = patch(
            'rest_api_server.handlers.v1.base.BaseAuthHandler.get_roles_info',
            return_value=user_roles).start()
        patch(
            'rest_api_server.controllers.resource_constraint.'
            'ConstraintBaseController.supported_constraint_types',
            return_value=[
                ConstraintTypes.TTL,
                ConstraintTypes.DAILY_EXPENSE_LIMIT,
                ConstraintTypes.TOTAL_EXPENSE_LIMIT
            ]).start()

    def _create_mongo_resource(self, name, cloud_account_id=None,
                               organization_id=None, created_at=None,
                               applied_rules=None, active=True):
        if not created_at:
            created_at = int(datetime.utcnow().timestamp())
        if not cloud_account_id:
            cloud_account_id = self.cloud_acc_id
        if not organization_id:
            organization_id = self.org_id
        resource = {
            'name': name,
            'cloud_account_id': cloud_account_id,
            'cloud_resource_id': str(uuid.uuid4()),
            'created_at': created_at,
            'organization_id': organization_id,
            'active': active
        }
        if applied_rules:
            resource['applied_rules'] = applied_rules
        self.mongo_client.restapi.resources.insert_one(resource)

    def get_instances(self, org_id):
        tags = {'tn': 'tv'}
        i1 = InstanceResource(
            cloud_resource_id='i-aaa',
            cloud_account_id=self.cloud_acc_id,
            region='us-1',
            name='Instance1',
            flavor='t1-tiny',
            tags=tags,
        )
        i2 = InstanceResource(
            cloud_resource_id='i-aab',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='instance2',
            flavor='t1-tiny',
            tags=tags,
        )
        i3 = InstanceResource(
            cloud_resource_id='i-ccb',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='Instance3',
            flavor='t1-tiny',
            tags=tags,
        )
        i4 = InstanceResource(
            cloud_resource_id='i-cbe',
            cloud_account_id=self.cloud_acc_id,
            region='us-2',
            name='INstance7',
            flavor='t777-superlarge',
            tags=tags,
        )
        return [i1, i2, i3, i4]

    @patch(PROCESS_RESOURCES)
    def test_observe_empty(self, m_hits):
        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        m_hits.assert_not_called()

    @patch(PROCESS_RESOURCES)
    def test_observe_after_discover(self, m_hits):
        self.resource_discovery_call(self.instances)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(m_hits.call_count, 1)

    @patch(PROCESS_RESOURCES)
    def test_observe_only_cached(self, m_hits):
        self.resource_discovery_call(self.instances)
        resources = list(self.resources_collection.find())
        for resource in resources:
            self.assertTrue(resource.get('active'))
        now = datetime.utcnow()
        with freeze_time(now + timedelta(60)):
            self.resource_discovery_call(self.instances, create_resources=False)
            code, _ = self.client.observe_resources(self.org_id)
            self.assertEqual(code, 204)
        m_hits.assert_not_called()
        resources = list(self.resources_collection.find())
        for resource in resources:
            self.assertTrue(not resource.get('active'))

    def test_observe_newly_discovered_resources(self):
        rule_1 = {'id': str(uuid.uuid4()), 'name': 'rule1',
                  'pool_name': self.pool_name, 'pool_id': self.org['pool_id']}
        rule_2 = {'id': str(uuid.uuid4()), 'name': 'rule2',
                  'pool_name': self.pool_name, 'pool_id': self.org['pool_id']}
        _, pool = self.client.pool_create(
            self.org['id'], params={'name': 'test_pool'})
        rule_3 = {'id': str(uuid.uuid4()), 'name': 'rule3',
                  'pool_name': pool['name'], 'pool_id': pool['id']}
        self._create_mongo_resource('res1', applied_rules=[rule_1, rule_2])
        self._create_mongo_resource('res2', applied_rules=[rule_1])
        self._create_mongo_resource('res3', applied_rules=[rule_3, rule_2])
        old_times = int(datetime.utcnow().timestamp()) - 500
        self._create_mongo_resource('res_old', created_at=old_times,
                                    applied_rules=[rule_1, rule_2])
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()

        code, resp = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, ANY, 'cloud_account', 'resources_discovered', {
                'stat': {'total': 3, 'clusters': [], 'clustered': 0},
                'object_name': ANY
            })
        p_publish_activities.assert_has_calls([
            call(*activity_param_tuples, add_token=True)
        ])
        self.assertEqual(p_publish_activities.call_count, 4)
        rule_1['count'] = 2
        rule_2['count'] = 2
        rule_3['count'] = 1
        for rule in [rule_1, rule_2, rule_3]:
            p_publish_activities.assert_has_calls([
                call(self.org_id, rule['id'], 'rule',
                     'rule_applied', ANY, 'rule.rule_applied', add_token=True)
            ])

    def test_observe_newly_discovered_resources_clustered(self):
        patch('rest_api_server.controllers.limit_hit.'
              'LimitHitsController._get_recipients').start()
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        now = datetime.utcnow()
        self.resource_discovery_call(self.instances)
        resources = list(self.resources_collection.find())
        cluster = None
        for resource in resources:
            if resource.get('cluster_type_id'):
                cluster = resource
                continue
            self.assertIsNotNone(resource.get('cluster_id'))
        self.assertIsNotNone(cluster)

        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        activity_param_tuples = self.get_publish_activity_tuple(
            self.org_id, ANY, 'cloud_account', 'resources_discovered', {
                'stat': {'clustered': 4, 'clusters': [cluster['_id']],
                         'total': 4},
                'object_name': ANY
            })
        p_publish_activities.assert_has_calls([
            call(*activity_param_tuples, add_token=True)
        ])
        with freeze_time(now + timedelta(minutes=10)):
            self.resource_discovery_call(self.instances)
            code, _ = self.client.observe_resources(self.org_id)
            self.assertEqual(code, 204)
            activity_param_tuples = self.get_publish_activity_tuple(
                self.org_id, ANY, 'cloud_account', 'resources_discovered', {
                    'stat': {'clustered': 4, 'clusters': [cluster['_id']],
                             'total': 4},
                    'object_name': ANY
                })
            p_publish_activities.assert_has_calls([
                call(*activity_param_tuples, add_token=True)
            ])

    def test_observe_newly_discovered_resources_clustered_active(self):
        patch('rest_api_server.controllers.limit_hit.'
              'LimitHitsController._get_recipients').start()
        code, ct = self.client.cluster_type_create(
            self.org_id, {'name': 'my_ct', 'tag_key': 'tn'})
        self.assertEqual(code, 201)
        now = datetime.utcnow()
        self.resource_discovery_call(self.instances)

        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)

        self.resources_collection.update_many(
            filter={
                'cluster_type_id': {'$exists': False}
            },
            update={'$unset': {'active': 1}})

        with freeze_time(now + timedelta(minutes=1)):
            code, _ = self.client.observe_resources(self.org_id)
            self.assertEqual(code, 204)

        resources = list(self.resources_collection.find())
        cluster = None
        for resource in resources:
            if resource.get('cluster_type_id'):
                cluster = resource
                continue
            self.assertIsNotNone(resource.get('cluster_id'))
        self.assertIsNotNone(cluster)
        self.assertFalse(cluster.get('active', False))

    @patch('rest_api_server.controllers.limit_hit.LimitHitsController.'
           'send_alerts')
    def test_process_limit_hits(self, p_alerts):
        def get_violated_resource_ids():
            res = self.resources_collection.find({'constraint_violated': True})
            return list(map(lambda x: x['_id'], res))
        resources = self.resource_discovery_call(self.instances)
        code, policy = self.client.pool_policy_create(
            self.org['pool_id'], {'limit': 50, 'type': 'total_expense_limit'})
        self.assertEqual(code, 201)
        employee_id = self.gen_id()
        now = datetime.utcnow()
        res_ids = []
        for r in [resources[0], resources[1], resources[2]]:
            res_ids.append(r['id'])
            self.resources_collection.update_one(filter={
                    '_id': r['id']
                },
                update={'$set': {
                    'employee_id': employee_id,
                    'pool_id': self.org['pool_id']
                }})
            self.expenses.append({
                'cost': 100,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': datetime.utcnow(),
                'sign': 1
            })
        self.update_resource_info_by_expenses(res_ids)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(p_alerts.call_count, 1)
        self.assertEqual(code, 204)
        self.assertEqual(
            get_violated_resource_ids(),
            [resources[0]['id'], resources[1]['id'], resources[2]['id']])
        _, resp = self.client.pool_limit_hits_list(self.org['pool_id'])
        self.assertEqual(len(resp['limit_hits']), 3)
        for limit_hit in resp['limit_hits']:
            self.assertTrue(limit_hit['resource_id'] in
                            list(map(lambda x: x['id'], [
                                resources[0], resources[1], resources[2]])))

        self.resources_collection.update_one(
            filter={'_id': resources[0]['id']},
            update={'$set': {
                'last_seen': int(datetime.utcnow().timestamp()) - 2000,
                'active': False}})
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(get_violated_resource_ids(),
                         [resources[1]['id'], resources[2]['id']])
        p_alerts.assert_called_with(self.org_id, [])

        code, _ = self.client.pool_policy_update(
            policy['id'], {'limit': 200})
        self.assertEqual(code, 200)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(get_violated_resource_ids(), [])
        p_alerts.assert_called_with(self.org_id, [])

        code, resp = self.client.resource_constraint_create(
            resources[3]['id'], {'limit': 100, 'type': 'total_expense_limit'})
        self.assertEqual(code, 201)
        self.expenses.append({
            'cost': 150,
            'cloud_account_id': self.cloud_acc_id,
            'resource_id': resources[1]['id'],
            'date': datetime.utcnow(),
            'sign': 1
        })
        self.update_resource_info_by_expenses([resources[1]['id']])
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(get_violated_resource_ids(), [resources[1]['id']])

        self.expenses.append({
            'cost': 150,
            'cloud_account_id': self.cloud_acc_id,
            'resource_id': resources[3]['id'],
            'date': datetime.utcnow(),
            'sign': 1
        })
        self.update_resource_info_by_expenses([resources[3]['id']])
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(get_violated_resource_ids(),
                         [resources[1]['id'], resources[3]['id']])

        patch('rest_api_server.controllers.resource_constraint.'
              'ResourceConstraintController.get_resource_owner').start()
        code, resp = self.client.resource_constraint_create(
            resources[1]['id'], {'limit': 500, 'type': 'total_expense_limit'})
        self.assertEqual(code, 201)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(get_violated_resource_ids(),
                         [resources[3]['id']])

    def test_send_limit_hit_activities_task(self):
        m_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        patch('rest_api_server.controllers.limit_hit.'
              'LimitHitsController._get_recipients',
              return_value=[{'user_id': self.employee['auth_user_id']}]).start()

        # 1 activities task for resource owner and 1 to pool alert
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'based': 'constraint'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        m_activities_publish.reset_mock()
        resources = self.resource_discovery_call(self.instances)
        code, policy = self.client.pool_policy_create(
            self.org['pool_id'], {'limit': 50, 'type': 'total_expense_limit'})
        self.assertEqual(code, 201)
        r_ids = []
        for r in [resources[0], resources[1], resources[2]]:
            r_ids.append(r['id'])
            self.resources_collection.update_one(filter={
                '_id': r['id']
            },
                update={'$set': {
                    'employee_id': self.employee['id'],
                    'pool_id': self.org['pool_id']
                }})
            self.expenses.append({
                'cost': 100,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': datetime.utcnow(),
                'sign': 1
            })
        self.update_resource_info_by_expenses(r_ids)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        self.assertEqual(m_activities_publish.call_count, 4)

        # 1 activities task for resource owner
        code, _ = self.client.alert_delete(alert['id'])
        self.assertEqual(code, 204)
        m_activities_publish.reset_mock()
        code, policy = self.client.pool_policy_update(
            policy['id'], {'limit': 10})
        self.assertEqual(code, 200)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        meta = {'violations': ANY}
        m_activities_publish.assert_has_calls([
            call(self.org_id, self.employee['auth_user_id'], 'user',
                 'constraint_violated', meta,
                 'alert.violation.constraint_violated')])

    def test_activities_task_with_employee_alert_contact(self):
        m_activities_publish = patch(
            'rest_api_server.controllers.base.'
            'BaseController.publish_activities_task').start()
        patch('rest_api_server.controllers.limit_hit.'
              'LimitHitsController._get_recipients',
              return_value=[
                  {'user_id': self.employee['auth_user_id']}]).start()

        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'employee_id': self.employee['id']}],
            'based': 'constraint'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        m_activities_publish.reset_mock()
        resources = self.resource_discovery_call(self.instances)
        code, policy = self.client.pool_policy_create(
            self.org['pool_id'], {'limit': 50, 'type': 'total_expense_limit'})
        self.assertEqual(code, 201)
        for r in [resources[0], resources[1], resources[2]]:
            self.resources_collection.update_one(filter={
                '_id': r['id']
            },
                update={'$set': {
                    'employee_id': self.employee['id'],
                    'pool_id': self.org['pool_id']
                }})
            self.expenses.append({
                'cost': 100,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': datetime.utcnow(),
                'sign': 1
            })
        self.update_resource_info_by_expenses([
            r['id'] for r in [resources[0], resources[1], resources[2]]])
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        # policy create, deactivated rule + 2 constraints
        self.assertEqual(m_activities_publish.call_count, 4)

    @patch('rest_api_server.controllers.limit_hit.LimitHitsController.'
           'send_alerts')
    def test_process_ttl_limit_hits(self, p_alerts):
        now = datetime(year=2021, month=3, day=16)
        limit = 10
        with freeze_time(now):
            # 4 instances created
            resources = self.resource_discovery_call(self.instances)

        code, sub_pool = self.client.pool_create(self.org_id, {'name': 'sub'})
        self.assertEqual(code, 201)

        code, policy = self.client.pool_policy_create(
            sub_pool['id'], {'limit': limit, 'type': 'ttl'})
        self.assertEqual(code, 201)

        employee_id = self.gen_id()
        for r in [resources[0], resources[1], resources[2]]:
            self.resources_collection.update_one(filter={
                    '_id': r['id']
                },
                update={'$set': {
                    'employee_id': employee_id,
                    'pool_id': sub_pool['id']
                }})
            self.expenses.append({
                'cost': 100,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': now,
                'sign': 1
            })

        new_now = datetime.utcnow()
        with freeze_time(new_now):
            self.resource_discovery_call(self.instances)
            code, _ = self.client.process_resource_violations(self.org_id)
            self.assertEqual(p_alerts.call_count, 1)
            self.assertEqual(code, 204)

            _, resp = self.client.pool_limit_hits_list(sub_pool['id'])
            # resource[3] assigned to root pool
            self.assertEqual(len(resp['limit_hits']), 3)
            for limit_hit in resp['limit_hits']:
                self.assertTrue(limit_hit['ttl_value'] >= int(new_now.timestamp()),
                                'hit value %s, '
                                'frozen now %s' % (limit_hit['ttl_value'],
                                                   int(new_now.timestamp())))
                self.assertEqual(limit_hit['constraint_limit'],
                                 int(now.timestamp()) + limit * 3600)

    @patch('rest_api_server.controllers.limit_hit.LimitHitsController.'
           'send_alerts')
    def test_process_daily_limit_hits(self, p_alerts):
        now = datetime(year=2021, month=3, day=16)
        limit = 10
        with freeze_time(now):
            # 4 instances created
            resources = self.resource_discovery_call(self.instances)

        for res in resources:
            code, constraint = self.client.resource_constraint_create(
                res['id'], {'limit': limit, 'type': 'daily_expense_limit'})
            self.assertEqual(code, 201)
        employee_id = self.gen_id()
        today = datetime.utcnow().replace(hour=0, minute=0, second=0,
                                          microsecond=0)
        yesterday = today - timedelta(days=1)
        r_ids = []
        for r in [resources[0], resources[1], resources[2]]:
            r_ids.append(r['id'])
            self.resources_collection.update_one(filter={
                '_id': r['id']
            },
                update={'$set': {
                    'employee_id': employee_id,
                    'pool_id': self.pool_id
                }})
            self.expenses.append({
                'cost': 99.1234,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': yesterday,
                'sign': 1,
            })
        self.update_resource_info_by_expenses(r_ids)
        new_now = datetime.utcnow()
        with freeze_time(new_now):
            self.resource_discovery_call(self.instances)
            code, _ = self.client.process_resource_violations(self.org_id)
            self.assertEqual(p_alerts.call_count, 1)
            self.assertEqual(code, 204)
            for r in [resources[0], resources[1], resources[2]]:
                _, resp = self.client.resource_limit_hits_list(r['id'])
                self.assertEqual(len(resp['limit_hits']), 1)
                for limit_hit in resp['limit_hits']:
                    self.assertEqual(limit_hit['expense_value'], 99.1234)
                    self.assertEqual(limit_hit['constraint_limit'], 10)
                    self.assertEqual(
                        limit_hit['state'], ConstraintLimitStates.RED.value)
        new_limit_hit_map = [
            (99.1234, ConstraintLimitStates.RED.value),
            (5, ConstraintLimitStates.GREEN.value)
        ]
        r_ids = []
        for r in [resources[0], resources[1], resources[2]]:
            r_ids.append(r['id'])
            self.expenses.append({
                'cost': 5,
                'cloud_account_id': self.cloud_acc_id,
                'resource_id': r['id'],
                'date': today,
                'sign': 1
            })
        self.update_resource_info_by_expenses(r_ids)
        with freeze_time(new_now):
            self.resource_discovery_call(self.instances)
            code, _ = self.client.process_resource_violations(self.org_id)
            self.assertEqual(p_alerts.call_count, 2)
            self.assertEqual(code, 204)
            for r in [resources[0], resources[1], resources[2]]:
                _, resp = self.client.resource_limit_hits_list(r['id'])
                self.assertEqual(len(resp['limit_hits']), 2)
                counter = 0
                for limit_hit in resp['limit_hits']:
                    hit_value, hit_state = new_limit_hit_map[counter]
                    hit_key = 'ttl_value' if (
                            limit_hit['type'] == 'TTL') else 'expense_value'
                    self.assertEqual(limit_hit[hit_key], hit_value)
                    self.assertEqual(limit_hit['constraint_limit'], 10)
                    self.assertEqual(
                        limit_hit['state'], hit_state)
                    counter += 1

    def test_released_booking_schedule(self):
        patch(PROCESS_RESOURCES).start()
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        self._mock_auth_user(self.user_id)
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        self.instances = self.get_instances(self.org_id)
        resources = self.resource_discovery_call(self.instances)
        resource = resources[0]
        self.resources_collection.update_one(
            filter={
                '_id': resource['id']
            },
            update={'$set': {
                'shareable': True}}
        )
        now = int(datetime.utcnow().timestamp())
        released_at = now - 100
        acquired_since = released_at - NEWLY_DISCOVERED_TIME
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
            'acquired_since': acquired_since,
            'released_at': released_at,
        }
        code, data = self.client.shareable_book_create(self.org_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        code, data = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        # rule deactivated, shareable booking released, resource discover
        self.assertEqual(p_publish_activities.call_count, 3)

    def test_released_booking_future(self):
        patch(PROCESS_RESOURCES).start()
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        self._mock_auth_user(self.user_id)
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        self.instances = self.get_instances(self.org_id)
        resources = self.resource_discovery_call(self.instances)
        resource = resources[0]
        self.resources_collection.update_one(
            filter={
                '_id': resource['id']
            },
            update={'$set': {
                'shareable': True}}
        )
        now = int(datetime.utcnow().timestamp())
        released_at = now + 2 * NEWLY_DISCOVERED_TIME
        acquired_since = now
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
            'acquired_since': acquired_since,
            'released_at': released_at,
        }
        code, data = self.client.shareable_book_create(self.org_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        code, data = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        # rule deactivated, resource discover - 0 released bookings
        self.assertEqual(p_publish_activities.call_count, 2)

    def test_released_booking_past(self):
        patch(PROCESS_RESOURCES).start()
        patch('rest_api_server.controllers.shareable_resource.'
              'ShareableBookingController.publish_task').start()
        self._mock_auth_user(self.user_id)
        p_publish_activities = patch(
            'rest_api_server.controllers.base.BaseController.'
            'publish_activities_task'
        ).start()
        self.instances = self.get_instances(self.org_id)
        resources = self.resource_discovery_call(self.instances)
        resource = resources[0]
        self.resources_collection.update_one(
            filter={
                '_id': resource['id']
            },
            update={'$set': {
                'shareable': True}}
        )
        now = int(datetime.utcnow().timestamp())
        released_at = now - 2 * NEWLY_DISCOVERED_TIME
        acquired_since = released_at - NEWLY_DISCOVERED_TIME
        schedule_book = {
            'resource_id': resource['id'],
            'acquired_by_id': self.employee['id'],
            'acquired_since': acquired_since,
            'released_at': released_at,
        }
        code, data = self.client.shareable_book_create(self.org_id,
                                                       schedule_book)
        self.assertEqual(code, 201)
        code, data = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        # rule deactivated + resource discovered - no released booking
        self.assertEqual(p_publish_activities.call_count, 2)

    def test_send_env_changes_activities_task(self):
        patch('rest_api_server.controllers.base.'
              'BaseController.publish_activities_task').start()
        token_info = {
            'user_id': self.user_id,
            'valid_until': datetime.utcnow().timestamp() * 2
        }
        patch('rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.get_meta_by_token', return_value=token_info
              ).start()
        alert_params = {
            'pool_id': self.org['pool_id'],
            'threshold': 0,
            'contacts': [{'slack_channel_id': 'channel',
                          'slack_team_id': 'team'}],
            'based': 'env_change'
        }
        code, alert = self.client.alert_create(self.org['pool_id'],
                                               alert_params)
        self.assertEqual(code, 201)
        resources = self.resource_discovery_call(self.instances)
        resource = resources[0]
        resource2 = resources[1]
        self.resources_collection.update_many(
            filter={'_id': {'$in': [resource['id'], resource2['id']]}},
            update={'$set': {'shareable': True}}
        )

        # resource state changed: active -> not active
        p_send_msg = patch('rest_api_server.controllers.base.'
                           'BaseController.publish_activities_task').start()
        patch(
            'rest_api_server.controllers.resource_observer.'
            'ResourceObserverController._clear_active_flags',
            return_value=[{'_id': resource2['id'],
                           'pool_id': self.org['pool_id'],
                           'shareable': True}]).start()
        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        meta = {
                'alert_id': alert['id'],
                'previous_state': 'Active',
                'new_state': 'Not Active'
        }
        p_send_msg.assert_has_calls([
            call(self.org_id, resource2['id'], 'resource',
                 'env_active_state_changed', meta,
                 'alert.violation.env_change')])

    def test_send_env_changes_activities_task_without_alert(self):
        token_info = {
            'user_id': self.user_id,
            'valid_until': datetime.utcnow().timestamp() * 2
        }
        patch('rest_api_server.handlers.v1.base.'
              'BaseAuthHandler.get_meta_by_token', return_value=token_info
              ).start()
        resources = self.resource_discovery_call(self.instances)
        resource = resources[0]
        resource2 = resources[1]
        self.resources_collection.update_many(
            filter={'_id': {'$in': [resource['id'], resource2['id']]}},
            update={'$set': {'shareable': True}}
        )

        # resource state changed: active -> not active
        p_send_msg = patch('rest_api_server.controllers.base.'
                           'BaseController.publish_activities_task').start()
        patch(
            'rest_api_server.controllers.resource_observer.'
            'ResourceObserverController._clear_active_flags',
            return_value=[{'_id': resource2['id'],
                           'pool_id': self.org['pool_id'],
                           'shareable': True}]).start()
        code, _ = self.client.observe_resources(self.org_id)
        self.assertEqual(code, 204)
        meta = {
                'previous_state': 'Active',
                'new_state': 'Not Active'
        }
        p_send_msg.assert_has_calls([
            call(self.org_id, resource2['id'], 'resource',
                 'env_active_state_changed', meta,
                 'alert.violation.env_change')])

    def test_policy_constraint_limit_hit(self):
        patch('rest_api_server.controllers.limit_hit.LimitHitsController.'
              'send_alerts').start()
        code, pool = self.client.pool_create(
            self.org_id, {'name': 'pool1'})
        self.assertEqual(code, 201)
        resource = InstanceResource(
            cloud_resource_id='i-aaa',
            cloud_account_id=self.cloud_acc_id,
        )
        res = self.resource_discovery_call([resource])[0]
        self.resources_collection.update_one(
            filter={'_id': res['id']},
            update={'$set': {'employee_id': self.employee['id'],
                             'pool_id': pool['id'],
                             'first_seen': 1}})
        today = datetime.utcnow().replace(hour=0, minute=0, second=0,
                                          microsecond=0)
        self.expenses.append({
            'cost': 99.1234,
            'cloud_account_id': self.cloud_acc_id,
            'resource_id': res['id'],
            'date': today,
            'sign': 1,
        })
        self.update_resource_info_by_expenses([res['id']])
        code, constraint = self.client.pool_policy_create(
            pool['id'], {'limit': 1, 'type': 'daily_expense_limit'})
        self.assertEqual(code, 201)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        code, hits = self.client.resource_limit_hits_list(res['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits['limit_hits']), 1)
        self.assertEqual(hits['limit_hits'][0]['state'], 'red')
        self.assertEqual(hits['limit_hits'][0]['pool_id'], pool['id'])
        self.assertEqual(hits['limit_hits'][0]['type'], 'daily_expense_limit')

        with freeze_time(today):
            code, constraint = self.client.resource_constraint_create(
                res['id'], {'limit': int(today.timestamp()) + 10,
                            'type': 'ttl'})
        self.assertEqual(code, 201)
        code, _ = self.client.process_resource_violations(self.org_id)
        self.assertEqual(code, 204)
        code, hits = self.client.resource_limit_hits_list(res['id'])
        self.assertEqual(code, 200)
        self.assertEqual(len(hits['limit_hits']), 2)
        self.assertEqual(hits['limit_hits'][0]['state'], 'red')
        self.assertEqual(hits['limit_hits'][0]['pool_id'], pool['id'])
        self.assertEqual(hits['limit_hits'][0]['type'], 'daily_expense_limit')
        self.assertEqual(hits['limit_hits'][1]['state'], 'red')
        self.assertIsNone(hits['limit_hits'][1]['pool_id'])
        self.assertEqual(hits['limit_hits'][1]['type'], 'ttl')
