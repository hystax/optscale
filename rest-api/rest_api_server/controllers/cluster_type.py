import logging
import uuid

from datetime import datetime
from pymongo import ReturnDocument, UpdateMany, UpdateOne
from retrying import retry
from sqlalchemy import exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_

from rest_api_server.controllers.base import (BaseController, MongoMixin,
                                              PriorityMixin)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.controllers.employee import EmployeeController
from rest_api_server.controllers.rule_apply import RuleApplyController
from rest_api_server.exceptions import Err
from rest_api_server.models.enums import AssignmentRequestStatuses
from rest_api_server.models.models import (
    ClusterType, Organization, CloudAccount, AssignmentRequest,
    ResourceConstraint, ShareableBooking)
from rest_api_server.utils import (RetriableException, should_retry,
                                   encoded_tags, update_tags)

from optscale_exceptions.common_exc import (
    WrongArgumentsException, ConflictException, NotFoundException)


LOG = logging.getLogger(__name__)
RETRIES = dict(
    stop_max_attempt_number=6, wait_fixed=500,
    retry_on_exception=should_retry)
BULK_SIZE = 200


class ClusterTypeController(BaseController, MongoMixin, PriorityMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._cluster_inherited_fields = [
            'active', 'first_seen', 'last_seen', 'tags']

    def _get_model_type(self):
        return ClusterType

    def _validate(self, item, is_new=True, **kwargs):
        org_id = kwargs.get('organization_id')
        if org_id and not self.is_organization_exists(org_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, org_id])
        if is_new and self.is_cluster_type_exists(org_id, item.name):
            raise ConflictException(Err.OE0463, [item.name, org_id])

    def is_organization_exists(self, organization_id):
        return self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()

    def is_cluster_type_exists(self, organization_id, name):
        return self.session.query(
            exists().where(and_(
                self.model_type.organization_id == organization_id,
                self.model_type.name == name,
                self.model_type.deleted.is_(False)
            ))
        ).scalar()

    def list(self, organization_id, **kwargs):
        if not self.is_organization_exists(organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        return self._get_cluster_types_output(
            self._get_all_cluster_types(organization_id)
        )

    @retry(**RETRIES)
    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        model_type = self._get_model_type()
        try:
            org_c_types = super().list(
                organization_id=kwargs.get('organization_id'))
            kwargs['priority'] = len(org_c_types) + 1
            item = model_type(**kwargs)
            self._validate(item, True, **kwargs)
            self.session.add(item)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(ex)
        except TypeError as ex:
            raise WrongArgumentsException(Err.OE0004, [str(ex)])
        return item

    def delete_clusters(self, cluster_type):
        cluster_ids = self.resources_collection.distinct(
            '_id', {'cluster_type_id': cluster_type.id})
        if cluster_ids:
            updated_resources = self.resources_collection.update_many(
                filter={
                    'cluster_id': {'$in': cluster_ids},
                },
                update={'$unset': {'cluster_id': 1}}
            )
            self.resources_collection.update_many(
                filter={
                    '_id': {'$in': cluster_ids},
                },
                update={
                    '$unset': {'active': 1},
                    '$set': {'deleted_at': int(datetime.utcnow().timestamp())}
                }
            )
            if updated_resources.modified_count > 0:
                meta = {
                    'object_name': cluster_type.organization.name,
                    'cluster_type_name': cluster_type.name,
                    'cluster_type_id': cluster_type.id,
                    'modified_count': updated_resources.modified_count
                }
                self.publish_activities_task(
                    cluster_type.organization_id, cluster_type.organization_id,
                    'organization', 'cluster_resources_deleted', meta,
                    'organization.cluster_resources_deleted',
                    add_token=True)

    @retry(**RETRIES)
    def delete(self, item_id):
        now_ts = int(datetime.utcnow().timestamp())
        cluster_type = self.get(item_id)
        all_cluster_types = self._get_all_cluster_types(
            cluster_type.organization_id)
        try:
            if cluster_type.priority != len(all_cluster_types):
                self.set_priority(all_cluster_types, cluster_type,
                                  len(all_cluster_types))
            cluster_type.deleted_at = now_ts
            self.session.commit()
        except IntegrityError as exc:
            LOG.warning('Unable to delete cluster_type: %s', str(exc))
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(exc)
        self.delete_clusters(cluster_type)

    def _get_all_cluster_types(self, organization_id):
        query = self.session.query(
            ClusterType
        ).filter(
            and_(
                ClusterType.deleted.is_(False),
                ClusterType.organization_id == organization_id
            )
        ).order_by(ClusterType.priority)
        return query.all()

    def edit(self, item_id, action):
        cluster_type = self.get(item_id)
        all_cluster_types = self._get_all_cluster_types(
            cluster_type.organization_id)
        return self.change_priority(action, cluster_type, all_cluster_types,
                                    self._get_cluster_types_output)

    @staticmethod
    def _get_cluster_types_output(cluster_types):
        return {
            'cluster_types': [
                cluster_type.to_dict() for cluster_type in cluster_types
            ]
        }

    def get_tag_cluster_type_map(self, organization_id, encode_tags=False):
        tag_key_prop = 'tag_key' if not encode_tags else 'encoded_tag_key'
        res = {}
        for c_type in super().list(organization_id=organization_id):
            tag_key = getattr(c_type, tag_key_prop)
            current = res.get(tag_key)
            if not current or current.priority > c_type.priority:
                res[tag_key] = c_type
        return res

    def get_or_create(self, cluster):
        filters = {k: cluster.pop(k) for k in [
            'cluster_type_id', 'cloud_resource_id', 'deleted_at']}
        updates = {k: cluster.pop(k, None)
                   for k in self._cluster_inherited_fields}
        obj = self.resources_collection.find_one_and_update(
            filters, {
                '$setOnInsert': cluster,
                '$set': {k: v for k, v in updates.items() if v is not None}
            }, upsert=True,
            return_document=ReturnDocument.AFTER)
        return obj

    @staticmethod
    def _fill_cluster(organization_id, cluster_type, name, now):
        cl_id = ClusterTypeController.get_cluster_cloud_resource_id(
            cluster_type.name, name)
        return {
            '_id': str(uuid.uuid4()),
            'created_at': now,
            'deleted_at': 0,
            'organization_id': organization_id,
            'cluster_type_id': cluster_type.id,
            'resource_type': cluster_type.name,
            'active': False,
            'service_name': None,
            'cloud_resource_id': cl_id,
            'tags': {},
        }

    @staticmethod
    def _set_cluster_lifetime_fields(cluster, changes):
        tag_exclusions = set()
        for change in changes:
            cluster['active'] = cluster.get(
                'active', False) | change.get('active', False)
            if not cluster.get('tags'):
                cluster['tags'] = change['tags']
            else:
                for tag_k, tag_v in change['tags'].items():
                    if tag_k in tag_exclusions:
                        continue
                    if cluster['tags'].get(tag_k) is None:
                        cluster['tags'][tag_k] = tag_v
                    elif cluster['tags'][tag_k] != tag_v:
                        cluster['tags'].pop(tag_k, None)
                        tag_exclusions.add(tag_k)
            if change.get('last_seen'):
                if not cluster.get('last_seen'):
                    cluster['last_seen'] = change['last_seen']
                else:
                    cluster['last_seen'] = max(
                        cluster['last_seen'], change['last_seen'])
            if change.get('first_seen'):
                if not cluster.get('first_seen'):
                    cluster['first_seen'] = change['first_seen']
                else:
                    cluster['first_seen'] = min(
                        cluster['first_seen'], change['first_seen'])

    def sync_clusters(self, clusters_map, exclusions):
        updates = []
        cluster_resources_map = {}
        cluster_ids = list(clusters_map.keys())
        resources = self.resources_collection.find({
            'cluster_id': {'$in': cluster_ids},
            'deleted_at': 0,
            'cloud_resource_id': {'$nin': exclusions},
            'cloud_resource_hash': {'$nin': exclusions}
        })
        for r in resources:
            cluster_id = r.get('cluster_id')
            if not cluster_resources_map.get(cluster_id):
                cluster_resources_map[cluster_id] = []
            cluster_resources_map[cluster_id].append({
                'first_seen': r.get('first_seen'),
                'last_seen': r.get('last_seen'),
                'active': r.get('active', False),
                'tags': r.get('tags', {})
            })

        for cluster_id, cluster in clusters_map.items():
            changes = cluster_resources_map.get(cluster_id, [])
            if changes:
                self._set_cluster_lifetime_fields(cluster, changes)
                updates.append(UpdateMany(
                    filter={'_id': cluster_id},
                    update={'$set': {k: cluster[k]
                                     for k in self._cluster_inherited_fields
                                     if cluster.get(k) is not None}}
                    ))
        if updates:
            self.resources_collection.bulk_write(updates)
        return self.resources_collection.find({
            '_id': {'$in': cluster_ids},
            'deleted_at': 0
        })

    @staticmethod
    def get_cluster_cloud_resource_id(cluster_type_name, cluster_name):
        return '%s/%s' % (cluster_type_name, cluster_name)

    @staticmethod
    def get_resource_cluster_type(resource, tag_cluster_type_map):
        cluster_type = None
        for k, v in resource.get('tags', {}).items():
            c_type_candidate = tag_cluster_type_map.get(k)
            if not c_type_candidate:
                continue
            if not cluster_type or cluster_type.priority > c_type_candidate.priority:
                cluster_type = c_type_candidate
        return cluster_type

    def bind_clusters(self, organization_id, resources, db_resources_map,
                      rules, is_report_import, now):
        tag_cluster_type_map = self.get_tag_cluster_type_map(
            organization_id)
        db_clusters_ids = {
            r.get('cluster_id') for r, _ in db_resources_map.values()
            if r.get('cluster_id') is not None}
        clusters_map = {
            c['_id']: c for c in self.resources_collection.find(
                {'_id': {'$in': list(db_clusters_ids)}, 'deleted_at': 0})}

        rss_cluster_requirement_map, clusters_definitions_map = {}, {}
        cluster_cid_changes_map = {}
        exclusions = set()
        for resource in resources:
            resource_unique_id = resource.get(
                'cloud_resource_id') or resource.get('cloud_resource_hash')
            if not resource_unique_id:
                continue
            db_resource, unique_field = db_resources_map.get(
                resource_unique_id, ({}, None))
            if db_resource:
                cluster_cid = clusters_map.get(
                    db_resource.get('cluster_id'), {}).get(unique_field)
                if not cluster_cid:
                    continue
                exclusions.add(resource_unique_id)
                cluster = clusters_definitions_map.get(cluster_cid)
                if not cluster:
                    cluster = clusters_map[db_resource['cluster_id']]
                    for reset_field in self._cluster_inherited_fields:
                        cluster.pop(reset_field, None)
            else:
                c_type = self.get_resource_cluster_type(
                    resource, tag_cluster_type_map)
                if not c_type:
                    continue
                c_name = resource.get('tags').get(c_type.tag_key)
                cluster_cid = self.get_cluster_cloud_resource_id(
                    c_type.name, c_name)
                cluster = clusters_definitions_map.get(cluster_cid)
                if not cluster:
                    cluster = self._fill_cluster(
                        organization_id, c_type, c_name, now)

            db_resource_tags = encoded_tags(
                db_resource.get('tags', {}), decode=True)
            resource_tags = update_tags(
                db_resource_tags, resource.get('tags', {}),
                is_report_import, decode=False)
            first_seen = resource.get('first_seen')
            if not first_seen:
                first_seen = db_resource.get('first_seen', now)
            last_seen = resource.get('last_seen')
            if not last_seen:
                db_resource.get('last_seen', now)
            change = {
                'first_seen': first_seen,
                'last_seen': last_seen,
                'active': resource.get('active', False),
                'tags': resource_tags
            }
            if not cluster_cid_changes_map.get(cluster_cid):
                cluster_cid_changes_map[cluster_cid] = []
            cluster_cid_changes_map[cluster_cid].append(change)
            clusters_definitions_map[cluster_cid] = cluster
            rss_cluster_requirement_map[resource_unique_id] = cluster_cid

        rac = RuleApplyController(self.session, self._config, self.token)
        for cluster_cid, cluster in clusters_definitions_map.items():
            changes = cluster_cid_changes_map.get(cluster_cid)
            if changes:
                self._set_cluster_lifetime_fields(cluster, changes)
            cluster, _ = rac.handle_assignment_data(
                organization_id, cluster, None, {}, rules)
            cluster['tags'] = encoded_tags(cluster['tags'])
            cluster = self.get_or_create(cluster)
            clusters_map[cluster['_id']] = cluster

        clusters_map = {c['cloud_resource_id']: c
                        for c in self.sync_clusters(clusters_map,
                                                    list(exclusions))}
        return {r_id: clusters_map.get(cluster_cid)
                for r_id, cluster_cid in rss_cluster_requirement_map.items()}


class ClusterTypeApplyController(ClusterTypeController):
    @staticmethod
    def fill_response(processed_resources, processed_cluster_types):
        return {
            "processed_resources": processed_resources,
            "processed_cluster_types": processed_cluster_types
        }

    def invalidate_assignment_requests(self, clustered_resource_ids, now,
                                       no_commit=True):
        self.session.query(AssignmentRequest).filter(and_(
            AssignmentRequest.deleted.is_(False),
            AssignmentRequest.status == AssignmentRequestStatuses.PENDING,
            AssignmentRequest.resource_id.in_(list(clustered_resource_ids))
        )).update({
            AssignmentRequest.status: AssignmentRequestStatuses.CANCELED,
            AssignmentRequest.deleted_at: now},
            synchronize_session=False)
        if not no_commit:
            self.session.commit()

    def delete_resources_constraints(self, organization_id,
                                     clustered_resource_ids, no_commit=True):
        self.session.query(ResourceConstraint).filter(and_(
            ResourceConstraint.deleted.is_(False),
            ResourceConstraint.organization_id == organization_id,
            ResourceConstraint.resource_id.in_(list(clustered_resource_ids))
        )).delete(synchronize_session=False)
        if not no_commit:
            self.session.commit()

    def delete_shareable_booking(self, clustered_resource_ids,
                                 no_commit=True):
        now = int(datetime.utcnow().timestamp())
        self.session.query(ShareableBooking).filter(and_(
            ShareableBooking.deleted.is_(False),
            ShareableBooking.resource_id.in_(
                clustered_resource_ids)
        )).update({
            ShareableBooking.deleted_at: now},
            synchronize_session=False)
        if not no_commit:
            self.session.commit()

    def reapply_clusters(self, organization_id, user_info):
        if not self.is_organization_exists(organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        org_ca_q = self.session.query(CloudAccount).filter(and_(
            CloudAccount.organization_id == organization_id,
            CloudAccount.deleted.is_(False)))
        ca_ids = [ca.id for ca in org_ca_q.all()]
        tag_cluster_type_map = self.get_tag_cluster_type_map(
            organization_id, encode_tags=True)
        if not ca_ids or not tag_cluster_type_map:
            return self.fill_response(0, [])

        employee = EmployeeController(
            self.session, self._config, self.token
        ).get_employee_by_user_and_organization(
            user_info['id'], organization_id)
        meta = {
            'object_name': employee.organization.name
        }
        self.publish_activities_task(
            employee.organization_id, employee.organization_id, 'organization',
            'cluster_types_processing_started', meta,
            'organization.cluster_types_processing_started', add_token=True)

        clusters_map = {}
        for c in self.resources_collection.find(
                {
                    'cluster_type_id': {
                        '$in': [c_type.id for c_type in tag_cluster_type_map.values()]
                    },
                    'deleted_at': 0
                }):
            for reset_field in self._cluster_inherited_fields:
                c.pop(reset_field, None)
            clusters_map[c['cloud_resource_id']] = c

        resources = self.resources_collection.find({
            'cloud_account_id': {'$in': ca_ids},
            'deleted_at': 0,
            'cluster_type_id': {'$exists': False},
            '$or': [{'tags.%s' % k: {'$exists': True}}
                    for k in tag_cluster_type_map.keys()]
        })

        now = int(datetime.utcnow().timestamp())
        total_count = 0
        cluster_cid_resources_map = {}
        cluster_cid_cluster_type_map = {}
        cluster_cid_changes_map = {}
        for resource in resources:
            total_count += 1
            c_type = self.get_resource_cluster_type(
                resource, tag_cluster_type_map)
            if not c_type:
                continue
            c_name = resource.get('tags').get(c_type.encoded_tag_key)
            cluster_cid = self.get_cluster_cloud_resource_id(
                c_type.name, c_name)
            cluster = clusters_map.get(cluster_cid)
            if not cluster:
                cluster = self._fill_cluster(
                    organization_id, c_type, c_name, now)
            change = {
                'first_seen': resource.get('first_seen'),
                'last_seen': resource.get('last_seen'),
                'active': resource.get('active', False),
                'tags': resource.get('tags', {})
            }
            if not cluster_cid_changes_map.get(cluster_cid):
                cluster_cid_changes_map[cluster_cid] = []
            cluster_cid_changes_map[cluster_cid].append(change)
            clusters_map[cluster_cid] = cluster
            if not cluster_cid_resources_map.get(cluster_cid):
                cluster_cid_resources_map[cluster_cid] = []
            cluster_cid_resources_map[cluster_cid].append(resource)
            cluster_cid_cluster_type_map[cluster_cid] = c_type

        rac = RuleApplyController(self.session, self._config, self.token)
        _, employee_allowed_pools = rac.collect_relations(ca_ids)
        rules = rac.get_valid_rules(organization_id, employee_allowed_pools)
        for cluster in clusters_map.copy().values():
            changes = cluster_cid_changes_map.get(cluster['cloud_resource_id'], [])
            if changes:
                self._set_cluster_lifetime_fields(cluster, changes)
            cluster['tags'] = encoded_tags(cluster.get('tags', {}), decode=True)
            cluster, _ = rac.handle_assignment_data(
                organization_id, cluster, None, {}, rules)
            cluster['tags'] = encoded_tags(cluster['tags'])
            cluster = self.get_or_create(cluster)
            clusters_map[cluster['cloud_resource_id']] = cluster

        cluster_types_apply_stat = {}
        new_clustered_resource_ids, clustered_resource_ids = [], []
        resource_update_chunk = []
        for cluster_cid, resources in cluster_cid_resources_map.items():
            cluster = clusters_map.get(cluster_cid)
            c_type = cluster_cid_cluster_type_map.get(cluster_cid)
            if not cluster or not cluster_cid_cluster_type_map:
                continue

            if not cluster_types_apply_stat.get(c_type.id):
                cluster_types_apply_stat[c_type.id] = {
                    'id': c_type.id,
                    'name': c_type.name,
                    'clustered_resources_count': 0,
                    'clusters_count': 0
                }
            cluster_types_apply_stat[c_type.id][
                'clustered_resources_count'] += len(resources)
            cluster_types_apply_stat[c_type.id]['clusters_count'] += 1

            for resource in resources:
                clustered_resource_ids.append(resource['_id'])
                if resource.get('cluster_id') == cluster['_id']:
                    continue
                new_clustered_resource_ids.append(resource['_id'])
                for prop in ['pool_id', 'employee_id']:
                    resource[prop] = cluster.get(prop)
                resource['applied_rules'] = cluster.get('applied_rules', [])
                resource['cluster_id'] = cluster['_id']
                resource_update_fields = ['pool_id', 'employee_id',
                                          'cluster_id', 'applied_rules']
                if resource.get('shareable'):
                    resource['shareable'] = False
                    resource_update_fields.append('shareable')
                resource_update_chunk.append(UpdateOne(
                    filter={'_id': resource['_id']},
                    update={
                        '$set': {
                            k: resource.get(k)
                            for k in resource_update_fields
                        },
                    },
                ))

        args = ['cluster_id', 'cluster_name', 'clustered_resources_count',
                'clusters_count']
        for c_type_info in cluster_types_apply_stat.values():
            meta = {k: c_type_info.get(k) for k in args}
            meta.update({'object_name': c_type_info['name']})
            self.publish_activities_task(
                organization_id, c_type_info['id'], 'cluster_type',
                'cluster_type_applied', meta,
                'cluster_type.cluster_type_applied', add_token=True)

        for i in range(0, len(resource_update_chunk), BULK_SIZE):
            self.resources_collection.bulk_write(
                resource_update_chunk[i:i + BULK_SIZE])
            self.invalidate_assignment_requests(
                new_clustered_resource_ids[i:i + BULK_SIZE], now, no_commit=True)
            self.delete_resources_constraints(
                organization_id, new_clustered_resource_ids[i:i + BULK_SIZE],
                no_commit=True)
            self.delete_shareable_booking(
                new_clustered_resource_ids[i:i + BULK_SIZE], no_commit=True)
        self.resources_collection.bulk_write([UpdateMany(
            filter={'$and': [
                {'cloud_account_id': {'$in': ca_ids}},
                {'_id': {'$nin': clustered_resource_ids}},
                {'cluster_id': {'$exists': True}}
            ]},
            update={'$unset': {'cluster_id': 1}}
        )])
        self.delete_empty_clusters(organization_id, ca_ids)
        self.session.commit()
        meta = {
            'object_name': employee.organization.name,
            'total': total_count
        }
        self.publish_activities_task(
            employee.organization_id, employee.organization_id, 'organization',
            'cluster_types_processing_done', meta,
            'organization.cluster_types_processing_done', add_token=True)
        return self.fill_response(
            total_count, list(cluster_types_apply_stat.values()))

    def delete_empty_clusters(self, organization_id, cloud_account_ids):
        cluster_ids = self.resources_collection.distinct(
            'cluster_id', {'cloud_account_id': {'$in': cloud_account_ids}})
        now = int(datetime.utcnow().timestamp())
        self.resources_collection.update_many(
            filter={
                '_id': {'$nin': cluster_ids},
                'organization_id': organization_id,
                'cluster_type_id': {'$exists': True},
                'deleted_at': 0
            },
            update={'$set': {'deleted_at': now}}
        )


class ClusterTypeAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ClusterTypeController


class ClusterTypeApplyAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ClusterTypeApplyController
