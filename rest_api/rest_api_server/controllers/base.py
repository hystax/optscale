import hashlib
import logging
import threading
from clickhouse_driver import Client as ClickHouseClient
from datetime import datetime
from kombu import Connection as QConnection, Exchange
from kombu.pools import producers
from pymongo import MongoClient
import requests
from retrying import retry
from sqlalchemy.exc import IntegrityError, ResourceClosedError
from sqlalchemy import and_, exists

from optscale_client.auth_client.client_v2 import Client as AuthClient
from tools.optscale_exceptions.common_exc import (
    WrongArgumentsException, FailedDependency, ConflictException,
    UnauthorizedException, NotFoundException)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import (
    PermissionKeys, Checklist, CloudAccount, Organization, ProfilingToken)
from rest_api.rest_api_server.utils import (
    Config, encoded_tags, encoded_map, RetriableException,
    should_retry, SupportedFiltersMixin, check_list_attribute,
    check_regex_attribute, check_bool_attribute, check_int_attribute, get_nil_uuid)

from optscale_client.arcee_client.client import Client as ArceeClient
from optscale_client.bulldozer_client.client import Client as BulldozerClient

ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
LOG = logging.getLogger(__name__)
PRIORITY_RETRIES = dict(
    stop_max_attempt_number=6, wait_fixed=500,
    retry_on_exception=should_retry)
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


class PriorityMixin(object):
    # the model should have organization_id and priority fields
    @retry(**PRIORITY_RETRIES)
    def change_priority(self, action, item, all_items, output_wrapper):
        max_priority = max(all_items, key=lambda it: it.priority).priority
        if action is None:
            raise WrongArgumentsException(Err.OE0216, ['action'])
        if action == 'prioritize':
            target_priority = 1
        elif action == 'promote':
            target_priority = item.priority - 1
            if target_priority < 1:
                return output_wrapper(all_items)
        elif action == 'demote':
            target_priority = item.priority + 1
            if target_priority > max_priority:
                return output_wrapper(all_items)
        elif action == 'deprioritize':
            target_priority = max_priority
        else:
            raise WrongArgumentsException(Err.OE0166, [action])
        try:
            result_items = self.set_priority(all_items, item, target_priority)
            self.session.commit()
        except IntegrityError as exc:
            LOG.warning('Unable to change %s priority: %s', (
                item.__class__.__name__, str(exc)))
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(exc)
        return output_wrapper(result_items)

    def set_priority(self, all_items, item, priority):
        """
        This method doesn't commit changes - it was done on purpose to make it
        possible to include other changes into one transaction.

        Updates done manually instead of changing ORM objects to make sure order
        of operations is kept untouched - due to mysql not supporting deferred
        constraints we have to do 3 operations to switch priority values between
        items instead of 2.
        """
        model = item.__class__
        max_priority = max(all_items, key=lambda it: it.priority).priority
        if priority < 1 or priority > max_priority:
            raise WrongArgumentsException(Err.OE0217, ['priority'])
        item_ids = [r.id for r in all_items]
        id_object_map = {r.id: r for r in all_items}
        target_item = id_object_map.get(item.id)
        if target_item is None:
            raise NotFoundException(Err.OE0002, [model.__name__, item.id])
        elif target_item.priority == priority:
            return all_items
        item_ids.insert(priority - 1, item_ids.pop(item_ids.index(item.id)))

        reverse_order = target_item.priority > priority
        self.session.query(model).filter(model.id == target_item.id).update({
            'priority': max_priority + 1})

        enumeration = enumerate(item_ids, start=1)
        if reverse_order:
            enumeration = reversed(list(enumeration))
        for i, r_id in enumeration:
            obj = id_object_map.get(r_id)
            self.session.query(model).filter(
                model.id == obj.id).update({'priority': i})
        return [id_object_map.get(r) for r in item_ids]


class ResourceFormatMixin(object):
    def get_org_id_by_cloud_acc_id(self, cloud_account_id):
        return self.session.query(
            CloudAccount.organization_id
        ).filter(and_(
            CloudAccount.id == cloud_account_id,
            CloudAccount.deleted.is_(False)
        )).scalar()

    def get_last_run_ts_by_org_id(self, org_id):
        last_completed = self.session.query(
            Checklist.last_completed
        ).filter(and_(
            Checklist.deleted.is_(False),
            Checklist.organization_id == org_id,
        )).scalar()
        return last_completed if last_completed else 0

    def get_last_run_ts_by_cloud_account_id(self, cloud_account_id):
        org_id = self.get_org_id_by_cloud_acc_id(cloud_account_id)
        if org_id:
            return self.get_last_run_ts_by_org_id(org_id)
        else:
            return 0

    def get_sub_resources(self, cluster_id, last_run_ts=None):
        sub_resources = self.resources_collection.find({
            'cluster_id': cluster_id,
            'deleted_at': 0
        })
        return [self.format_resource(r, last_run_ts) for r in sub_resources]

    def format_resource(self, resource, last_run_ts=None,
                        ignore_dependencies=False, is_report_import=False):
        optional_params = ['name', 'region', 'employee_id', 'pool_id',
                           'meta', 'tags', 'last_seen',
                           'sub_resources', 'is_environment']
        default_values = {
            'last_seen': 0, 'meta': {}, 'tags': {}, 'sub_resources': [],
            'is_environment': False
        }
        if resource.get('_id'):
            resource['id'] = resource.pop('_id')
        for nullable_field in optional_params:
            if nullable_field not in resource:
                resource[nullable_field] = default_values.get(
                    nullable_field)
        active = resource.get('active', False)
        if not active:
            resource['meta']['cloud_console_link'] = None
        resource['tags'] = encoded_tags(resource.get('tags'), True)
        resource['env_properties'] = encoded_map(resource.get('env_properties'), True)

        if last_run_ts is None and not is_report_import:
            if resource.get('cloud_account_id'):
                last_run_ts = self.get_last_run_ts_by_cloud_account_id(
                    resource['cloud_account_id'])
            else:
                last_run_ts = self.get_last_run_ts_by_org_id(
                    resource['organization_id'])
        if not ignore_dependencies and resource.get('cluster_type_id'):
            resource['sub_resources'].extend(
                self.get_sub_resources(resource.get('id'), last_run_ts))
            resource['recommendations'] = {}
            for sub_resource in resource['sub_resources']:
                recommendations = sub_resource.get('recommendations')
                if recommendations and last_run_ts <= recommendations.get(
                        'run_timestamp', 0):
                    if not resource.get('recommendations'):
                        resource['recommendations'] = recommendations
                    else:
                        resource['recommendations']['modules'].extend(
                            recommendations['modules'])
        else:
            recommendations = resource.get('recommendations')
            if (recommendations is None or last_run_ts is None or
                    last_run_ts > recommendations.get('run_timestamp', 0)):
                resource['recommendations'] = {}
        dismissed_recommendations = resource.get('dismissed_recommendations')
        if (dismissed_recommendations is None or last_run_ts is None or
                last_run_ts > dismissed_recommendations.get('run_timestamp', 0)):
            resource['dismissed_recommendations'] = {}
        if resource.get('dismissed') is None:
            resource['dismissed'] = []
        return resource


class MongoMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mongo_client = None

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = Config().mongo_params
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def resources_collection(self):
        return self.mongo_client.restapi.resources

    @property
    def checklists_collection(self):
        return self.mongo_client.restapi.checklists

    @property
    def raw_expenses_collection(self):
        return self.mongo_client.restapi.raw_expenses

    @property
    def property_history_collection(self):
        return self.mongo_client.restapi.property_history

    @property
    def archived_recommendations_collection(self):
        return self.mongo_client.restapi.archived_recommendations


class ClickHouseMixin(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clickhouse_client = None

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, db_name = Config().clickhouse_params
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_client

    def execute_clickhouse(self, query, **params):
        return self.clickhouse_client.execute(query=query, **params)


class FilterValidationMixin(SupportedFiltersMixin):
    NIL_UUID = get_nil_uuid()

    def _check_int_attribute(self, filter_name, filter_val):
        check_int_attribute(filter_name, filter_val, min_length=1)

    def _check_bool_attribute(self, filter_name, filter_val):
        if filter_val != self.NIL_UUID:
            check_bool_attribute(filter_name, filter_val)

    def check_filters(self, filters):
        allowed_filters = (self.list_filters + self.bool_filters +
                           self.int_filters + self.str_filters)
        unexpected_filters = list(filter(
            lambda x: x not in allowed_filters, filters))
        if unexpected_filters:
            message = ', '.join(unexpected_filters)
            raise WrongArgumentsException(Err.OE0212, [message])

        filter_group_checks = [
            (self.list_filters, check_list_attribute),
            (self.str_filters, check_regex_attribute),
            (self.bool_filters, self._check_bool_attribute),
            (self.int_filters, self._check_int_attribute)
        ]
        for filters_group, check_func in filter_group_checks:
            for filter_name in filters_group:
                if filter_name in filters:
                    check_func(filter_name, filters[filter_name])


class OrganizationValidatorMixin:
    def check_organization(self, organization_id) -> None:
        does_exist = self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()
        if not does_exist:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])

    def get_organization(self, organization_id) -> Organization:
        organization = self.session.query(Organization).filter(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ).one_or_none()
        return organization


class BaseController(object):

    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__()
        self._session = db_session
        self._config = config
        self._db = None
        self._model_type = None
        self._engine = engine
        self._auth_client = None
        self.token = token

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        self._session = val

    @property
    def model_type(self):
        if self._model_type is None:
            self._model_type = self._get_model_type()
        return self._model_type

    @property
    def model_column_list(self):
        return list(map(lambda x: str(x.name),
                        self.model_type.__table__.columns))

    def _get_model_type(self):
        raise NotImplementedError

    def _get_create_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_creatable)

    def _get_update_restrictions(self):
        return self._get_restrictions(PermissionKeys.is_updatable)

    def _get_restrictions(self, filter_by):
        res = list(
            map(lambda x: x.name, list(
                filter(lambda x: x.info.get(filter_by) is True,
                       self._get_model_type().__table__.c))))
        return res

    def _validate(self, item, is_new=True, **kwargs):
        pass

    def publish_activities_task(self, organization_id, object_id, object_type,
                                action, meta, routing_key, add_token=False):
        if add_token and self.token:
            if not meta:
                meta = {}
            meta.update({'token': self.token})
        task = {
            'organization_id': organization_id,
            'object_id': object_id,
            'object_type': object_type,
            'action': action,
            'meta': meta
        }
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')))
        task_exchange = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                task,
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=routing_key,
                retry=True
            )

    @property
    def auth_client(self):
        if not self._auth_client:
            self._auth_client = AuthClient(
                url=Config().auth_url, secret=Config().cluster_secret)
        return self._auth_client

    def get_user_id(self):
        user_digest = hashlib.md5(self.token.encode('utf-8')).hexdigest()
        _, token_meta = self.auth_client.token_meta_get([user_digest])
        return token_meta.get(user_digest, {}).get('user_id')

    @staticmethod
    def _popkey(obj, key):
        if key in obj:
            obj.pop(key)
        for k, v in obj.items():
            if isinstance(v, dict):
                return BaseController._popkey(v, key)

    def create(self, **kwargs):
        self.check_create_restrictions(**kwargs)
        model_type = self._get_model_type()
        try:
            item = model_type(**kwargs)
            self._validate(item, True, **kwargs)
            self._popkey(kwargs, 'password')
            LOG.info("Creating %s with parameters %s", model_type.__name__,
                     kwargs)
            self.session.add(item)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        except TypeError as ex:
            raise WrongArgumentsException(Err.OE0004, [str(ex)])
        return item

    def get(self, item_id, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.id == item_id,
            self.model_type.deleted.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        res = query.all()
        if len(res) > 1:
            raise WrongArgumentsException(Err.OE0177, [])
        if len(res) == 1:
            return res[0]

    def edit(self, item_id, **kwargs):
        self.check_update_restrictions(**kwargs)
        return self.update(item_id, **kwargs)

    def hard_delete(self, item_id):
        LOG.info("Hard-deleting %s with id %s",
                 self.model_type.__name__, item_id)
        try:
            item = self.get(item_id)
            self.session.delete(item)
            self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return item

    def delete(self, item_id):
        LOG.info("Deleting %s with id %s", self.model_type.__name__, item_id)
        return self.update(
            item_id, deleted_at=int(datetime.utcnow().timestamp()))

    def update(self, item_id, **kwargs):
        try:
            item = self.get(item_id)
            if kwargs:
                self.session.expunge(item)
                for key, value in kwargs.items():
                    setattr(item, key, value)
                self._validate(item, is_new=False, **kwargs)
                self.session.add(item)
                self.session.commit()
        except IntegrityError as ex:
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return item

    def list(self, **kwargs):
        query = self.session.query(self.model_type).filter(
            self.model_type.deleted_at.is_(False))
        if len(kwargs) > 0:
            query = query.filter_by(**kwargs)
        return query.all()

    def _get_entities(self, model_type, entity_ids):
        return self.session.query(model_type).filter(
            model_type.id.in_(list(entity_ids)),
            model_type.deleted.is_(False)
        ).all()

    def check_update_restrictions(self, **kwargs):
        self._check_restrictions(self._get_update_restrictions(), **kwargs)

    def check_create_restrictions(self, **kwargs):
        self._check_restrictions(self._get_create_restrictions(), **kwargs)

    def check_update_immutables(self, **kwargs):
        self._check_immutables(self._get_update_restrictions(), **kwargs)

    def check_create_immutables(self, **kwargs):
        self._check_immutables(self._get_create_restrictions(), **kwargs)

    def _check_immutables(self, restrictions, **kwargs):
        immutables = list(filter(
            lambda x: x not in restrictions, self.model_column_list))
        immutables_matches = list(filter(lambda x: x in kwargs, immutables))
        if immutables_matches:
            message = ', '.join(immutables_matches)
            LOG.warning('immutable parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OE0211, [immutables_matches[0]])

    def _check_restrictions(self, restrictions, **kwargs):
        self._check_immutables(restrictions, **kwargs)
        unexpected_params = list(filter(
            lambda x:
            x not in self.model_column_list and x not in restrictions,
            kwargs.keys()))
        if unexpected_params:
            message = ', '.join(unexpected_params)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OE0212, [unexpected_params])

    @staticmethod
    def run_async(func, params):
        thr = threading.Thread(target=func, args=params)
        thr.start()

    def _get_type_id(self, assignment_type):
        # TODO remove it, this workaround is needed only until we have
        #  pool and organization type in auth
        levels = {
            "root": 1,
            "organization": 2,
            "pool": 3
        }
        level = levels.get(assignment_type)
        _, types = self.auth_client.type_list()
        parent_id = None
        type_id = None
        type_map = {type_['parent_id']: type_['id'] for type_ in types}
        for i in range(level):
            type_id = type_map.get(parent_id)
            parent_id = type_id
        return type_id

    def assign_role_to_user(self, user_id, scope_id, purpose,
                            assignment_type="organization"):
        try:
            _, role = self.auth_client.get_purposed_role(purpose)
            type_id = self._get_type_id(assignment_type)
            self.auth_client.assignment_register(user_id, role['id'], type_id,
                                                 scope_id)
        except requests.exceptions.HTTPError as ex:
            LOG.error('Assign error: %s' % str(ex))
            raise FailedDependency(Err.OE0435, [str(ex)])

    def get_user_info(self):
        try:
            user_id = self.get_user_id()
            if user_id is None:
                return {}
            self.auth_client.token = self.token
            _, user = self.auth_client.user_get(user_id)
        except requests.exceptions.HTTPError as ex:
            raise WrongArgumentsException(Err.OE0435, [str(ex)])
        return user

    def create_auth_user(self, email, password, name):
        try:
            _, user = self.auth_client.user_create(email, password, name)
        except requests.exceptions.HTTPError as ex:
            err_code = ex.response.json()['error']['error_code']
            if err_code == 'OA0042':
                raise WrongArgumentsException(Err.OE0494, [email])
            if ex.response.status_code in [409, 400]:
                error_class = WrongArgumentsException if (
                    ex.response.status_code == 400) else ConflictException
                raise error_class(Err.OE0435, [str(ex)])
            raise
        return user

    @staticmethod
    def _get_assignments_actions_by_token(token, actions, user_id=None):
        auth_client = AuthClient(url=Config().auth_url, token=token,
                                 secret=Config().cluster_secret)
        try:
            _, result = auth_client.action_resources_get(
                actions, user_id=user_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response.status_code == 401:
                raise UnauthorizedException(Err.OE0235, [])
            raise
        return result

    def get_bulk_allowed_action_pools_map(self, user_ids, actions):
        _, response = self.auth_client.bulk_action_resources_get(
            user_ids, actions)
        result = {}
        for user_id, action_resources in response.items():
            action_pool_map = {}
            for action, resources in action_resources.items():
                action_pool_map[action] = []
                for type, resource_id in resources:
                    if type == 'pool':
                        action_pool_map[action].append(resource_id)
            result[user_id] = action_pool_map
        return result

    def get_actions_assignment_map(self, org, token, actions, user_id=None):
        result = {action: [] for action in actions}
        resp = self._get_assignments_actions_by_token(token, actions,
                                                      user_id=user_id)
        for action in actions:
            assignments = resp[action]
            for assignment in assignments:
                if assignment[0] == 'pool':
                    result[action].append(assignment[1])
                if assignment[0] == 'organization' and assignment[1] == org.id:
                    result[action].append(org.pool_id)
        return result

    def _is_cloud_account_exists(self, cloud_account_id):
        return self.session.query(
            exists().where(and_(
                CloudAccount.id == cloud_account_id,
                CloudAccount.deleted.is_(False)
            ))
        ).scalar()

    def _check_cloud_account_exists(self, cloud_account_id):
        if not self._is_cloud_account_exists(cloud_account_id):
            raise NotFoundException(
                    Err.OE0002, [CloudAccount.__name__, cloud_account_id])


class BaseHierarchicalController(BaseController):
    def get_item_hierarchy(self, bind_model_key, bind_model_value,
                           bind_hierarchy_key, model_type, include_item=False):
        identification_field = 'id' if include_item else bind_hierarchy_key
        hierarchy = self.session.query(model_type).filter(
            getattr(model_type, identification_field) == bind_model_value,
            getattr(model_type, 'deleted_at') == 0,
        ).cte(name="hierarchy", recursive=True)
        hierarchy = hierarchy.union_all(
            self.session.query(model_type).filter(
                getattr(model_type, bind_hierarchy_key
                        ) == getattr(hierarchy.c, bind_model_key),
                getattr(model_type, 'deleted_at') == 0,
            ))
        try:
            result = self.session.query(
                model_type).select_entity_from(hierarchy).all()
        except ResourceClosedError:
            result = []
        return result


class BaseProfilingTokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._arcee_client = None
        self._bulldozer_client = None

    @staticmethod
    def get_secret():
        return Config().cluster_secret

    @property
    def arcee_client(self):
        if not self._arcee_client:
            self._arcee_client = ArceeClient(
                url=Config().arcee_url)
            self._arcee_client.secret = self.get_secret()
        return self._arcee_client

    def get_arcee_client(self, token=None):
        self.arcee_client.token = token
        return self.arcee_client

    @property
    def bulldozer_client(self):
        if not self._bulldozer_client:
            self._bulldozer_client = BulldozerClient(
                url=Config().bulldozer_url)
            self._bulldozer_client.secret = self.get_secret()
        return self._bulldozer_client

    def get_bulldozer_client(self, token=None):
        self.bulldozer_client.token = token
        return self.bulldozer_client

    def _get(self, organization_id):
        return self.session.query(ProfilingToken).filter(
            ProfilingToken.deleted.is_(False),
            ProfilingToken.organization_id == organization_id
        ).one_or_none()

    def get_or_create_profiling_token(self, organization_id):
        item = self._get(organization_id)
        if not item:
            try:
                item = ProfilingToken(organization_id=organization_id)
                self.session.add(item)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                item = self._get(organization_id)
            try:
                self._create_arcee_token(item.token)
            except Exception:
                self.session.delete(item)
                self.session.commit()
                raise
            try:
                self._create_bulldozer_token(item.infrastructure_token)
            except Exception:
                self._delete_arcee_token(item.token)
                self.session.delete(item)
                self.session.commit()
                raise
        return item

    def _create_bulldozer_token(self, infrastructure_token):
        bulldozer = self.get_bulldozer_client()
        bulldozer.token_create(infrastructure_token)

    def _delete_bulldozer_token(self, infrastructure_token):
        bulldozer = self.get_arcee_client(infrastructure_token)
        bulldozer.token_delete(infrastructure_token)

    def _create_arcee_token(self, profiling_token):
        arcee = self.get_arcee_client()
        arcee.token_create(profiling_token)

    def _delete_arcee_token(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        arcee.token_delete(profiling_token)
