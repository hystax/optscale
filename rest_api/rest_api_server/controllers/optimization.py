from sqlalchemy import and_
from functools import lru_cache

from rest_api.rest_api_server.controllers.base import (
    BaseController, MongoMixin, ResourceFormatMixin)
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.checklist import ChecklistController
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization, CloudAccount

from tools.optscale_exceptions.common_exc import (FailedDependency,
                                                  NotFoundException)

ENABLE_ACTION = 'activate'
DISABLE_ACTION = 'dismiss'

ACTIVE_STATUS = 'active'
DISMISSED_STATUS = 'dismissed'
EXCLUDED_STATUS = 'excluded'


class OptimizationController(BaseController, MongoMixin, ResourceFormatMixin):

    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)

    def _get_model_type(self):
        return Organization

    def _get_optimizations_data(self, checklist, module=None):
        and_condition = [
            {'organization_id': {'$eq': checklist.organization_id}},
            {'created_at': {'$eq': checklist.last_completed}}
        ]
        if module:
            and_condition.append({'module': {'$eq': module}})
        pipeline = [
            {'$match': {'$and': and_condition}}
        ]
        return self.checklists_collection.aggregate(pipeline)

    @staticmethod
    def get_basic_response(checklist):
        return {
            'total_saving': 0,
            'optimizations': {},
            'dismissed_optimizations': {},
            'excluded_optimizations': {},
            **checklist.to_dict()
        }

    @staticmethod
    def limit_optimization_data(optimization_data, limit):
        return sorted(
            optimization_data,
            key=lambda x: (-x.get('saving', 0), -x.get('detected_at', 0)),
        )[:limit]

    @staticmethod
    def _get_cloud_account_data_filter(cloud_account_ids):
        ca_ids_map = {ca_id: True for ca_id in cloud_account_ids}
        return lambda x: ca_ids_map.get(x, len(ca_ids_map) == 0)

    @staticmethod
    def _get_item_status(optimization_item):
        if optimization_item.get('is_excluded', False):
            return EXCLUDED_STATUS
        elif optimization_item.get('is_dismissed', False):
            return DISMISSED_STATUS
        else:
            return ACTIVE_STATUS

    @staticmethod
    def _process_optimization_statuses(res, res_map, module):
        if res_map.get(DISMISSED_STATUS):
            res['dismissed_optimizations'][module] = res_map[DISMISSED_STATUS]
        if res_map.get(EXCLUDED_STATUS):
            res['excluded_optimizations'][module] = res_map[EXCLUDED_STATUS]
        if res_map.get(ACTIVE_STATUS):
            res['optimizations'][module] = res_map[ACTIVE_STATUS]
            res['total_saving'] += res_map[ACTIVE_STATUS].get('saving', 0)

    def fill_optimization_group(self, group, cloud_account_ids, detailed,
                                limit, status):
        def get_group_base(status_=None):
            res = {
                'count': 0,
                'saving': 0,
            }
            error = group.get('error') or group.get('timeout_error')
            if error:
                res['error'] = error
            if detailed and status_ == status:
                res['options'] = group.get('options') or {}
                res['items'] = []
            return res

        res_map = {
            ACTIVE_STATUS: {**get_group_base(ACTIVE_STATUS)},
            DISMISSED_STATUS: {},
            EXCLUDED_STATUS: {},
        }

        data_filter_func = self._get_cloud_account_data_filter(
            cloud_account_ids)
        data = group.get('data', []) or []
        for item in data:
            if not data_filter_func(item['cloud_account_id']):
                continue

            item_status = self._get_item_status(item)
            res_group = res_map.get(item_status)
            if not res_group:
                res_group.update(get_group_base(item_status))
            res_group['count'] += 1

            if item.get('saving') is None:
                res_group.pop('saving', None)
            else:
                res_group['saving'] += item.get('saving', 0)

            if detailed and status == item_status:
                cloud_account = self._get_cloud_account(item.get('cloud_account_id'))
                item['cloud_account_name'] = getattr(cloud_account, 'name', None)
                res_group['items'].append(item)

        if detailed and limit:
            for res_group in res_map.values():
                if res_group.get('items'):
                    res_group['items'] = self.limit_optimization_data(
                        res_group['items'], limit)
                    res_group['limit'] = limit
        return res_map

    def check_cloud_accounts(self, organization_id, cloud_account_ids):
        ca_db_ids = self.session.query(CloudAccount.id).filter(and_(
            CloudAccount.organization_id == organization_id,
            CloudAccount.id.in_(cloud_account_ids),
            CloudAccount.deleted.is_(False)
        )).all()
        ca_db_ids = {ca[0] for ca in ca_db_ids}
        if len(ca_db_ids) != len(cloud_account_ids):
            diff = list(set(cloud_account_ids) - ca_db_ids)
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, diff.pop()])

    def get_optimizations(self, organization, types, cloud_account_ids,
                          limit, status, overview=False):
        if cloud_account_ids:
            self.check_cloud_accounts(organization.id, cloud_account_ids)
        types = {t: True for t in types}
        checklist = ChecklistController(
            self.session, self._config).get_by_organization(organization.id)
        res = self.get_basic_response(checklist)
        optimization_groups = list(self._get_optimizations_data(checklist))
        for group in optimization_groups:
            module = group.get('module')
            res_map = self.fill_optimization_group(
                group, cloud_account_ids, types.get(module, False or overview), limit,
                status)
            self._process_optimization_statuses(res, res_map, module)
        return res

    def get_optimization_data(self, organization, opt_type,
                              cloud_account_ids, opt_status, limit=None):
        if cloud_account_ids:
            self.check_cloud_accounts(organization.id, cloud_account_ids)
        data_filter_func = self._get_cloud_account_data_filter(
            cloud_account_ids)
        checklist = ChecklistController(
            self.session, self._config).get_by_organization(organization.id)
        optimizations = list(self._get_optimizations_data(
            checklist, module=opt_type))
        if not optimizations:
            return []
        optimization = optimizations[0]
        result = [x for x in optimization.get('data', [])
                  if self._get_item_status(x) == opt_status and
                  data_filter_func(x['cloud_account_id'])]
        if limit:
            result = self.limit_optimization_data(result, limit)
        return result

    def get_resource(self, resource_id):
        resource = CloudResourceController(
            self.session, self._config).get(resource_id)
        if resource.get('cluster_type_id'):
            raise FailedDependency(Err.OE0465, [])
        return resource

    def get_resource_owner(self, resource_id):
        auth_user_id = CloudResourceController(
            self.session, self._config).get_owner(resource_id)
        return auth_user_id

    def _dismiss_module_optimization(self, resource_id, cloud_account_id,
                                     module, is_dismissed):
        org_id = self.session.query(Organization.id).join(
            CloudAccount, and_(
                CloudAccount.organization_id == Organization.id,
                CloudAccount.deleted.is_(False),
                CloudAccount.id == cloud_account_id)
        ).filter(Organization.deleted.is_(False)).scalar()
        checklist = ChecklistController(
            self.session, self._config).get_by_organization(org_id)
        self.checklists_collection.update_one(
            filter={'organization_id': checklist.organization_id,
                    'created_at': checklist.last_completed,
                    'module': module,
                    'data.resource_id': resource_id},
            update={
                '$set': {'data.$.is_dismissed': is_dismissed}
            }
        )

    @staticmethod
    def _fill_recommendation(data, run_timestamp):
        if not run_timestamp or not data:
            return {}
        return {
            'run_timestamp': run_timestamp,
            'modules': data
        }

    def process_resource_recommendation(self, resource, action, recommendation):
        dismissed_recommendations = resource.get(DISMISSED_STATUS, [])
        if action == DISABLE_ACTION:
            if recommendation in dismissed_recommendations:
                return resource
            dismissed_recommendations.append(recommendation)
        else:
            try:
                dismissed_recommendations.remove(recommendation)
            except ValueError:
                return resource

        action_direction_map = {
            ENABLE_ACTION: ('dismissed_recommendations', 'recommendations'),
            DISABLE_ACTION: ('recommendations', 'dismissed_recommendations')
        }
        from_key, to_key = action_direction_map.get(action)
        from_recommendations_data = resource.get(from_key, {}).get('modules', [])
        to_recommendations_data = resource.get(to_key, {}).get('modules', [])
        run_timestamp = 0
        for key in [from_key, to_key]:
            run_timestamp = resource.get(key, {}).get('run_timestamp')
            if run_timestamp:
                break
        for pos, r in enumerate(from_recommendations_data.copy()):
            if r.get('name') == recommendation:
                to_recommendations_data.append(r)
                from_recommendations_data.pop(pos)
                break

        self._dismiss_module_optimization(
            resource['id'], resource['cloud_account_id'],
            recommendation, action != ENABLE_ACTION)

        self.resources_collection.update_one(
            filter={
                '_id': resource['id'],
            },
            update={
                '$set': {
                    'dismissed': dismissed_recommendations,
                    from_key: self._fill_recommendation(
                        from_recommendations_data, run_timestamp),
                    to_key: self._fill_recommendation(
                        to_recommendations_data, run_timestamp)
                }
            })
        self._publish_recommendation_activity(recommendation, resource, action)
        return self.get_resource(resource['id'])

    def _publish_recommendation_activity(self, recommendation, resource,
                                         action):
        action_class_map = {
            DISABLE_ACTION: 'recommendations_dismissed',
            ENABLE_ACTION: 'recommendations_reactivated'
        }
        cloud_acc = self.session.query(CloudAccount).filter(and_(
            CloudAccount.id == resource['cloud_account_id'],
            CloudAccount.deleted.is_(False))).one_or_none()
        resource_name = resource.get('name', resource.get('cloud_resource_id'))
        action = action_class_map.get(action)
        meta = {
            'object_name': resource_name,
            'recommendation': recommendation
        }
        self.publish_activities_task(
            cloud_acc.organization_id, resource['id'], 'resource',
            action, meta, 'resource.{action}'.format(action=action),
            add_token=True)

    @lru_cache
    def _get_cloud_account(self, cloud_account_id):
        if cloud_account_id is None:
            return None
        cloud_account = self.session.query(CloudAccount).filter(
            CloudAccount.id == cloud_account_id,
            CloudAccount.deleted.is_(False)
        ).one_or_none()
        return cloud_account


class OptimizationAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return OptimizationController
