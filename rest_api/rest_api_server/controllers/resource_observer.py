import logging

from sqlalchemy import and_, false
from datetime import datetime
from pymongo import UpdateMany

from tools.cloud_adapter.model import ResourceTypes
from rest_api.rest_api_server.controllers.base import (BaseController, MongoMixin)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.cloud_resource_discover import CloudResourceDiscover
from rest_api.rest_api_server.controllers.limit_hit import LimitHitsController
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.controllers.cloud_account import CloudAccountController
from rest_api.rest_api_server.controllers.pool_alert import PoolAlertController
from rest_api.rest_api_server.controllers.shareable_resource import ShareableBookingController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import ThresholdBasedTypes, CloudTypes
from rest_api.rest_api_server.models.models import (Organization, CloudAccount,
                                                    ShareableBooking)
from rest_api.rest_api_server.utils import (
    raise_does_not_exist_exception, generate_discovered_cluster_resources_stat)

from tools.optscale_exceptions.common_exc import NotFoundException


LOG = logging.getLogger(__name__)
BULK_SIZE = 2000
NEWLY_DISCOVERED_TIME = 300  # 5 min
HOUR_IN_SEC = 3600


class ResourceObserverController(BaseController, MongoMixin):
    def _get_organization(self, organization_id):
        return self.session.query(Organization).filter(and_(
            Organization.deleted.is_(False),
            Organization.id == organization_id,
            Organization.is_demo.is_(false())
        )).one_or_none()

    def _get_cloud_accounts(self, organization_id):
        return self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == organization_id,
            CloudAccount.deleted.is_(False)
        ).all()

    def _clear_active_flags(self, cloud_acc_id_discovered_res_ids, resource_type):
        resources_ = {}
        for cloud_acc_id, active_res_ids in cloud_acc_id_discovered_res_ids.items():
            res = self.resources_collection.find({
                '_id': {'$nin': active_res_ids},
                'cloud_account_id': cloud_acc_id,
                'resource_type': resource_type.value,
                'active': True})
            resources_.update({r['_id']: r for r in res})
        inactive_res_ids = list(resources_.keys())
        if inactive_res_ids:
            self.resources_collection.update_many(
                filter={'_id': {'$in': inactive_res_ids}},
                update={'$unset': {'active': 1}}
            )
        return list(resources_.values())

    def _clear_clusters_active_flags(self, cluster_ids, organization_id):
        res = self.resources_collection.find({
            '_id': {'$nin': cluster_ids},
            'organization_id': organization_id,
            'active': True,
            'cluster_type_id': {'$exists': True}}
        )
        resources_ = {r['_id']: r for r in res}
        self.resources_collection.update_many(
            filter={'_id': {'$in': list(resources_.keys())}},
            update={'$unset': {'active': 1}}
        )
        return list(resources_.values())

    def observe(self, organization_id):
        now = int(datetime.utcnow().timestamp())
        last_run = now - NEWLY_DISCOVERED_TIME
        organization = self._get_organization(organization_id)
        if not organization:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        cloud_accounts_map = {}
        for cloud_account in self._get_cloud_accounts(organization_id):
            if cloud_account.type == CloudTypes.AZURE_TENANT:
                CloudAccountController(
                    self.session, self._config, self.token
                ).create_children_accounts(cloud_account)
                continue
            cloud_accounts_map[cloud_account.id] = cloud_account
        cloud_account_ids = list(cloud_accounts_map.keys())
        if not cloud_account_ids:
            return
        discover_controller = CloudResourceDiscover(
            self.session, self._config, self.token)
        cluster_ids = set()
        all_resources = []
        inactive_res = []
        for rss_type in ResourceTypes.objects():
            cloud_acc_id_res_ids = {x: [] for x in cloud_account_ids}
            resources = discover_controller.try_load_from_cache(
                organization_id, rss_type, {}, {}, None)
            resources_ids = []
            for r in resources:
                resources_ids.append(r.resource_id)
                all_resources.append(r)
                if r.cluster_id is not None:
                    cluster_ids.add(r.cluster_id)
                cloud_acc_id_res_ids[r.cloud_account_id].append(r.resource_id)
            inactive_res.extend(self._clear_active_flags(
                cloud_acc_id_res_ids, rss_type))
        inactive_clusters = self._clear_clusters_active_flags(
            list(cluster_ids), organization_id)
        inactive_res_list = []
        if inactive_res:
            inactive_res_list = [i for n, i in enumerate(inactive_res)
                                 if i not in inactive_res[n + 1:]]

        newly_discovered_resources = list(self.resources_collection.find({
            'cloud_account_id': {'$in': cloud_account_ids},
            'active': True,
            'created_at': {'$gte': last_run},
            'cluster_type_id': {'$exists': False}
        }))
        cluster_map = {c['_id']: c for c in self._get_clusters(
            list(cluster_ids))}
        rules_map = {}
        for r in newly_discovered_resources:
            applied_rules = r.get('applied_rules', [])
            for rule in applied_rules:
                rule_id = rule['id']
                if rule_id not in rules_map.keys():
                    rules_map[rule_id] = {'count': 0}
                    rules_map[rule_id].update(rule)
                rules_map[rule_id]['count'] += 1
        newly_discovered_stat = generate_discovered_cluster_resources_stat(
            newly_discovered_resources, cluster_map)
        for acc_id, stat in newly_discovered_stat.items():
            cloud_account = cloud_accounts_map[acc_id]
            meta = {
                'object_name': cloud_account.name,
                'stat': stat
            }
            self.publish_activities_task(
                organization_id, cloud_account.id, 'cloud_account',
                'resources_discovered', meta,
                'cloud_account.resources_discovered', add_token=True)
        pools_for_org = PoolController(
            self.session, self._config, self.token
        ).get_organization_pools(organization_id)
        pools_dict = {pool['id']: pool for pool in pools_for_org}
        for rule in rules_map.values():
            pool = pools_dict.get(rule['pool_id'])
            if not pool:
                raise_does_not_exist_exception('pool_id', rule['pool_id'])
            pool_name = pool.get('name')
            meta = {
                'pool_name': pool_name,
                'object_name': rule['name'],
                'rule_count': rule['count'],
                'pool_id': rule['pool_id']
            }
            self.publish_activities_task(
                organization_id, rule['id'], 'rule', 'rule_applied', meta,
                'rule.rule_applied', add_token=True)
        self._proccess_released_resources(all_resources, last_run)
        self._process_shareable_resources(
            inactive_clusters + inactive_res_list, organization,
            list(pools_dict.keys()))

    def process_violated_resources(self, organization_id):
        organization = self._get_organization(organization_id)
        if not organization:
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        cloud_account_ids = list(map(
            lambda x: x.id, self._get_cloud_accounts(organization_id)))
        if not cloud_account_ids:
            return
        lh_controller = LimitHitsController(
            self.session, self._config)
        resources = self.resources_collection.find({
            '$or': [
                {'cloud_account_id': {'$in': cloud_account_ids}},
                {'organization_id': organization_id}
            ],
            'active': True,
            'last_seen': {'$gte': int(
                datetime.utcnow().timestamp()) - HOUR_IN_SEC},
            'cluster_type_id': {'$exists': False}
        }, ['cloud_account_id', 'cluster_id', 'first_seen', 'pool_id',
            'total_cost', 'last_expense'])
        violated_resource_ids = set()
        bulk = []
        for r in resources:
            bulk.append(r)
            if len(bulk) == BULK_SIZE:
                res = lh_controller.process_resources(organization_id, bulk)
                violated_resource_ids.update(res)
                bulk.clear()
        if len(bulk):
            res = lh_controller.process_resources(organization_id, bulk)
            violated_resource_ids.update(res)
        self.update_violated_resources(list(violated_resource_ids),
                                       cloud_account_ids, organization_id)

    def _proccess_released_resources(self, resources, last_run):
        resource_ids = [x.resource_id for x in resources]
        ctrl = ShareableBookingController(self.session, self._config,
                                          self.token)
        now_ts = int(datetime.utcnow().timestamp())
        bookings = self.session.query(ShareableBooking).filter(and_(
            ShareableBooking.deleted.is_(False),
            ShareableBooking.resource_id.in_(resource_ids))).all()
        for booking in bookings:
            if (last_run <= booking.released_at < now_ts and
                    booking.released_at != 0):
                resource = list(filter(
                    lambda x: x.resource_id == booking.resource_id, resources))[0]
                resource = resource.to_dict()
                meta = {
                    'object_name': resource['name']
                }
                self.publish_activities_task(
                    booking.organization_id, resource['resource_id'],
                    'resource', 'shareable_booking_released', meta,
                    'resource.shareable_booking_released', add_token=True)

    def _process_shareable_resources(self, inactive_resources, organization,
                                     pool_ids):
        inactive_res = list(filter(lambda x: x.get('shareable'),
                                   inactive_resources))
        pool_alerts_map = PoolAlertController(
            self.session, self._config, self.token).get_pool_alerts_map(
            pool_ids, ThresholdBasedTypes.ENV_CHANGE)
        for resource in inactive_res:
            pool_id = resource['pool_id']
            meta = {
                'previous_state': 'Active',
                'new_state': 'Not Active'
            }
            if pool_alerts_map.get(resource['pool_id']):
                for alert_id in pool_alerts_map[pool_id]:
                    meta['alert_id'] = alert_id
                    self.publish_activities_task(
                        organization.id, resource['_id'], 'resource',
                        'env_active_state_changed', meta,
                        'alert.violation.env_change')
            else:
                self.publish_activities_task(
                    organization.id, resource['_id'], 'resource',
                    'env_active_state_changed', meta,
                    'alert.violation.env_change')

    def _get_clusters(self, cluster_ids):
        if not cluster_ids:
            return []
        return self.resources_collection.find({'_id': {'$in': cluster_ids}})

    def update_violated_resources(self, violated_resource_ids,
                                  cloud_account_ids, organization_id):
        self.resources_collection.bulk_write([
            UpdateMany(
                filter={
                    '$or': [
                        {'cloud_account_id': {'$in': cloud_account_ids}},
                        {'organization_id': organization_id}
                    ],
                    '_id': {'$in': violated_resource_ids},
                    'constraint_violated': {'$ne': True}
                },
                update={'$set': {'constraint_violated': True}}
            ),
            UpdateMany(
                filter={
                    '$or': [
                        {'cloud_account_id': {'$in': cloud_account_ids}},
                        {'organization_id': organization_id}
                    ],
                    '_id': {'$nin': violated_resource_ids},
                    'constraint_violated': True
                },
                update={'$unset': {'constraint_violated': 1}}
            ),
        ])


class ResourceObserverAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ResourceObserverController
