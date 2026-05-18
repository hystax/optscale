import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, exists

from rest_api.rest_api_server.utils import check_list_attribute, \
    check_dict_attribute, encode_string
from tools.optscale_exceptions.common_exc import (
    ConflictException, WrongArgumentsException, NotFoundException)
from rest_api.rest_api_server.controllers.base import (
    BaseController, OrganizationValidatorMixin, MongoMixin,
    ResourceFormatMixin)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.cloud_resource import (
    CloudResourceController
)
from rest_api.rest_api_server.models.models import (
    PowerSchedule, PowerScheduleTrigger, CloudAccount
)
from rest_api.rest_api_server.exceptions import Err
from tools.cloud_adapter.cloud import Cloud as CloudAdapter
from tools.cloud_adapter.exceptions import (
    ResourceNotFound, InvalidResourceStateException)

LOG = logging.getLogger(__name__)


class PowerScheduleController(BaseController, OrganizationValidatorMixin,
                              MongoMixin, ResourceFormatMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._power_schedule_trigger_ctrl = None

    def _get_model_type(self):
        return PowerSchedule

    def _validate(self, item, is_new=True, **kwargs):
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        ps_exists = query.scalar()
        if ps_exists:
            raise ConflictException(Err.OE0149, [
                self.model_type.__name__, kwargs['name']])
        if (item.end_date and item.start_date and
                item.start_date >= item.end_date):
            raise WrongArgumentsException(
                Err.OE0541, ['start_date', 'end_date'])
        now = int(datetime.now(tz=timezone.utc).timestamp())
        end_date = kwargs.get('end_date')
        if isinstance(end_date, int) and end_date < now:
            raise WrongArgumentsException(Err.OE0461, ['end_date'])

    def _get_tag_matched_resources(self, power_schedule, explicit_cloud_ids,
                                   live=True):
        """Return resources matching the schedule's tag_selector.

        When live=False (list endpoint, count only) only MongoDB is queried.
        When live=True AWS describe APIs are also called for the regions known
        from MongoDB.
        """
        tag_selector = power_schedule.get('tag_selector')
        if not tag_selector or not isinstance(tag_selector, dict):
            return []
        tags = tag_selector.get('tags', {})
        if not tags:
            return []
        resource_types = set(tag_selector.get(
            'resource_types',
            ['Instance', 'RDS Instance', 'Aurora Cluster']))

        org_id = power_schedule.get('organization_id')
        aws_accounts = [
            ca for ca in self.session.query(CloudAccount).filter(
                CloudAccount.organization_id == org_id,
                CloudAccount.deleted_at == 0,
            ).all()
            if ca.type.value == 'aws_cnr'
        ]
        if not aws_accounts:
            return []

        ca_ids = [ca.id for ca in aws_accounts]

        if not live:
            # Fast path: count using MongoDB only (no AWS calls).
            mongo_q = {'active': True,
                       'resource_type': {'$in': list(resource_types)},
                       'cloud_account_id': {'$in': ca_ids}}
            for k, v in tags.items():
                mongo_q[f'tags.{encode_string(k)}'] = v
            results = []
            seen = set()
            for doc in self.resources_collection.find(mongo_q):
                crid = doc.get('cloud_resource_id')
                if crid and crid not in explicit_cloud_ids and crid not in seen:
                    seen.add(crid)
                    results.append(doc)
            return results

        # Live path: query AWS using regions known from MongoDB.
        mongo_regions = list(self.resources_collection.distinct(
            'region',
            {'active': True,
             'cloud_account_id': {'$in': ca_ids},
             'resource_type': {'$in': list(resource_types)}},
        )) or ['us-east-1']

        results = []
        seen = set()

        def _add(r, ca):
            key = (ca.id, r['cloud_resource_id'])
            if key not in seen and r['cloud_resource_id'] not in explicit_cloud_ids:
                seen.add(key)
                r.update({'cloud_account_id': ca.id,
                          'organization_id': org_id,
                          'cloud_account_name': ca.name})
                results.append(r)

        for ca in aws_accounts:
            try:
                config = dict(ca.decoded_config)
                config['type'] = ca.type.value
                adapter = CloudAdapter.get_adapter(config)
            except Exception as exc:
                LOG.error('CloudAdapter init error ca=%s: %s', ca.id, exc)
                continue

            for region in mongo_regions:
                if 'Instance' in resource_types:
                    try:
                        for r in adapter.describe_instances_by_tags(tags, region):
                            _add(r, ca)
                    except Exception as exc:
                        LOG.warning('EC2 describe ca=%s region=%s: %s',
                                    ca.id, region, exc)

                if 'RDS Instance' in resource_types:
                    try:
                        for r in adapter.describe_rds_instances_by_tags(tags, region):
                            _add(r, ca)
                    except Exception as exc:
                        LOG.warning('RDS describe ca=%s region=%s: %s',
                                    ca.id, region, exc)

                if 'Aurora Cluster' in resource_types:
                    try:
                        for r in adapter.describe_aurora_clusters_by_tags(tags, region):
                            _add(r, ca)
                    except Exception as exc:
                        LOG.warning('Aurora describe ca=%s region=%s: %s',
                                    ca.id, region, exc)

        return results

    @staticmethod
    def _format_live_resource(r):
        rid = r.get('cloud_resource_id', '')
        return {
            'id': None,
            'cloud_resource_id': rid,
            'name': r.get('name', rid),
            'resource_type': r.get('resource_type', 'Instance'),
            'active': True,
            'tag_matched': True,
            'cloud_account_id': r.get('cloud_account_id', ''),
            'organization_id': r.get('organization_id', ''),
            'tags': r.get('tags', {}),
            'meta': {
                'stopped_allocated': r.get('stopped_allocated', False),
                'flavor': r.get('flavor'),
                'source_cluster_id': r.get('source_cluster_id'),
            },
            'region': r.get('region', ''),
            'pool_id': None,
            'details': {
                'region': r.get('region', ''),
                'cloud_name': r.get('cloud_account_name', ''),
                'cloud_type': 'aws_cnr',
                'owner_name': '',
                'pool_name': '',
                'pool_purpose': '',
            },
        }

    def _enrich_explicit_state(self, explicit_resources):
        """Update meta.stopped_allocated in-place via live AWS calls."""
        groups = defaultdict(list)
        for r in explicit_resources:
            ca_id = r.get('cloud_account_id', '')
            region = r.get('region', '')
            rtype = r.get('resource_type', '')
            if ca_id and region and rtype in (
                    'Instance', 'RDS Instance', 'MSK Cluster'):
                groups[(ca_id, region, rtype)].append(r)
        if not groups:
            return
        ca_ids = list({k[0] for k in groups})
        accounts = {
            ca.id: ca
            for ca in self.session.query(CloudAccount).filter(
                CloudAccount.id.in_(ca_ids),
                CloudAccount.deleted_at == 0,
            ).all()
            if ca.type.value == 'aws_cnr'
        }
        adapters = {}
        for ca_id in ca_ids:
            ca = accounts.get(ca_id)
            if not ca:
                continue
            try:
                config = dict(ca.decoded_config)
                config['type'] = ca.type.value
                adapters[ca_id] = CloudAdapter.get_adapter(config)
            except Exception as exc:
                LOG.error('CloudAdapter init ca=%s: %s', ca_id, exc)
        for (ca_id, region, rtype), resources in groups.items():
            adapter = adapters.get(ca_id)
            if not adapter:
                continue
            ids = [r['cloud_resource_id'] for r in resources
                   if r.get('cloud_resource_id')]
            try:
                if rtype == 'Instance':
                    state_map = adapter.get_ec2_instances_state(ids, region)
                elif rtype == 'RDS Instance':
                    state_map = adapter.get_rds_instances_state(ids, region)
                elif rtype == 'MSK Cluster':
                    state_map = adapter.get_msk_clusters_state(ids, region)
                else:
                    continue
                for r in resources:
                    crid = r.get('cloud_resource_id')
                    if crid in state_map:
                        if not r.get('meta'):
                            r['meta'] = {}
                        r['meta']['stopped_allocated'] = state_map[crid]
            except Exception as exc:
                LOG.warning('State enrich ca=%s region=%s rtype=%s: %s',
                            ca_id, region, rtype, exc)

    def _set_resources(self, power_schedule, show_resources=False):
        explicit = list(self.resources_collection.find(
            {'power_schedule': power_schedule['id']}))
        explicit_cloud_ids = {r.get('cloud_resource_id') for r in explicit}
        tag_matched = self._get_tag_matched_resources(
            power_schedule, explicit_cloud_ids, live=show_resources)
        power_schedule['resources_count'] = len(explicit) + len(tag_matched)
        if show_resources:
            self._enrich_explicit_state(explicit)
            power_schedule['resources'] = []
            res_ctrl = CloudResourceController(
                self.session, self._config, self.token)
            for resource in explicit:
                resource = self.format_resource(resource)
                resource.update(
                    {'details': res_ctrl.get_resource_details(resource)})
                power_schedule['resources'].append(resource)
            # Look up tag-matched resources in MongoDB for pool/owner data
            tag_cloud_ids = [r['cloud_resource_id'] for r in tag_matched
                             if r.get('cloud_resource_id')]
            mongo_by_crid = {}
            if tag_cloud_ids:
                for doc in self.resources_collection.find(
                    {'cloud_resource_id': {'$in': tag_cloud_ids}}
                ):
                    crid = doc.get('cloud_resource_id')
                    if crid:
                        mongo_by_crid[crid] = doc
            for resource in tag_matched:
                crid = resource.get('cloud_resource_id')
                mongo_doc = mongo_by_crid.get(crid)
                if mongo_doc:
                    formatted = self.format_resource(dict(mongo_doc))
                    formatted.setdefault('meta', {})
                    formatted['meta']['stopped_allocated'] = resource.get(
                        'stopped_allocated', False)
                    formatted['tag_matched'] = True
                    formatted.update(
                        {'details': res_ctrl.get_resource_details(formatted)})
                else:
                    formatted = self._format_live_resource(resource)
                power_schedule['resources'].append(formatted)

    @staticmethod
    def _validate_tag_selector(tag_selector):
        if tag_selector is None:
            return
        if not isinstance(tag_selector, dict):
            raise WrongArgumentsException(Err.OE0219, ['tag_selector'])
        tags = tag_selector.get('tags')
        if tags is not None and not isinstance(tags, dict):
            raise WrongArgumentsException(Err.OE0219, ['tag_selector.tags'])
        resource_types = tag_selector.get('resource_types')
        if resource_types is not None:
            check_list_attribute('tag_selector.resource_types', resource_types)

    @staticmethod
    def _validate_triggers(triggers):
        check_list_attribute('triggers', triggers)
        times = []
        required = {'action', 'time'}
        optional = {'days_of_week'}
        allowed = required | optional
        for trigger in triggers:
            check_dict_attribute('trigger', trigger)
            unexpected = set(trigger.keys()) - allowed
            if unexpected:
                raise WrongArgumentsException(
                    Err.OE0212, [', '.join(unexpected)])
            missing = required - set(trigger.keys())
            if missing:
                raise WrongArgumentsException(Err.OE0216, [missing.pop()])
            days_of_week = trigger.get('days_of_week')
            if days_of_week is not None:
                if not isinstance(days_of_week, list):
                    raise WrongArgumentsException(Err.OE0219, ['days_of_week'])
                for d in days_of_week:
                    if not isinstance(d, int) or d < 0 or d > 6:
                        raise WrongArgumentsException(
                            Err.OE0219, ['days_of_week'])
            time = trigger.get('time')
            if time in times:
                raise WrongArgumentsException(Err.OE0562, [time])
            times.append(time)

    def _create_triggers(self, power_schedule_id, triggers):
        for trigger in triggers:
            t = dict(trigger)
            if 'days_of_week' in t and t['days_of_week'] is not None:
                t['days_of_week'] = json.dumps(t['days_of_week'])
            self.session.add(PowerScheduleTrigger(
                power_schedule_id=power_schedule_id, **t))

    def _delete_triggers(self, power_schedule_id):
        self.session.query(PowerScheduleTrigger).filter(
            PowerScheduleTrigger.power_schedule_id == power_schedule_id,
        ).delete()

    def create(self, organization_id: str, **kwargs):
        self.check_organization(organization_id)
        start_date = kwargs.get('start_date')
        if start_date is None:
            kwargs['start_date'] = int(datetime.now(timezone.utc).timestamp())
        triggers = kwargs.pop("triggers", [])
        self._validate_triggers(triggers)
        tag_selector = kwargs.get('tag_selector')
        self._validate_tag_selector(tag_selector)
        if isinstance(tag_selector, dict):
            kwargs['tag_selector'] = json.dumps(tag_selector)
        self.check_create_restrictions(**kwargs)
        try:
            ps_id = str(uuid.uuid4())
            item = PowerSchedule(id=ps_id, organization_id=organization_id,
                                 **kwargs)
            self._validate(item, True, **kwargs)
            LOG.info("Creating %s with parameters %s",
                     self._get_model_type().__name__, kwargs)
            self.session.add(item)
            self._create_triggers(ps_id, triggers)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        except TypeError as ex:
            raise WrongArgumentsException(Err.OE0004, [str(ex)])
        power_schedule = item.to_dict()
        power_schedule['resources_count'] = 0
        self.publish_activities_task(
            organization_id, power_schedule["id"], "power_schedule",
            "power_schedule_created", {"object_name": power_schedule["name"]},
            "power_schedule.power_schedule_created"
        )
        return power_schedule

    def list(self, organization_id: str, **kwargs):
        if organization_id:
            self.check_organization(organization_id)
        result = []
        ps_list = super().list(organization_id=organization_id)
        for ps in ps_list:
            ps = ps.to_dict()
            self._set_resources(ps, show_resources=False)
            result.append(ps)
        return result

    def get_item(self, item_id: str):
        item = super().get(item_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, item_id])
        item = item.to_dict()
        self._set_resources(item, show_resources=True)
        return item

    def edit(self, item_id: str, **kwargs):
        item = super().get(item_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, item_id])
        triggers = kwargs.pop("triggers", None)
        if triggers is not None:
            self._validate_triggers(triggers)
            self._delete_triggers(item_id)
            self._create_triggers(item_id, triggers)
            if not kwargs:
                self.session.commit()
        tag_selector = kwargs.get('tag_selector')
        if tag_selector is not None:
            self._validate_tag_selector(tag_selector)
            kwargs['tag_selector'] = json.dumps(tag_selector) if isinstance(
                tag_selector, dict) else None
        if 'last_run_details' in kwargs:
            last_run_details = kwargs['last_run_details']
            kwargs['last_run_details'] = json.dumps(last_run_details) if isinstance(
                last_run_details, (list, dict)) else None
        super().edit(item_id, **kwargs)
        schedule = self.get_item(item_id)
        self._set_resources(schedule, show_resources=True)
        # not spam events on every schedule run
        if set(kwargs) - {'last_eval', 'last_run_error', 'last_run', 'last_run_details'}:
            self.publish_activities_task(
                item.organization_id, item_id, "power_schedule",
                "power_schedule_updated", {"object_name": item.name},
                "power_schedule.power_schedule_created"
            )
        return schedule

    def bulk_action(self, power_schedule_id: str, data: dict):
        item = super().get(power_schedule_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, power_schedule_id])
        action = data['action']
        instance_ids = data['instance_id']
        query_params = {'_id': {'$in': instance_ids},
                        'resource_type': {'$in': [
                            'Instance', 'RDS Instance', 'MSK Cluster',
                        ]}}
        if action == 'attach':
            query_params['active'] = True
        resources = self.resources_collection.find(query_params, ['_id'])
        res_exist = [x['_id'] for x in resources]
        if res_exist and action == 'attach':
            self.resources_collection.update_many(
                {'_id': {'$in': res_exist}},
                {'$set': {'power_schedule': power_schedule_id}})
        elif res_exist and action == 'detach':
            self.resources_collection.update_many(
                {'_id': {'$in': res_exist}},
                {'$unset': {'power_schedule': 1}})
        failed = [x for x in instance_ids if x not in res_exist]
        return {
            'failed': failed,
            'succeeded': res_exist
        }

    def delete(self, power_schedule_id):
        item = super().get(power_schedule_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, power_schedule_id])
        self.resources_collection.update_many(
            {'power_schedule': power_schedule_id},
            {'$unset': {'power_schedule': 1}})
        self.publish_activities_task(
            item.organization_id, power_schedule_id, "power_schedule",
            "power_schedule_deleted", {"object_name": item.name},
            "power_schedule.power_schedule_deleted"
        )
        self._delete_triggers(power_schedule_id)
        super().delete(power_schedule_id)

    def power_by_tags(self, organization_id: str, data: dict):
        """Immediately start or stop AWS resources matching ALL given tags."""
        action = data.get('action')
        tags = data.get('tags') or {}
        filter_ca_id = data.get('cloud_account_id')
        resource_types = data.get('resource_types') or ['Instance', 'RDS Instance']
        dry_run = bool(data.get('dry_run', False))

        if action not in ('power_on', 'power_off'):
            raise WrongArgumentsException(Err.OE0217, ['action'])
        if not tags or not isinstance(tags, dict):
            raise WrongArgumentsException(Err.OE0216, ['tags'])

        self.check_organization(organization_id)

        # Fetch AWS cloud accounts for this organization
        ca_q = self.session.query(CloudAccount).filter(
            CloudAccount.organization_id == organization_id,
            CloudAccount.deleted_at == 0,
        )
        if filter_ca_id:
            ca_q = ca_q.filter(CloudAccount.id == filter_ca_id)
        cloud_accounts = {
            ca.id: ca for ca in ca_q.all()
            if ca.type.value == 'aws_cnr'
        }
        if not cloud_accounts:
            empty = {'matched': 0, 'action': action, 'matched_resources': []}
            if not dry_run:
                empty.update({'succeeded': 0, 'failed': 0})
            return empty

        # MongoDB AND query: resource must carry every specified tag
        mongo_q = {
            'active': True,
            'resource_type': {'$in': resource_types},
            'cloud_account_id': {'$in': list(cloud_accounts.keys())},
        }
        for key, value in tags.items():
            mongo_q[f'tags.{encode_string(key)}'] = value

        resources = list(self.resources_collection.find(mongo_q))

        matched_resources = [
            {
                'id': str(r.get('_id', r.get('cloud_resource_id', ''))),
                'name': r.get('name') or r.get('cloud_resource_id', ''),
                'resource_type': r.get('resource_type', ''),
                'cloud_resource_id': r.get('cloud_resource_id', ''),
                'region': r.get('region', ''),
                'stopped_allocated': (
                    r.get('stopped_allocated')
                    if 'stopped_allocated' in r
                    else (r.get('meta') or {}).get('stopped_allocated')
                ),
                'cloud_account_id': r.get('cloud_account_id', ''),
            }
            for r in resources
        ]

        if dry_run or not resources:
            result = {
                'matched': len(resources),
                'action': action,
                'matched_resources': matched_resources,
            }
            if not dry_run:
                result.update({'succeeded': 0, 'failed': 0})
            return result

        # Group by cloud account
        by_account = defaultdict(list)
        for r in resources:
            by_account[r['cloud_account_id']].append(r)

        worker_action = ('start_instance' if action == 'power_on'
                         else 'stop_instance')
        succeeded = 0
        failed = 0
        succeeded_ids = []

        for ca_id, ca_resources in by_account.items():
            ca = cloud_accounts.get(ca_id)
            if not ca:
                failed += len(ca_resources)
                continue
            try:
                config = dict(ca.decoded_config)
                config['type'] = ca.type.value
                adapter = CloudAdapter.get_adapter(config)
            except Exception as exc:
                LOG.error('Cloud adapter init failed for %s: %s', ca_id, exc)
                failed += len(ca_resources)
                continue

            # Separate EC2, RDS, Aurora, MSK
            ec2_by_region = defaultdict(list)
            rds_list = []
            aurora_by_cluster = {}
            msk_list = []
            for r in ca_resources:
                rtype = r.get('resource_type')
                region = r.get('region', '')
                if rtype == 'Instance':
                    ec2_by_region[region].append(
                        (r['cloud_resource_id'], r['_id']))
                elif rtype == 'RDS Instance':
                    cluster_id = (r.get('meta') or {}).get('source_cluster_id')
                    if cluster_id:
                        aurora_by_cluster.setdefault(cluster_id,
                                                     (region, r['_id']))
                    else:
                        rds_list.append(
                            (r['cloud_resource_id'], region, r['_id']))
                elif rtype == 'MSK Cluster':
                    msk_list.append(
                        (r['cloud_resource_id'], region, r['_id']))

            if worker_action == 'start_instance':
                # Phase 1: start DB group + MSK (MSK fails gracefully)
                for db_id, region, res_id in rds_list:
                    try:
                        adapter.start_rds_instance([db_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('RDS start failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('RDS start error: %s', e)
                        failed += 1
                for cluster_id, (region, res_id) in aurora_by_cluster.items():
                    try:
                        adapter.start_aurora_cluster([cluster_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('Aurora start failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('Aurora start error: %s', e)
                        failed += 1
                for cluster_arn, region, res_id in msk_list:
                    try:
                        adapter.start_msk_cluster(cluster_arn, region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('MSK start failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('MSK start error: %s', e)
                        failed += 1
                # Wait for DB group before starting EC2
                for db_id, region, _ in rds_list:
                    try:
                        adapter.wait_rds_available(db_id, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for RDS %s: %s',
                                    db_id, exc)
                for cluster_id, (region, _) in aurora_by_cluster.items():
                    try:
                        adapter.wait_aurora_cluster_available(cluster_id, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for Aurora %s: %s',
                                    cluster_id, exc)
                # Phase 2: start EC2
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    res_ids = [p[1] for p in id_pairs]
                    try:
                        adapter.start_instance(ids, region)
                        succeeded += len(ids)
                        succeeded_ids.extend(res_ids)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('EC2 start failed: %s', e)
                        failed += len(ids)
                    except Exception as e:
                        LOG.error('EC2 start error: %s', e)
                        failed += len(ids)

            else:  # stop_instance
                # Phase 1: stop EC2 + MSK
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    res_ids = [p[1] for p in id_pairs]
                    try:
                        adapter.stop_instance(ids, region)
                        succeeded += len(ids)
                        succeeded_ids.extend(res_ids)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('EC2 stop failed: %s', e)
                        failed += len(ids)
                    except Exception as e:
                        LOG.error('EC2 stop error: %s', e)
                        failed += len(ids)
                for cluster_arn, region, res_id in msk_list:
                    try:
                        adapter.stop_msk_cluster(cluster_arn, region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('MSK stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('MSK stop error: %s', e)
                        failed += 1
                # Wait for EC2 to stop before stopping DB group
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    try:
                        adapter.wait_instances_stopped(ids, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for EC2 to stop '
                                    'in %s: %s', region, exc)
                # Phase 2: stop DB group
                for db_id, region, res_id in rds_list:
                    try:
                        adapter.stop_rds_instance([db_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('RDS stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('RDS stop error: %s', e)
                        failed += 1
                for cluster_id, (region, res_id) in aurora_by_cluster.items():
                    try:
                        adapter.stop_aurora_cluster([cluster_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('Aurora stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('Aurora stop error: %s', e)
                        failed += 1

        # Optimistically update stopped_allocated in MongoDB for acted resources
        if succeeded_ids:
            new_stopped = action == 'power_off'
            self.resources_collection.update_many(
                {'_id': {'$in': succeeded_ids}},
                {'$set': {'meta.stopped_allocated': new_stopped}}
            )

        return {
            'matched': len(resources),
            'succeeded': succeeded,
            'failed': failed,
            'action': action,
            'matched_resources': matched_resources,
        }

    def run_now(self, power_schedule_id: str, action: str) -> dict:
        """Immediately execute power_on or power_off for all schedule resources."""
        if action not in ('power_on', 'power_off'):
            raise WrongArgumentsException(Err.OE0217, ['action'])
        item = super().get(power_schedule_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, power_schedule_id])

        explicit = list(self.resources_collection.find(
            {'power_schedule': power_schedule_id, 'active': True}))
        explicit_cloud_ids = {r.get('cloud_resource_id') for r in explicit}

        ps_dict = item.to_dict()
        tag_live = self._get_tag_matched_resources(ps_dict, explicit_cloud_ids)
        tag_cids = [r['cloud_resource_id'] for r in tag_live
                    if r.get('cloud_resource_id')]
        tag_mongo = []
        if tag_cids:
            tag_mongo = list(self.resources_collection.find({
                'cloud_resource_id': {'$in': tag_cids},
                'active': True,
            }))
        # Deduplicate
        tag_mongo = [r for r in tag_mongo
                     if r.get('cloud_resource_id') not in explicit_cloud_ids]

        # Include live resources not yet in MongoDB (e.g. not yet discovered)
        mongo_cids = {r.get('cloud_resource_id') for r in tag_mongo}
        extra_live = [r for r in tag_live
                      if r.get('cloud_resource_id') and
                      r['cloud_resource_id'] not in mongo_cids and
                      r.get('cloud_resource_id') not in explicit_cloud_ids]

        all_resources = explicit + tag_mongo + extra_live
        LOG.info('run_now ps=%s action=%s explicit=%d tag_mongo=%d extra_live=%d total=%d',
                 power_schedule_id, action, len(explicit), len(tag_mongo),
                 len(extra_live), len(all_resources))
        for r in all_resources:
            LOG.info('run_now resource: crid=%s rtype=%s region=%s ca=%s src=%s',
                     r.get('cloud_resource_id'), r.get('resource_type'),
                     r.get('region'), r.get('cloud_account_id'),
                     'explicit' if r.get('power_schedule') else
                     ('mongo' if r.get('_id') else 'live'))
        if not all_resources:
            return {'matched': 0, 'succeeded': 0, 'failed': 0, 'action': action}

        ca_ids = list({r.get('cloud_account_id')
                       for r in all_resources if r.get('cloud_account_id')})
        cloud_accounts = {
            ca.id: ca
            for ca in self.session.query(CloudAccount).filter(
                CloudAccount.id.in_(ca_ids),
                CloudAccount.organization_id == item.organization_id,
                CloudAccount.deleted_at == 0,
            ).all()
            if ca.type.value == 'aws_cnr'
        }
        LOG.info('run_now ca_ids=%s cloud_accounts_found=%s', ca_ids,
                 list(cloud_accounts.keys()))

        worker_action = ('start_instance' if action == 'power_on'
                         else 'stop_instance')
        succeeded = 0
        failed = 0
        succeeded_ids = []

        by_account = defaultdict(list)
        for r in all_resources:
            ca_id = r.get('cloud_account_id', '')
            if ca_id:
                by_account[ca_id].append(r)

        for ca_id, ca_resources in by_account.items():
            ca = cloud_accounts.get(ca_id)
            if not ca:
                LOG.warning('run_now: no cloud account found for ca_id=%s '
                            '(skipping %d resources)', ca_id, len(ca_resources))
                failed += len(ca_resources)
                continue
            try:
                config = dict(ca.decoded_config)
                config['type'] = ca.type.value
                adapter = CloudAdapter.get_adapter(config)
            except Exception as exc:
                LOG.error('CloudAdapter init failed for %s: %s', ca_id, exc)
                failed += len(ca_resources)
                continue

            ec2_by_region = defaultdict(list)
            rds_list = []
            aurora_by_cluster = {}
            msk_list = []
            for r in ca_resources:
                rtype = r.get('resource_type')
                region = r.get('region', '')
                crid = r.get('cloud_resource_id', '')
                res_id = r.get('_id')
                LOG.info('run_now classify: crid=%s rtype=%s region=%s',
                         crid, rtype, region)
                if rtype == 'Instance':
                    ec2_by_region[region].append((crid, res_id))
                elif rtype == 'RDS Instance':
                    # source_cluster_id may be in meta (MongoDB) or top-level (live)
                    cluster_id = (
                        (r.get('meta') or {}).get('source_cluster_id')
                        or r.get('source_cluster_id')
                    )
                    if cluster_id:
                        aurora_by_cluster.setdefault(
                            cluster_id, (region, res_id))
                    else:
                        rds_list.append((crid, region, res_id))
                elif rtype == 'MSK Cluster':
                    msk_list.append((crid, region, res_id))

            LOG.info('run_now action=%s ec2_by_region=%s rds_list=%s',
                     worker_action,
                     {r: [x[0] for x in ids] for r, ids in ec2_by_region.items()},
                     [x[0] for x in rds_list])
            if worker_action == 'start_instance':
                # Phase 1: start DB group + MSK (MSK fails gracefully)
                for db_id, region, res_id in rds_list:
                    try:
                        LOG.info('run_now: starting RDS %s in %s', db_id, region)
                        adapter.start_rds_instance([db_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('run_now: RDS start failed (already running?): %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('RDS start error: %s', e)
                        failed += 1
                for cluster_id, (region, res_id) in aurora_by_cluster.items():
                    try:
                        adapter.start_aurora_cluster([cluster_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('Aurora start failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('Aurora start error: %s', e)
                        failed += 1
                for cluster_arn, region, res_id in msk_list:
                    try:
                        adapter.start_msk_cluster(cluster_arn, region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('MSK start failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('MSK start error: %s', e)
                        failed += 1
                # Wait for DB group to be available before starting EC2
                for db_id, region, _ in rds_list:
                    try:
                        adapter.wait_rds_available(db_id, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for RDS %s: %s',
                                    db_id, exc)
                for cluster_id, (region, _) in aurora_by_cluster.items():
                    try:
                        adapter.wait_aurora_cluster_available(cluster_id, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for Aurora %s: %s',
                                    cluster_id, exc)
                # Phase 2: start EC2
                LOG.info('run_now: Phase 2 EC2 start, ec2_by_region=%s',
                         {r: [p[0] for p in ps]
                          for r, ps in ec2_by_region.items()})
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    res_ids = [p[1] for p in id_pairs]
                    LOG.info('run_now: calling start_instance ids=%s region=%s',
                             ids, region)
                    try:
                        adapter.start_instance(ids, region)
                        succeeded += len(ids)
                        succeeded_ids.extend(res_ids)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('EC2 start failed: %s', e)
                        failed += len(ids)
                    except Exception as e:
                        LOG.error('EC2 start error: %s', e)
                        failed += len(ids)

            else:  # stop_instance
                # Phase 1: stop EC2 + MSK
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    res_ids = [p[1] for p in id_pairs]
                    try:
                        adapter.stop_instance(ids, region)
                        succeeded += len(ids)
                        succeeded_ids.extend(res_ids)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('EC2 stop failed: %s', e)
                        failed += len(ids)
                    except Exception as e:
                        LOG.error('EC2 stop error: %s', e)
                        failed += len(ids)
                for cluster_arn, region, res_id in msk_list:
                    try:
                        adapter.stop_msk_cluster(cluster_arn, region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('MSK stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('MSK stop error: %s', e)
                        failed += 1
                # Wait for EC2 to stop before stopping DB group
                for region, id_pairs in ec2_by_region.items():
                    ids = [p[0] for p in id_pairs]
                    try:
                        adapter.wait_instances_stopped(ids, region)
                    except Exception as exc:
                        LOG.warning('Timed out waiting for EC2 to stop '
                                    'in %s: %s', region, exc)
                # Phase 2: stop DB group
                for db_id, region, res_id in rds_list:
                    try:
                        adapter.stop_rds_instance([db_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('RDS stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('RDS stop error: %s', e)
                        failed += 1
                for cluster_id, (region, res_id) in aurora_by_cluster.items():
                    try:
                        adapter.stop_aurora_cluster([cluster_id], region)
                        succeeded += 1
                        succeeded_ids.append(res_id)
                    except (ResourceNotFound, InvalidResourceStateException) as e:
                        LOG.warning('Aurora stop failed: %s', e)
                        failed += 1
                    except Exception as e:
                        LOG.error('Aurora stop error: %s', e)
                        failed += 1

        if succeeded_ids:
            new_stopped = action == 'power_off'
            self.resources_collection.update_many(
                {'_id': {'$in': succeeded_ids}},
                {'$set': {'meta.stopped_allocated': new_stopped}}
            )

        return {
            'matched': len(all_resources),
            'succeeded': succeeded,
            'failed': failed,
            'action': action,
        }

    def get_resources_live_state(self, organization_id: str,
                                 resources: list) -> dict:
        """Return {cloud_resource_id: stopped_allocated} via live AWS calls."""
        self.check_organization(organization_id)
        by_account = defaultdict(list)
        for r in resources:
            ca_id = r.get('cloud_account_id', '')
            if ca_id and r.get('cloud_resource_id') and r.get('region'):
                by_account[ca_id].append(r)
        if not by_account:
            return {}
        ca_ids = list(by_account.keys())
        accounts = {
            ca.id: ca
            for ca in self.session.query(CloudAccount).filter(
                CloudAccount.id.in_(ca_ids),
                CloudAccount.organization_id == organization_id,
                CloudAccount.deleted_at == 0,
            ).all()
            if ca.type.value == 'aws_cnr'
        }
        adapters = {}
        for ca_id in ca_ids:
            ca = accounts.get(ca_id)
            if not ca:
                continue
            try:
                config = dict(ca.decoded_config)
                config['type'] = ca.type.value
                adapters[ca_id] = CloudAdapter.get_adapter(config)
            except Exception as exc:
                LOG.error('CloudAdapter init ca=%s: %s', ca_id, exc)
        result = {}
        for ca_id, res_list in by_account.items():
            adapter = adapters.get(ca_id)
            if not adapter:
                continue
            by_region_type = defaultdict(lambda: defaultdict(list))
            for r in res_list:
                by_region_type[r['region']][
                    r.get('resource_type', 'Instance')].append(
                    r['cloud_resource_id'])
            for region, by_type in by_region_type.items():
                ec2_ids = by_type.get('Instance', [])
                if ec2_ids:
                    try:
                        result.update(
                            adapter.get_ec2_instances_state(ec2_ids, region))
                    except Exception as exc:
                        LOG.warning('EC2 live_state ca=%s region=%s: %s',
                                    ca_id, region, exc)
                rds_ids = by_type.get('RDS Instance', [])
                if rds_ids:
                    try:
                        result.update(
                            adapter.get_rds_instances_state(rds_ids, region))
                    except Exception as exc:
                        LOG.warning('RDS live_state ca=%s region=%s: %s',
                                    ca_id, region, exc)
                msk_ids = by_type.get('MSK Cluster', [])
                if msk_ids:
                    try:
                        result.update(
                            adapter.get_msk_clusters_state(msk_ids, region))
                    except Exception as exc:
                        LOG.warning('MSK live_state ca=%s region=%s: %s',
                                    ca_id, region, exc)
        return result


class PowerScheduleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self) -> type:
        return PowerScheduleController
