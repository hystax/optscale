import copy
import enum
import json
import logging
import os
import uuid
from collections import defaultdict
from json.decoder import JSONDecodeError
from kombu.pools import producers
from kombu import Connection as QConnection, Exchange
from bson.objectid import ObjectId
from pymongo import UpdateOne

from optscale_client.config_client.client import etcd
from datetime import datetime, timedelta
from sqlalchemy import and_, true

from tools.cloud_adapter.model import ResourceTypes
from tools.optscale_exceptions.common_exc import InternalServerError
from rest_api.rest_api_server.controllers.base import (
    BaseController, MongoMixin, BaseProfilingTokenController, ClickHouseMixin)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.register import RegisterController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import (
    InviteAssignmentScopeTypes, CloudTypes, OrganizationConstraintTypes)
from rest_api.rest_api_server.models.models import (
    CloudAccount, Checklist, Employee, Pool, Organization, PoolPolicy,
    ResourceConstraint, ConstraintLimitHit, Rule, Condition, DiscoveryInfo,
    ClusterType, K8sNode, CostModel, ShareableBooking, OrganizationOption,
    OrganizationConstraint, OrganizationLimitHit, OrganizationGemini,
    ProfilingToken, PowerSchedule)
from rest_api.rest_api_server.utils import (
    gen_id, encode_config, timestamp_to_day_start)
from optscale_client.herald_client.client_v2 import Client as HeraldClient


LOG = logging.getLogger(__name__)

BULK_SIZE = 3000
CLICKHOUSE_BULK_SIZE = 20000
DEMO_ORG_TEMPLATE = 'Sunflower Inc'
DEMO_USER_NAME = 'Demo User'
EMAIL_TEMPLATE = '%s@sunflower.demo'
PRESET_FILENAME = 'rest_api/live_demo.json'
DUPLICATION_MODULE_NAMES = {'abandoned_instances', 'rightsizing_instances'}
DUPLICATION_COUNT = 3
TOP_NO_DUPLICATE_RESOURCES = 10
DUPLICATION_FORMAT = '-x{ending}'
WITH_SUBPOOLS_SIGN = '+'
RECOMMENDATION_MULTIPLIED_FIELDS = ['saving', 'annually_monthly_saving',
                                    'monthly_saving']
PREPARED_DEMO_LIFETIME_DAYS = 3
CLICKHOUSE_TABLE_DB_MAP = {
    'average_metrics': 'default',
    'k8s_metrics': 'default',
    'expenses': 'default',
    'traffic_expenses': 'default',
    'ri_sp_usage': 'risp',
    'uncovered_usage': 'risp'
}
ROUTING_KEY = 'live-demo-generation'
EXCHANGE_NAME = 'live-demo-generations'
RETRY_POLICY = {'max_retries': 15, 'interval_start': 0,
                'interval_step': 1, 'interval_max': 3}


class ObjectGroups(enum.Enum):
    CostModels = 'cost_models'
    CloudAccounts = 'cloud_accounts'
    DiscoveryInfo = 'discovery_info'
    Checklists = 'checklists'
    Employees = 'employees'
    Pools = 'pools'
    ClusterTypes = 'cluster_types'
    PowerSchedules = 'power_schedules'
    Resources = 'resources'
    RawExpenses = 'raw_expenses'
    CleanExpenses = 'clean_expenses'
    TrafficExpenses = 'traffic_expenses'
    Optimizations = 'optimizations'
    ArchivedRecommendations = 'archived_recommendations'
    PoolPolicies = 'pool_policies'
    ResourceConstraints = 'resource_constraints'
    LimitHits = 'limit_hits'
    Rules = 'rules'
    Conditions = 'conditions'
    AuthUsers = 'auth_users'
    PoolRelations = 'pool_relations'
    Nodes = 'nodes'
    AverageMetrics = 'average_metrics'
    K8sMetrics = 'k8s_metrics'
    ShareableBookings = 'shareable_bookings'
    OrganizationOptions = 'organization_options'
    OrganizationConstraint = 'organization_constraint'
    OrganizationLimitHit = 'organization_limit_hit'
    RiSpUsages = 'ri_sp_usage'
    UncoveredUsages = 'uncovered_usage'
    Metrics = 'metrics'
    Tasks = 'tasks'
    Templates = 'templates'
    Runsets = 'runsets'
    Datasets = 'datasets'
    Runs = 'runs'
    Runners = 'runners'
    Platforms = 'platforms'
    Logs = 'logs'
    Milestones = 'milestones'
    Stages = 'stages'
    ProcData = 'proc_data'
    Consoles = 'consoles'
    LeaderboardTemplates = 'leaderboard_templates'
    Leaderboards = 'leaderboards'
    OrganizationGeminis = 'organization_geminis'
    Models = 'models'
    ModelVersions = 'model_versions'
    Artifacts = 'artifacts'

    @classmethod
    def rest_objects(cls):
        # pylint: disable=no-member
        return (cls._member_map_[name] for name in cls._member_names_
                if name not in {'AuthUsers', 'PoolRelations'})


class LiveDemoController(BaseController, MongoMixin, ClickHouseMixin):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._recovery_map = {}
        self._build_obj_map = {
            ObjectGroups.CloudAccounts: self.build_cloud_account,
            ObjectGroups.Checklists: self.build_checklist,
            ObjectGroups.Employees: self.build_employee,
            ObjectGroups.Pools: self.build_pool,
            ObjectGroups.ClusterTypes: self.build_cluster_type,
            ObjectGroups.Resources: self.build_resource,
            ObjectGroups.RawExpenses: self.build_raw_expense,
            ObjectGroups.CleanExpenses: self.build_clean_expense,
            ObjectGroups.TrafficExpenses: self.build_traffic_expenses,
            ObjectGroups.Optimizations: self.build_optimization,
            ObjectGroups.PoolPolicies: self.build_pool_policy,
            ObjectGroups.ResourceConstraints: self.build_resource_constraint,
            ObjectGroups.LimitHits: self.build_limit_hit,
            ObjectGroups.Rules: self.build_rule,
            ObjectGroups.Conditions: self.build_condition,
            ObjectGroups.DiscoveryInfo: self.build_discovery_info,
            ObjectGroups.Nodes: self.build_node,
            ObjectGroups.CostModels: self.build_cost_model,
            ObjectGroups.AverageMetrics: self.build_average_metric,
            ObjectGroups.K8sMetrics: self.build_k8s_metric,
            ObjectGroups.ShareableBookings: self.build_shareable_booking,
            ObjectGroups.OrganizationOptions: self.build_organization_option,
            ObjectGroups.OrganizationConstraint:
                self.build_organization_constraint,
            ObjectGroups.OrganizationLimitHit:
                self.build_organization_limit_hit,
            ObjectGroups.ArchivedRecommendations:
                self.build_archived_recommendations,
            ObjectGroups.RiSpUsages: self.build_ri_sp_usage,
            ObjectGroups.UncoveredUsages: self.build_uncovered_usage,
            ObjectGroups.Metrics: self.build_metric,
            ObjectGroups.Tasks: self.build_task,
            ObjectGroups.Runs: self.build_run,
            ObjectGroups.Platforms: self.build_platform,
            ObjectGroups.Logs: self.build_log,
            ObjectGroups.Milestones: self.build_milestone,
            ObjectGroups.Stages: self.build_stage,
            ObjectGroups.ProcData: self.build_proc_data,
            ObjectGroups.Models: self.build_model,
            ObjectGroups.ModelVersions: self.build_model_version,
            ObjectGroups.Artifacts: self.build_artifact,
            ObjectGroups.Templates: self.build_template,
            ObjectGroups.Runsets: self.build_runset,
            ObjectGroups.Runners: self.build_runner,
            ObjectGroups.Datasets: self.build_dataset,
            ObjectGroups.Consoles: self.build_console,
            ObjectGroups.LeaderboardTemplates: self.build_leaderboard_template,
            ObjectGroups.Leaderboards: self.build_leaderboard,
            ObjectGroups.OrganizationGeminis: self.build_organization_gemini,
            ObjectGroups.PowerSchedules: self.build_power_schedule
        }
        self._dest_map = {
            ObjectGroups.Resources: self.resources_collection,
            ObjectGroups.RawExpenses: self.raw_expenses_collection,
            ObjectGroups.Optimizations: self.checklists_collection,
            ObjectGroups.ArchivedRecommendations:
                self.archived_recommendations_collection,
            ObjectGroups.Tasks: self.tasks_collection,
            ObjectGroups.Runs: self.runs_collection,
            ObjectGroups.Metrics: self.metrics_collection,
            ObjectGroups.Platforms: self.platforms_collection,
            ObjectGroups.Logs: self.logs_collection,
            ObjectGroups.Milestones: self.milestones_collection,
            ObjectGroups.Stages: self.stages_collection,
            ObjectGroups.ProcData: self.proc_data_collection,
            ObjectGroups.Models: self.model_collection,
            ObjectGroups.ModelVersions: self.model_version_collection,
            ObjectGroups.Templates: self.templates_collection,
            ObjectGroups.Runsets: self.runsets_collection,
            ObjectGroups.Runners: self.runners_collection,
            ObjectGroups.Datasets: self.datasets_collection,
            ObjectGroups.Consoles: self.consoles_collection,
            ObjectGroups.LeaderboardTemplates:
                self.leaderboard_templates_collection,
            ObjectGroups.Leaderboards:
                self.leaderboards_collection,
            ObjectGroups.Artifacts: self.artifact_collection,
        }
        self._clickhouse_table_map = {
            ObjectGroups.AverageMetrics: 'average_metrics',
            ObjectGroups.K8sMetrics: 'k8s_metrics',
            ObjectGroups.CleanExpenses: 'expenses',
            ObjectGroups.TrafficExpenses: 'traffic_expenses',
            ObjectGroups.RiSpUsages: 'ri_sp_usage',
            ObjectGroups.UncoveredUsages: 'uncovered_usage'
        }
        self._key_object_group_map = {
            'pool_id': ObjectGroups.Pools.value,
            'employee_id': ObjectGroups.Employees.value,
            'cloud_account_id': ObjectGroups.CloudAccounts.value,
            'cloud_account_ids': ObjectGroups.CloudAccounts.value,
            'owner_id': ObjectGroups.Employees.value,
            'resource_id': ObjectGroups.Resources.value,
            'creator_id': ObjectGroups.Employees.value,
            'rule_id': ObjectGroups.Rules.value,
            'default_owner_id': ObjectGroups.Employees.value,
            'cluster_type_id': ObjectGroups.ClusterTypes.value,
            'cost_model_id': ObjectGroups.CostModels.value,
            'acquired_by_id': ObjectGroups.Employees.value,
            'constraint_id': ObjectGroups.OrganizationConstraint.value,
            'offer_id': ObjectGroups.Resources.value,
            'metrics': ObjectGroups.Metrics.value,
            'task_id': ObjectGroups.Tasks.value,
            'task_ids': ObjectGroups.Tasks.value,
            'run_id': ObjectGroups.Runs.value,
            'model_id': ObjectGroups.Models.value,
            'template_id': ObjectGroups.Templates.value,
            'runset_id': ObjectGroups.Runsets.value,
            'leaderboard_template_id': ObjectGroups.LeaderboardTemplates.value,
            'dataset_id': ObjectGroups.Datasets.value,
            'dataset_ids': ObjectGroups.Datasets.value,
            'primary_metric': ObjectGroups.Metrics.value,
            'other_metrics': ObjectGroups.Metrics.value,
            'filters': ObjectGroups.Metrics.value,
            'power_schedule': ObjectGroups.PowerSchedules.value
        }
        self._multiplier = None
        self._duplication_module_res_info_map = defaultdict(dict)
        self._origin_res_duplication_info = defaultdict(dict)
        self._object_group_duplicated_func_map = {
            ObjectGroups.Resources: self.duplicate_resource,
            ObjectGroups.RawExpenses: self.duplicate_raw_expense,
            ObjectGroups.CleanExpenses: self.duplicate_res_id_depended,
            ObjectGroups.Optimizations: self.duplicate_optimization,
            ObjectGroups.ResourceConstraints: self.duplicate_res_id_depended,
            ObjectGroups.LimitHits: self.duplicate_res_id_depended,
            ObjectGroups.CostModels: self.duplicate_res_id_depended,
            ObjectGroups.ShareableBookings: self.duplicate_res_id_depended,
            ObjectGroups.AverageMetrics: self.duplicate_res_id_depended
        }
        self._org_constraint_type_map = {}

    @property
    def tasks_collection(self):
        return self.mongo_client.arcee.task

    @property
    def runs_collection(self):
        return self.mongo_client.arcee.run

    @property
    def metrics_collection(self):
        return self.mongo_client.arcee.metric

    @property
    def platforms_collection(self):
        return self.mongo_client.arcee.platform

    @property
    def logs_collection(self):
        return self.mongo_client.arcee.log

    @property
    def milestones_collection(self):
        return self.mongo_client.arcee.milestone

    @property
    def stages_collection(self):
        return self.mongo_client.arcee.stage

    @property
    def proc_data_collection(self):
        return self.mongo_client.arcee.proc_data

    @property
    def model_collection(self):
        return self.mongo_client.arcee.model

    @property
    def model_version_collection(self):
        return self.mongo_client.arcee.model_version

    @property
    def artifact_collection(self):
        return self.mongo_client.arcee.artifact

    @property
    def templates_collection(self):
        return self.mongo_client.bulldozer.template

    @property
    def runsets_collection(self):
        return self.mongo_client.bulldozer.runset

    @property
    def runners_collection(self):
        return self.mongo_client.bulldozer.runner

    @property
    def datasets_collection(self):
        return self.mongo_client.arcee.dataset

    @property
    def consoles_collection(self):
        return self.mongo_client.arcee.console

    @property
    def leaderboard_templates_collection(self):
        return self.mongo_client.arcee.leaderboard_template

    @property
    def leaderboards_collection(self):
        return self.mongo_client.arcee.leaderboard

    def _get_demo_multiplier(self):
        try:
            multiplier = int(
                self._config.read('/restapi/demo/multiplier').value)
        except etcd.EtcdKeyNotFound:
            LOG.info('Demo multiplier is not set in etcd.')
            multiplier = 1
        return multiplier

    @property
    def multiplier(self):
        if not self._multiplier:
            self._multiplier = self._get_demo_multiplier()
        return self._multiplier

    @property
    def permitted_constraints_multiplier(self):
        return {'total_expense_limit', 'daily_expense_limit'}

    @property
    def permitted_org_constraints_multiplier(self):
        return {OrganizationConstraintTypes.EXPENSE_ANOMALY.value,
                OrganizationConstraintTypes.EXPIRING_BUDGET.value,
                OrganizationConstraintTypes.RECURRING_BUDGET.value}

    @staticmethod
    def _get_basic_params():
        org = DEMO_ORG_TEMPLATE
        name = DEMO_USER_NAME
        passwd = str(uuid.uuid4().hex)
        email = EMAIL_TEMPLATE % passwd
        return org, name, email, passwd

    @staticmethod
    def load_preset(path=None):
        if not os.path.exists(path):
            raise InternalServerError(Err.OE0452, [])
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except JSONDecodeError:
            raise InternalServerError(Err.OE0450, [])

    def duplicate_resource(self, preset_object, duplication_resource_info_map):
        result = []
        res_id = preset_object.get('_id')
        if res_id in duplication_resource_info_map:
            for i in range(1, DUPLICATION_COUNT + 1):
                new_resource = copy.deepcopy(preset_object)
                new_id = gen_id()
                new_resource['_id'] = new_id
                res_ending = DUPLICATION_FORMAT.format(ending=i)
                cloud_res_id = preset_object.get('cloud_resource_id')
                res_name = preset_object.get('name')
                recommendations = new_resource.get('recommendations')
                if recommendations:
                    modules = recommendations.get('modules', [])
                    if modules:
                        new_modules = []
                        for module in modules:
                            module_name = module.get('name')
                            if module_name in DUPLICATION_MODULE_NAMES:
                                new_modules.append(module)
                        new_resource['recommendations']['modules'] = new_modules
                new_cloud_res_id = cloud_res_id + res_ending
                new_res_name = res_name + res_ending if res_name else res_name
                new_resource['cloud_resource_id'] = new_cloud_res_id
                new_resource['name'] = new_res_name
                result.append(new_resource)
                self._origin_res_duplication_info[res_id][new_id] = {
                    'cloud_resource_id': new_cloud_res_id,
                    'name': new_res_name
                }
        return result

    def duplicate_raw_expense(self, preset_object,
                              duplication_resource_info_map):
        result = []
        cloud_res_id = preset_object.get('resource_id')
        if cloud_res_id in duplication_resource_info_map.values():
            for i in range(1, DUPLICATION_COUNT + 1):
                new_resource = copy.deepcopy(preset_object)
                new_id = ObjectId()
                new_resource['_id'] = new_id
                res_ending = DUPLICATION_FORMAT.format(ending=i)
                new_cloud_res_id = cloud_res_id + res_ending
                new_resource['resource_id'] = new_cloud_res_id
                result.append(new_resource)
        return result

    def duplicate_res_id_depended(self, preset_object,
                                  duplication_resource_info_map):
        result = []
        res_id = preset_object.get('resource_id')
        if res_id in duplication_resource_info_map:
            duplicate_res_ids = list(self._origin_res_duplication_info.get(
                res_id).keys())
            for duplicate_res_id in duplicate_res_ids:
                new_resource = copy.deepcopy(preset_object)
                new_resource['resource_id'] = duplicate_res_id
                result.append(new_resource)
        return result

    def duplicate_optimization(self, preset_object,
                               duplication_resource_info_map):
        duplicate_module_names = set(
            self._duplication_module_res_info_map.keys())
        module_name = preset_object.get('module')
        if module_name in duplicate_module_names:
            module_data_list = copy.deepcopy(preset_object.get('data', []))
            if not module_data_list or not isinstance(module_data_list, list):
                return []
            for module_data in preset_object.get('data', []):
                res_id = module_data.get('resource_id')
                duplicate_res_info_map = (
                    self._origin_res_duplication_info.get(res_id))
                if duplicate_res_info_map:
                    for new_res_id, new_res_info in duplicate_res_info_map.items():
                        new_data = copy.deepcopy(module_data)
                        new_data['resource_id'] = new_res_id
                        new_data['cloud_resource_id'] = new_res_info.get(
                            'cloud_resource_id')
                        new_data['resource_name'] = new_res_info.get('name')
                        module_data_list.append(new_data)
            preset_object['data'] = module_data_list

    def add_duplicated_objects(self, objects_group, preset_object,
                               duplication_resource_info_map):
        duplicate_func = self._object_group_duplicated_func_map.get(
            objects_group)
        if duplicate_func:
            return duplicate_func(preset_object, duplication_resource_info_map)

    def recover_objects(self, objects_group, preset, **kwargs):
        res = []
        if objects_group.value not in self._recovery_map:
            self._recovery_map[objects_group.value] = {}
        duplication_resource_info_map = kwargs.pop(
            'duplication_resource_info_map', None)
        preset_objects = preset.pop(objects_group.value, [])
        for preset_object in preset_objects:
            objs = []
            if objects_group in self._object_group_duplicated_func_map:
                objs = self.add_duplicated_objects(
                    objects_group, preset_object, duplication_resource_info_map)
            items = [preset_object]
            if objs:
                items = items + objs
            for item in items:
                obj = self._build_obj_map.get(objects_group)(
                    obj=item, objects_group=objects_group, **kwargs)
                if obj:
                    res.append(obj)
        return res

    @staticmethod
    def offsets_to_timestamps(keys, now, obj):
        for key in keys:
            val = obj.pop('%s_offset' % key, None)
            if val is not None:
                if '.' in key:
                    parts = key.split('.')
                    child_key = parts[-1]
                    current = obj
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[child_key] = now - val if val != 0 else val
                else:
                    obj[key] = now - val if val != 0 else val
        return obj

    @staticmethod
    def dict_key_offsets_to_timestamps(keys, now, obj):
        def set_keys(obj_):
            for k in obj_.copy().keys():
                k_offset = int(k)
                k_ts = now - k_offset if k_offset != 0 else k_offset
                obj_[k_ts] = obj_.pop(k)
            return obj_

        for key in keys:
            if '.' in key:
                current = obj
                parts = key.split('.')  # expect key smth like hello.odd.world
                for part in parts[:-1]:
                    if part not in current:
                        break
                    current = current[part]

                child_key = parts[-1]
                val = current.get(child_key)
                if val is not None:
                    current[child_key] = set_keys(val)
            else:
                val = obj.get(key)
                if val is not None:
                    obj[key] = set_keys(val)
        return obj

    @staticmethod
    def offsets_to_datetimes(keys, now, obj, clear_time=False):
        for key in keys:
            val = obj.pop('%s_offset' % key, None)
            if val is not None:
                res = now - val
                if clear_time:
                    res -= (res % (24 * 3600))
                obj[key] = datetime.fromtimestamp(res)
        return obj

    def refresh_relations(self, keys: list, obj: dict):
        def set_value(object_group_, obj_, key_chain_):
            key_ = key_chain_.pop(0)
            if obj_.get(key_):
                if key_chain_:
                    set_value(object_group_, obj_[key_], key_chain_)
                else:
                    if isinstance(obj_[key_], list):
                        for i, val_ in enumerate(obj_[key_]):
                            if isinstance(val_, dict):
                                obj_[key_][i]['id'] = self._recovery_map[
                                    object_group_].get(val_['id'])
                            else:
                                obj_[key_][i] = self._recovery_map[
                                    object_group_].get(val_)
                    else:
                        obj_[key_] = self._recovery_map[object_group_].get(
                            obj_.get(key_))
        for key in keys:
            group_key = '_'.join(key if isinstance(key, list) else [key])
            key_chain = key if isinstance(key, list) else [key]
            object_group = self._key_object_group_map.get(group_key)
            set_value(object_group, obj, key_chain)
        return obj

    def build_cloud_account(self, obj, objects_group, now,
                            organization_id, **kwargs):
        obj = self.refresh_relations(['cost_model_id'], obj)
        if obj.get('cost_model_id'):
            new_id = obj['cost_model_id']
        else:
            new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['auto_import'] = False
        config = {}
        if obj['type'] == CloudTypes.KUBERNETES_CNR.value:
            config.update({
                'url': 'https://%s.com' % gen_id(),
                'port': 4433,
                'user': 'optscale'
            })
        obj['config'] = encode_config(config)
        obj['organization_id'] = organization_id
        obj['account_id'] = gen_id()
        obj = self.offsets_to_timestamps(
            ['created_at', 'last_import_at'], now, obj)
        return CloudAccount(**obj)

    def build_checklist(self, obj, now, organization_id, **kwargs):
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(
            ['last_run', 'created_at', 'last_completed', 'next_run'],
            now, obj)
        return Checklist(**obj)

    def build_employee(self, obj, objects_group, now, organization_id,
                       **kwargs):
        if self._recovery_map[objects_group.value].get(obj['id']):
            return None

        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj.pop('auth_user_id', None)
        return Employee(**obj)

    def build_cluster_type(self, obj, objects_group, now, organization_id,
                           **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return ClusterType(**obj)

    def build_pool(self, obj, objects_group, now, organization_id,
                   **kwargs):
        if self._recovery_map[objects_group.value].get(obj['id']):
            return None

        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.refresh_relations(['default_owner_id'], obj)
        obj.pop('parent_id', None)
        return Pool(**obj)

    def build_cost_model(self, obj, objects_group, now, organization_id, **kwargs):
        if self._recovery_map[objects_group.value].get(obj['id']):
            return None

        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        value = {cm_key: cm_value * self.multiplier
                 for cm_key, cm_value in (obj['value'] or {}).items()}
        obj['value'] = json.dumps(value)
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return CostModel(**obj)

    def build_resource(self, obj, objects_group, now, organization_id, **kwargs):
        for k in ['_id', 'cluster_id']:
            if not obj.get(k):
                continue
            if self._recovery_map[ObjectGroups.CostModels.value].get(obj[k]):
                new_id = self._recovery_map[ObjectGroups.CostModels.value][obj[k]]
                self._recovery_map[objects_group.value][obj[k]] = new_id
                obj[k] = new_id
            elif self._recovery_map[objects_group.value].get(obj[k]):
                obj[k] = self._recovery_map[objects_group.value][obj[k]]
            else:
                new_id = gen_id()
                self._recovery_map[objects_group.value][obj[k]] = new_id
                obj[k] = new_id
        obj = self.offsets_to_timestamps(
            ['created_at', 'last_seen', 'deleted_at',
             'recommendations.run_timestamp', 'meta.start', 'meta.end'],
            now, obj)
        if obj.get('active', False):
            obj['last_seen'] = int((
                datetime.utcnow() + timedelta(days=7)).timestamp())
        obj['_last_seen_date'] = timestamp_to_day_start(obj.get('last_seen', 0))
        obj['_first_seen_date'] = timestamp_to_day_start(
            obj.get('first_seen', 0))
        obj = self.refresh_relations(
            ['employee_id', 'pool_id',
             'cloud_account_id', 'cluster_type_id', 'power_schedule'],
            obj)
        if obj.get('cluster_type_id'):
            obj['organization_id'] = organization_id
        recommendations = obj.get('recommendations')
        if recommendations:
            modules = recommendations.get('modules', [])
            for module in modules:
                for field in RECOMMENDATION_MULTIPLIED_FIELDS:
                    if module.get(field):
                        module[field] = module[field] * self.multiplier
        obj['total_cost'] = obj.get('total_cost', 0) * self.multiplier
        return obj

    def build_raw_expense(self, obj, now, **kwargs):
        obj['_id'] = ObjectId()
        obj['cost'] = obj['cost'] * self.multiplier
        obj = self.offsets_to_datetimes(['end_date', 'start_date'], now, obj)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        for field in ['pricing/publicOnDemandCost', 'lineItem/UnblendedCost',
                      'reservation/EffectiveCost',
                      'savingsPlan/SavingsPlanEffectiveCost']:
            if field in obj:
                obj[field] = float(obj[field]) * self.multiplier
        return obj

    def build_clean_expense(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj, clear_time=True)
        obj = self.refresh_relations(['cloud_account_id', 'resource_id'], obj)
        multipliered_cost = obj['cost'] * self.multiplier
        # TODO: temp map while expense contains extra fields. Remove it
        return {
            'cloud_account_id': obj['cloud_account_id'],
            'resource_id': obj['resource_id'],
            'date': obj['date'],
            'cost': multipliered_cost,
            'sign': 1
        }

    def build_traffic_expenses(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj, clear_time=True)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        multipliered_cost = obj['cost'] * self.multiplier
        multipliered_usage = obj['usage'] * self.multiplier
        obj['cost'] = multipliered_cost
        obj['usage'] = multipliered_usage
        return obj

    def build_optimization(self, obj, now, organization_id, **kwargs):
        def _recover_prop(props_2_recover, obj):
            for prop in props_2_recover:
                offset = obj.pop('%s_offset' % prop, None)
                if offset is None:
                    continue
                if offset == 0:
                    offset = now
                obj[prop] = now - offset
            return obj

        props_to_recover = [
            'created_at', 'last_seen_active', 'last_seen_in_attached_state',
            'first_seen', 'last_seen', 'detected_at']
        obj = _recover_prop(props_to_recover, obj)
        obj['organization_id'] = organization_id
        # handle failed checklists
        if isinstance(obj.get('data'), list):
            for data_obj in obj['data']:
                data_obj = _recover_prop(props_to_recover, data_obj)
                data_obj = self.refresh_relations(
                    ['cloud_account_id', 'resource_id',
                     ['owner', 'id'], ['pool', 'id']], data_obj)
                if data_obj.get('snapshots') is not None:
                    for snapshot in data_obj.get('snapshots'):
                        snapshot = self.refresh_relations(
                            ['resource_id'], snapshot)
                for field in RECOMMENDATION_MULTIPLIED_FIELDS:
                    if data_obj.get(field):
                        data_obj[field] = data_obj[field] * self.multiplier
        return obj

    def build_archived_recommendations(self, obj, now, organization_id, **kwargs):
        def _recover_prop(props_2_recover, obj):
            for prop in props_2_recover:
                offset = obj.pop('%s_offset' % prop, None)
                if offset is None:
                    continue
                if offset == 0:
                    offset = now
                obj[prop] = now - offset
            return obj

        props_to_recover = [
            'created_at', 'last_seen_active', 'last_seen_in_attached_state',
            'first_seen', 'last_seen', 'detected_at', 'archived_at']
        obj = _recover_prop(props_to_recover, obj)
        obj['organization_id'] = organization_id
        obj = self.refresh_relations(
            ['cloud_account_id', 'resource_id',
             ['owner', 'id'], ['pool', 'id']], obj)
        if obj.get('snapshots') is not None:
            for snapshot in obj.get('snapshots', []):
                snapshot = self.refresh_relations(
                    ['resource_id'], snapshot)
        for field in RECOMMENDATION_MULTIPLIED_FIELDS:
            if obj.get(field):
                obj[field] *= self.multiplier
        return obj

    def build_pool_policy(self, obj, now, organization_id, **kwargs):
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.refresh_relations(['pool_id'], obj)
        if obj['type'] in self.permitted_constraints_multiplier:
            obj['limit'] = obj['limit'] * self.multiplier
        obj['organization_id'] = organization_id
        return PoolPolicy(**obj)

    def build_resource_constraint(self, obj, now, organization_id, **kwargs):
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.refresh_relations(['resource_id'], obj)
        if obj['type'] in self.permitted_constraints_multiplier:
            obj['limit'] = obj['limit'] * self.multiplier
        obj['organization_id'] = organization_id
        return ResourceConstraint(**obj)

    def build_limit_hit(self, obj, now, organization_id, **kwargs):
        obj = self.offsets_to_timestamps(['created_at', 'time'], now, obj)
        obj = self.refresh_relations(['pool_id', 'resource_id'], obj)
        if obj['type'] in self.permitted_constraints_multiplier:
            obj['constraint_limit'] = obj['constraint_limit'] * self.multiplier
            obj['expense_value'] = obj['expense_value'] * self.multiplier
        obj['organization_id'] = organization_id
        return ConstraintLimitHit(**obj)

    def build_discovery_info(self, obj, now, **kwargs):
        obj = self.offsets_to_timestamps(
            ['created_at', 'last_discovery_at'], now, obj)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        obj['resource_type'] = getattr(ResourceTypes, obj['resource_type'])
        return DiscoveryInfo(**obj)

    def build_node(self, obj, now, **kwargs):
        obj = self.offsets_to_timestamps(
            ['created_at', 'last_seen'], now, obj)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        if obj.get('hourly_price'):
            obj['hourly_price'] = obj['hourly_price'] * self.multiplier
        return K8sNode(**obj)

    def build_rule(self, obj, objects_group, now, organization_id, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.refresh_relations(
            ['owner_id', 'pool_id', 'creator_id'], obj)
        return Rule(**obj)

    def build_condition(self, obj, now, **kwargs):
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.refresh_relations(['rule_id'], obj)
        return Condition(**obj)

    def build_average_metric(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj)
        obj = self.refresh_relations(['cloud_account_id', 'resource_id'], obj)
        return obj

    def build_k8s_metric(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj)
        obj['date'] = obj['date'] + timedelta(days=2)
        obj = self.refresh_relations(['cloud_account_id', 'resource_id'], obj)
        return obj

    def build_shareable_booking(self, obj, now, organization_id, **kwargs):
        obj = self.offsets_to_timestamps(
            ['created_at', 'acquired_since', 'released_at'], now, obj)
        obj = self.refresh_relations(['acquired_by_id', 'resource_id'], obj)
        obj['organization_id'] = organization_id
        return ShareableBooking(**obj)

    def build_organization_option(self, obj, now, organization_id, **kwargs):
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return OrganizationOption(**obj)

    def build_organization_constraint(self, obj, objects_group, now,
                                      organization_id, **kwargs):
        new_id = str(uuid.uuid4())
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj = self.offsets_to_timestamps(['created_at', 'last_run',
                                          'definition.start_date'], now, obj)
        obj = self.dict_key_offsets_to_timestamps(
            ['last_run_result.breakdown'], now, obj)
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        filters = obj['filters']
        for filter_name in ['pool_id', 'owner_id', 'cloud_account_id']:
            if filter_name in filters:
                for i, filter_value in enumerate(filters[filter_name]):
                    if (filter_name == 'pool_id' and filter_value and
                            filter_value.endswith(WITH_SUBPOOLS_SIGN)):
                        new_value = self._recovery_map.get(
                            self._key_object_group_map.get(filter_name)).get(
                            filter_value.removesuffix(
                                WITH_SUBPOOLS_SIGN))
                        new_value += WITH_SUBPOOLS_SIGN
                    else:
                        new_value = self._recovery_map.get(
                            self._key_object_group_map.get(filter_name)).get(
                            filter_value)
                    filters[filter_name][i] = new_value
        obj['filters'] = filters
        if obj['type'] == OrganizationConstraintTypes.EXPIRING_BUDGET.value:
            obj['definition']['total_budget'] *= self.multiplier
        elif obj['type'] == OrganizationConstraintTypes.RECURRING_BUDGET.value:
            obj['definition']['monthly_budget'] *= self.multiplier
        self._org_constraint_type_map[new_id] = obj['type']
        return OrganizationConstraint(**obj)

    def build_organization_limit_hit(self, obj, now, organization_id,
                                     **kwargs):
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        obj = self.dict_key_offsets_to_timestamps(
            ['run_result.breakdown'], now, obj)
        obj = self.refresh_relations(['constraint_id'], obj)
        obj['organization_id'] = organization_id
        if self._org_constraint_type_map[
                obj['constraint_id']] in self.permitted_org_constraints_multiplier:
            obj['constraint_limit'] *= self.multiplier
            obj['value'] *= self.multiplier
        return OrganizationLimitHit(**obj)

    def build_ri_sp_usage(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj, clear_time=True)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        multipliered_on_demand_cost = obj['on_demand_cost'] * self.multiplier
        multipliered_offer_cost = obj['offer_cost'] * self.multiplier
        multipliered_expected_cost = obj['expected_cost'] * self.multiplier
        obj['on_demand_cost'] = multipliered_on_demand_cost
        obj['offer_cost'] = multipliered_offer_cost
        obj['expected_cost'] = multipliered_expected_cost
        return obj

    def build_uncovered_usage(self, obj, now, **kwargs):
        obj = self.offsets_to_datetimes(['date'], now, obj, clear_time=True)
        obj = self.refresh_relations(['cloud_account_id'], obj)
        multipliered_cost = obj['cost'] * self.multiplier
        obj['cost'] = multipliered_cost
        return obj

    def build_metric(self, obj, objects_group, profiling_token, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        return obj

    def build_task(self, obj, objects_group, profiling_token, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        obj['deleted_at'] = 0
        obj = self.refresh_relations(['owner_id', 'metrics'], obj)
        return obj

    def build_dataset(self, obj, now, objects_group, profiling_token, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        obj['deleted_at'] = 0
        obj = self.offsets_to_timestamps([
            'created_at',
            'timespan_from',
            'timespan_to',
        ], now, obj)
        for param in ['timespan_from', 'timespan_to']:
            if param not in obj:
                obj[param] = None
        return obj

    def build_console(self, obj, objects_group, **kwargs):
        obj['_id'] = gen_id()
        obj = self.refresh_relations(['run_id'], obj)
        return obj

    def build_leaderboard_template(
            self, obj, now, objects_group, profiling_token, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        obj['deleted_at'] = 0
        obj = self.refresh_relations(
            ['task_id', 'primary_metric', 'other_metrics', 'filters'], obj)
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return obj

    def build_leaderboard(self, obj, now, profiling_token, **kwargs):
        obj['_id'] = gen_id()
        obj['token'] = profiling_token
        obj['deleted_at'] = 0
        obj = self.refresh_relations(['leaderboard_template_id', 'dataset_ids',
                                      'primary_metric', 'other_metrics',
                                      'filters'], obj)
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return obj

    def build_run(self, obj, objects_group, now, **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        if obj.get('runset_id'):
            obj = self.refresh_relations(['runset_id'], obj)
        if obj.get('dataset_id'):
            obj = self.refresh_relations(['dataset_id'], obj)
        obj = self.refresh_relations(['task_id'], obj)
        obj = self.offsets_to_timestamps(['start', 'finish'], now, obj)
        return obj

    def build_platform(self, obj, **kwargs):
        obj['_id'] = gen_id()
        obj['account_id'] = gen_id()
        return obj

    def build_log(self, obj, now, **kwargs):
        obj['_id'] = gen_id()
        obj = self.refresh_relations(['run_id'], obj)
        obj = self.offsets_to_timestamps(['timestamp'], now, obj)
        return obj

    def build_milestone(self, obj, now, **kwargs):
        obj['_id'] = gen_id()
        obj = self.refresh_relations(['run_id'], obj)
        obj = self.offsets_to_timestamps(['timestamp'], now, obj)
        return obj

    def build_stage(self, obj, now, **kwargs):
        obj['_id'] = gen_id()
        obj = self.refresh_relations(['run_id'], obj)
        obj = self.offsets_to_timestamps(['timestamp'], now, obj)
        return obj

    def build_proc_data(self, obj, now, **kwargs):
        obj['_id'] = gen_id()
        obj = self.refresh_relations(['run_id'], obj)
        obj = self.offsets_to_timestamps(['timestamp'], now, obj)
        return obj

    def build_model(
            self, obj, objects_group, now, profiling_token, **kwargs
    ):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return obj

    def build_model_version(
            self, obj, objects_group, now, profiling_token, **kwargs
    ):
        new_id = gen_id()
        obj['_id'] = new_id
        obj['deleted_at'] = 0
        obj = self.refresh_relations(
            ['model_id', 'run_id'], obj)
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return obj

    def build_artifact(self, obj, objects_group, now, profiling_token,
                       **kwargs):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = profiling_token
        obj = self.offsets_to_timestamps(
            ['created_at', '_created_at_dt'], now, obj)
        obj = self.refresh_relations(['run_id'], obj)
        return obj

    def build_template(
            self, obj, objects_group, now, infrastructure_token, **kwargs
    ):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = infrastructure_token
        obj['deleted_at'] = 0
        obj = self.refresh_relations(
            ['task_ids', 'cloud_account_ids'], obj)
        obj = self.offsets_to_timestamps(['created_at'], now, obj)
        return obj

    def build_runset(
            self, obj, objects_group, now, infrastructure_token, **kwargs
    ):
        new_id = gen_id()
        self._recovery_map[objects_group.value][obj['_id']] = new_id
        obj['_id'] = new_id
        obj['token'] = infrastructure_token
        obj['deleted_at'] = 0
        obj = self.refresh_relations(
            ['template_id', 'task_id', 'cloud_account_id', 'owner_id'],
            obj)
        obj = self.offsets_to_timestamps(
            ['created_at', 'started_at', 'destroyed_at'], now, obj)
        return obj

    def build_runner(self, obj, now, infrastructure_token, **kwargs):
        obj['_id'] = gen_id()
        obj['token'] = infrastructure_token
        obj = self.refresh_relations(
            ['runset_id', 'cloud_account_id', 'task_id', 'run_id'],
            obj)
        obj = self.offsets_to_timestamps(
            ['created_at', 'started_at', 'destroyed_at'], now, obj)
        return obj

    def _multiply_organization_gemini_stats(self, stats: dict) -> dict:
        for k, v in stats.items():
            if isinstance(v, (int, float)):
                stats[k] = v * self.multiplier
            elif isinstance(v, dict):
                stats[k] = self._multiply_organization_gemini_stats(v)
        return stats

    def build_organization_gemini(self, obj, now, organization_id, **kwargs):
        obj['organization_id'] = organization_id
        for bucket in obj.get('filters', {}).get('buckets', []):
            self.refresh_relations(['cloud_account_id'], bucket)
        obj = self.offsets_to_timestamps(
            ['created_at', 'last_run', 'last_completed'], now, obj)
        obj["filters"] = json.dumps(obj.pop("filters"))
        obj["stats"] = json.dumps(self._multiply_organization_gemini_stats(
            obj.pop("stats")))
        return OrganizationGemini(**obj)

    def build_power_schedule(self, obj, objects_group, now, organization_id,
                             **kwargs):
        new_id = str(uuid.uuid4())
        self._recovery_map[objects_group.value][obj['id']] = new_id
        obj['id'] = new_id
        obj['organization_id'] = organization_id
        obj = self.offsets_to_timestamps([
            'created_at', 'start_date', 'end_date', 'last_eval', 'last_run'
        ], now, obj)
        return PowerSchedule(**obj)

    def rollback(self, insertions_map):
        for group, ids in insertions_map.items():
            dest = self._dest_map.get(group)
            if dest is not None:
                dest.delete_many({'_id': {'$in': ids}})
        self.session.rollback()

    def _bind_pools(self):
        pool_relations = []
        for b_id, (parent_id, limit) in self._recovery_map.get(
                ObjectGroups.PoolRelations.value, []).items():
            pool_id = self._recovery_map[
                ObjectGroups.Pools.value].get(b_id)
            parent_id = self._recovery_map[
                ObjectGroups.Pools.value].get(parent_id)
            pool_relations.append({
                Pool.id.name: pool_id,
                Pool.parent_id.name: parent_id,
                Pool.limit.name: limit
            })
        return pool_relations

    @staticmethod
    def _get_auth_user_params(auth_user_data):
        email_head = auth_user_data['user_email'].split('@')[0]
        email = EMAIL_TEMPLATE % '%s.%s' % (email_head, str(uuid.uuid4().hex))
        name = auth_user_data['user_display_name']
        password = str(uuid.uuid4().hex)
        return email, name, password

    def _bind_auth_users(self, organization_id, ignore_list, auth_users_data):
        employee_user_bindings = []
        employee_user_map = {}
        for auth_user_data in auth_users_data:
            old_employee_id = self._recovery_map[
                ObjectGroups.AuthUsers.value].get(auth_user_data['user_id'])
            if not old_employee_id or old_employee_id in ignore_list:
                continue
            new_employee_id = self._recovery_map[
                ObjectGroups.Employees.value][old_employee_id]
            auth_user = employee_user_map.get(new_employee_id)
            if not auth_user:
                email, name, password = self._get_auth_user_params(
                    auth_user_data)
                auth_user = self.create_auth_user(email, password, name)

                employee_user_bindings.append({
                    Employee.id.name: new_employee_id,
                    Employee.auth_user_id.name: auth_user['id']
                })
                employee_user_map[new_employee_id] = auth_user

            assignment_type = InviteAssignmentScopeTypes.ORGANIZATION.value
            scope = self._recovery_map[ObjectGroups.Pools.value].get(
                auth_user_data['assignment_resource_id'], organization_id)
            if scope != organization_id:
                assignment_type = InviteAssignmentScopeTypes.POOL.value

            self.assign_role_to_user(
                auth_user['id'], scope, auth_user_data['role_purpose'],
                assignment_type)

        return employee_user_bindings

    def setup(self, src_replace_employee, dest_replace_employee,
              organization_pool_id, preset):
        self._recovery_map[ObjectGroups.Employees.value] = {
            src_replace_employee: dest_replace_employee
        }

        self._recovery_map[ObjectGroups.PoolRelations.value] = {}
        self._recovery_map[ObjectGroups.Pools.value] = {}
        for pool_data in preset.get(ObjectGroups.Pools.value, []):
            self._recovery_map[ObjectGroups.PoolRelations.value][
                pool_data['id']] = (pool_data.get('parent_id'),
                                    pool_data.get('limit', 0) * self.multiplier)
            if not pool_data.get('parent_id'):
                self._recovery_map[ObjectGroups.Pools.value][
                    pool_data['id']] = organization_pool_id

        self._recovery_map[ObjectGroups.AuthUsers.value] = {}
        for employee_data in preset.get(ObjectGroups.Employees.value, []):
            self._recovery_map[ObjectGroups.AuthUsers.value][
                employee_data.get('auth_user_id', None)] = employee_data['id']

    def _insert_platforms(self, data: list[dict]) -> list[str]:
        # platforms are matched by instance_id over the code so related
        # collection shouldn't have duplicate records. Insert only if missing
        if not data:
            return []
        update_operations = []
        for obj in data:
            update_operations.append(UpdateOne(
                filter={
                    'instance_id': obj['instance_id']
                },
                update={'$setOnInsert': obj},
                upsert=True,
            ))
        res = self.platforms_collection.bulk_write(update_operations)
        return list(res.upserted_ids.values())

    def fill_organization(
            self, organization: Organization, token: ProfilingToken,
            src_replace_employee, dest_replace_employee, preset
    ):
        now = int(datetime.utcnow().replace(
            hour=0, minute=0, second=0).timestamp())
        insertions_map = {}
        self.setup(src_replace_employee, dest_replace_employee,
                   organization.pool_id, preset)
        cloud_accounts = []
        clickhouse_inserted = 0
        duplication_resource_info_map = {}
        for res_cloud_id_map in self._duplication_module_res_info_map.values():
            duplication_resource_info_map.update(res_cloud_id_map)
        try:
            for group in ObjectGroups.rest_objects():
                res = self.recover_objects(
                    group, preset, now=now, organization_id=organization.id,
                    duplication_resource_info_map=duplication_resource_info_map,
                    profiling_token=token.token,
                    infrastructure_token=token.infrastructure_token)
                if group == ObjectGroups.CloudAccounts:
                    cloud_accounts.extend(res)
                dest = self._dest_map.get(group)
                if res and dest is not None:
                    insertions_map[group] = []
                    for i in range(0, len(res), BULK_SIZE):
                        bulk = res[i:i + BULK_SIZE]
                        # generalize on new conditions
                        if group == ObjectGroups.Platforms:
                            obj_ids = self._insert_platforms(bulk)
                        else:
                            obj_ids = dest.insert_many(bulk).inserted_ids
                        insertions_map[group].extend(obj_ids)
                elif res and group in self._clickhouse_table_map:
                    table = self._clickhouse_table_map.get(group)
                    if not table:
                        continue
                    for i in range(0, len(res), CLICKHOUSE_BULK_SIZE):
                        bulk = res[i:i + CLICKHOUSE_BULK_SIZE]
                        cnt = self._insert_clickhouse(table, bulk)
                        clickhouse_inserted += cnt
                else:
                    self.session.add_all(res)
                    self.session.flush()

            pool_relations = self._bind_pools()
            self.session.bulk_update_mappings(Pool, pool_relations)

            employee_user_bindings = self._bind_auth_users(
                organization.id, [src_replace_employee],
                preset.pop(ObjectGroups.AuthUsers.value))
            self.session.bulk_update_mappings(
                Employee, employee_user_bindings)
            self.session.commit()
        except Exception as orig_exc:
            try:
                self.rollback(insertions_map)
                if clickhouse_inserted:
                    self.delete_clickhouse_info(cloud_accounts)
            except Exception as exc:
                LOG.exception('Organization %s rollback failed: %s',
                              organization.id, str(exc))
            raise orig_exc

    def _insert_clickhouse(self, table, bulk):
        db = CLICKHOUSE_TABLE_DB_MAP[table]
        return self.clickhouse_client.execute(
            f'INSERT INTO {db}.{table} VALUES', bulk)

    def delete_clickhouse_info(self, cloud_accounts):
        cloud_account_ids = list(map(lambda x: x.id, cloud_accounts))
        for table in CLICKHOUSE_TABLE_DB_MAP:
            db = CLICKHOUSE_TABLE_DB_MAP[table]
            self.clickhouse_client.execute(
                f'ALTER TABLE {db}.{table} DELETE '
                f'WHERE cloud_account_id in {cloud_account_ids}')

    @staticmethod
    def get_replacement_employee(preset):
        empl_rss_count_map = {}
        for e in preset.get(ObjectGroups.Employees.value, []):
            empl_rss_count_map[e['id']] = 0

        for r in preset.get(ObjectGroups.Resources.value, []):
            employee_id = r.get('employee_id')
            if employee_id:
                empl_rss_count_map[employee_id] += 1

        target_employee_id = None
        for employee_id, count in empl_rss_count_map.items():
            if target_employee_id is None:
                target_employee_id = employee_id
            if empl_rss_count_map[target_employee_id] < count:
                target_employee_id = employee_id

        return target_employee_id

    @staticmethod
    def get_top_resources_by_total_cost(preset):
        resources = preset.get(ObjectGroups.Resources.value, [])
        not_clusters = [x for x in resources
                        if x.get('cluster_type_id') is None]
        top_res = sorted(not_clusters, key=lambda x: x.get('total_cost', 0),
                         reverse=True)[:TOP_NO_DUPLICATE_RESOURCES]
        return [x['_id'] for x in top_res]

    def init_duplication_resources(self, preset):
        top_resources = self.get_top_resources_by_total_cost(preset)
        optimizations = preset.get(ObjectGroups.Optimizations.value, [])
        for optimization in optimizations:
            module_name = optimization.get('module')
            if module_name in DUPLICATION_MODULE_NAMES:
                module_data_list = optimization.get('data', [])
                if (not module_data_list or
                        not isinstance(module_data_list, list)):
                    return
                for module_data in module_data_list:
                    resource_id = module_data.get('resource_id')
                    cloud_resource_id = module_data.get('cloud_resource_id')
                    if (resource_id and cloud_resource_id and
                            resource_id not in top_resources):
                        self._duplication_module_res_info_map[
                            module_name][resource_id] = cloud_resource_id

    def create(self, pregenerate=False, **kwargs):
        result = self._create(pregenerate)
        subscribe_email = kwargs.get('email')
        subscribe = kwargs.get('subscribe', False)
        if subscribe_email:
            self._send_subscribe_email(subscribe_email, subscribe)
        return result

    def _create(self, pregenerate=False):
        if not pregenerate:
            live_demo = self._get_prepared_live_demo()
            if live_demo:
                self.publish_generation_task()
                return live_demo
        org_name, name, email, password = self._get_basic_params()
        LOG.info('%s %s %s %s' % (org_name, name, email, password))
        auth_user = self.create_auth_user(email, password, name)
        organization, employee = RegisterController(
            self.session, self._config, self.token).add_organization(
            org_name, auth_user, is_demo=True)
        profiling_token = BaseProfilingTokenController(
            self.session, self._config, self.token
        ).get_or_create_profiling_token(organization.id)

        preset = self.load_preset(PRESET_FILENAME)
        employee_id_to_replace = self.get_replacement_employee(preset)
        self.init_duplication_resources(preset)
        try:
            self.fill_organization(
                organization, profiling_token, employee_id_to_replace,
                employee.id, preset)
        except Exception as exc:
            LOG.exception(exc)
            raise InternalServerError(Err.OE0451, [str(exc)])
        return {
            'organization_id': organization.id,
            'email': email,
            'password': password
        }

    def _send_subscribe_email(self, email, subscribe):
        recipient = self._config.optscale_email_recipient()
        if not recipient:
            return
        subject = f'[{self._config.public_ip()}] New live demo subscriber'
        template_params = {
            'texts': {
                'user': {
                    'email': email,
                    'subscribe': subscribe
                },
            }
        }
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [recipient], subject, template_type="new_subscriber",
            template_params=template_params, reply_to_email=email)

    def find_demo_organization(self, auth_user_id):
        demo_organization_q = self.session.query(Organization).join(
            Employee, Employee.organization_id == Organization.id
        ).filter(and_(
            Employee.auth_user_id == auth_user_id,
            Employee.deleted.is_(False),
            Organization.is_demo.is_(true()),
            Organization.deleted.is_(False),
            Organization.created_at >= int(
                (datetime.utcnow() - timedelta(days=7)).timestamp())
        ))
        orgs = demo_organization_q.all()
        return len(orgs) == 1

    def _get_prepared_live_demo(self):
        live_demo_threshhold = datetime.utcnow() - timedelta(
            days=PREPARED_DEMO_LIFETIME_DAYS)
        live_demo = self.mongo_client.restapi.live_demos.find_one_and_delete({
            'created_at': {'$gte': int(live_demo_threshhold.timestamp())}
        }, sort=[('created_at', 1)])
        if live_demo:
            live_demo.pop('_id', None)
        return live_demo

    def publish_generation_task(self):
        queue_conn = QConnection('amqp://{user}:{pass}@{host}:{port}'.format(
            **self._config.read_branch('/rabbit')),
            transport_options=RETRY_POLICY)
        task_exchange = Exchange(EXCHANGE_NAME, type='direct')
        with producers[queue_conn].acquire(block=True) as producer:
            producer.publish(
                {},
                serializer='json',
                exchange=task_exchange,
                declare=[task_exchange],
                routing_key=ROUTING_KEY,
                retry=True,
                retry_policy=RETRY_POLICY
            )


class LiveDemoAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return LiveDemoController
