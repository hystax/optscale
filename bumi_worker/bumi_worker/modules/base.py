import json
import logging
from collections import OrderedDict
from contextlib import ContextDecorator
from datetime import datetime, timedelta
from kombu import Connection as QConnection
from kombu import Exchange
from kombu.pools import producers

from pymongo import MongoClient, UpdateOne
from rest_api_client.client_v2 import Client as RestClient
from clickhouse_driver import Client as ClickHouseClient

from bumi_worker.consts import ArchiveReason

ACTIVITIES_EXCHANGE_NAME = 'activities-tasks'
ACTIVITIES_EXCHANGE = Exchange(ACTIVITIES_EXCHANGE_NAME, type='topic')
BULK_SIZE = 2000
DAYS_IN_MONTH = 30
LOG = logging.getLogger(__name__)


class time_measure(ContextDecorator):
    def __init__(self, module, module_type, organization_id):
        self.module = module
        self.module_type = module_type
        self.organization_id = organization_id
        self._start = None

    def __enter__(self):
        self._start = datetime.utcnow().timestamp()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        total = datetime.utcnow().timestamp() - self._start
        LOG.info(
            '%s module %s (organization_id %s) completed in %0.2f seconds',
            self.module_type.capitalize(), self.module, self.organization_id, total)


class ServiceBase(object):
    def __init__(self, organization_id, config_client, created_at):
        self.organization_id = organization_id
        self.config_cl = config_client
        self.created_at = created_at
        self._rest_client = None
        self._mongo_client = None
        self.option_ordered_map = {}
        self._options = None

    @classmethod
    def get_name(cls):
        return cls.__module__.split('.')[-1]

    @classmethod
    def get_type(cls):
        return cls.__module__.split('.')[-2]

    @property
    def rest_client(self):
        if self._rest_client is None:
            self._rest_client = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_client.secret = self.config_cl.cluster_secret()
        return self._rest_client

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    def get_options(self):
        if self._options is None:
            self._options = OrderedDict()
            stored_options = self._get_stored_options()
            for option_name, option_params in self.option_ordered_map.items():
                default_value = option_params.get('default')
                clean_func = option_params.get('clean_func')
                option_value = stored_options.get(option_name, default_value)
                if clean_func:
                    option_value = clean_func(option_value, default_value)
                self._options[option_name] = option_value
            LOG.info('Active options for %s: %s', self.get_name(), self._options)
            if self._options != stored_options:
                self._set_stored_options(self._options)
        return self._options

    def _get_stored_options(self):
        _, response = self.rest_client.organization_option_get(
            self.organization_id, 'recommendation_' + self.get_name())
        return json.loads(response['value'])

    def _set_stored_options(self, options):
        _, response = self.rest_client.organization_option_update(
            self.organization_id, 'recommendation_' + self.get_name(),
            {'value': json.dumps(options)})
        return json.loads(response['value'])

    def get_options_values(self):
        return tuple(self.get_options().values())

    def _get(self):
        raise NotImplementedError()

    def _publish_activities_tasks(self, tasks, routing_key):
        queue_conn = QConnection(
            'amqp://{user}:{pass}@{host}:{port}'.format(
                **self.config_cl.read_branch('/rabbit')))
        with producers[queue_conn].acquire(block=True) as producer:
            for task in tasks:
                producer.publish(
                    task,
                    serializer='json',
                    exchange=ACTIVITIES_EXCHANGE,
                    declare=[ACTIVITIES_EXCHANGE],
                    routing_key=routing_key,
                    retry=True
                )

    def get(self):
        try:
            error = None
            with time_measure(self.get_name(), self.get_type(),
                              self.organization_id):
                module_res = self._get()
        except Exception as ex:
            error = str(ex) or str(type(ex))
            module_res = None
            LOG.exception(
                'Error while processing %s (%s) for organization %s. Reason - %s',
                self.get_name(), self.get_type(), self.organization_id, error)
        return module_res, self.get_options(), error


class ModuleBase(ServiceBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clickhouse_client = None

    @property
    def is_resource_based(self):
        return True

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, db_name = self.config_cl.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_client

    @property
    def unique_record_keys(self):
        return 'cloud_account_id', 'cloud_resource_id',

    def get_employees(self):
        _, response = self.rest_client.employee_list(self.organization_id)
        return {x['id']: x for x in response['employees']}

    def get_cloud_accounts(self, supported_cloud_types=None,
                           skip_cloud_accounts=None, only_type=False):
        _, response = self.rest_client.cloud_account_list(
            self.organization_id, process_recommendations=True)
        cloud_accounts = response['cloud_accounts']
        cloud_account_map = {}
        for cloud_account in cloud_accounts:
            cloud_account_id = cloud_account['id']
            cloud_type = cloud_account['type']
            if (supported_cloud_types and cloud_type not in
                    supported_cloud_types):
                continue
            if (skip_cloud_accounts and cloud_account_id in
                    skip_cloud_accounts):
                continue
            if only_type:
                cloud_account_map[cloud_account_id] = cloud_type
            else:
                cloud_account_map[cloud_account_id] = cloud_account
        return cloud_account_map

    def get_pools(self):
        _, organization = self.rest_client.organization_get(
            self.organization_id)
        _, org_pool = self.rest_client.pool_get(
            organization['pool_id'], children=True)
        pools = {x['id']: x for x in org_pool['children']}
        pools[org_pool['id']] = org_pool
        return pools

    def _extract_owner(self, employee_id, employees_map):
        employee = employees_map.get(employee_id)
        if employee_id and employee:
            return {
                'id': employee_id,
                'name': employee['name'],
            }

    def _extract_pool(self, pool_id, pools_map):
        pool = pools_map.get(pool_id)
        if pool_id and pool:
            return {
                'id': pool_id,
                'name': pool['name'],
                'purpose': pool['purpose'],
            }

    def clean_excluded_pools(self, pools_map, default_value):
        existing_pools = self.get_pools()
        return {k: True for k, v in pools_map.items()
                if k in existing_pools and v}

    def get_resources_stuck_in_state(self, resource_type, status_field_name,
                                     date_field_name, resource_stuck_condition,
                                     cloud_account_ids, delta_days=1):
        _, response = self.rest_client.cloud_resources_discover(
            self.organization_id, resource_type)
        starting_point = int(
            (datetime.utcnow() - timedelta(days=delta_days)).timestamp()
        )
        today = datetime.utcnow().replace(hour=0, minute=0, second=0,
                                          microsecond=0)
        month_ago_timestamp = (today - timedelta(days=1) - timedelta(
            days=DAYS_IN_MONTH))
        resources = response['data']

        def matched_resource(resource):
            status_check = resource['meta'][status_field_name] == resource_stuck_condition
            date_check = resource['meta'][date_field_name] < starting_point
            cloud_check = resource['cloud_account_id'] in cloud_account_ids
            return status_check and date_check and cloud_check

        def get_by_cost_saving_timestamp(resource, is_saving=True):
            res_dt = resource['meta'][date_field_name]
            if is_saving:
                return (month_ago_timestamp if
                        int(month_ago_timestamp.timestamp()) > res_dt else
                        datetime.utcfromtimestamp(res_dt).replace(
                            hour=0, minute=0, second=0, microsecond=0))
            else:
                return datetime.utcfromtimestamp(res_dt).replace(
                    hour=0, minute=0, second=0, microsecond=0)

        def get_cost_saving(is_saving=True):
            external_table = [{
                'id': r_id,
                'date': get_by_cost_saving_timestamp(r, is_saving)
            } for r_id, r in filtered_resources.items()]
            query = """
                SELECT resource_id, sum(sign), sum(cost * sign)
                FROM expenses
                JOIN resources ON resource_id = resources.id
                WHERE date >= resources.date
                    AND or(date != %(today)s, cost != 0)
                GROUP BY resource_id
            """
            return self.clickhouse_client.execute(
                query=query,
                external_tables=[{
                    'name': 'resources',
                    'structure': [('id', 'String'), ('date', 'Date')],
                    'data': external_table
                }],
                params={
                    'today': today
                }
            )

        filtered_resources = {r['resource_id']: r
                              for r in resources if matched_resource(r)}
        if not filtered_resources:
            return {}
        # get saving from the last used date or from the last month
        saving_expenses_res = get_cost_saving()
        # get costs from the all period from last used date, if we have
        # saving then we have also cost. We need costs for the all period.
        cost_expenses_res = {
            e[0]: e[2] for e in get_cost_saving(is_saving=False)
        }
        for expense in saving_expenses_res:
            resource_id, days, cost = expense
            filtered_resource = filtered_resources[resource_id]
            # if we don't have last state date info - check when resource was
            # created and skip if less than 1 day ago
            if days == 1 and filtered_resource['meta'][date_field_name] == 0:
                _, resource_obj = self.rest_client.cloud_resource_get(
                    resource_id
                )
                if resource_obj['created_at'] > starting_point:
                    continue

            filtered_resource[
                'cost_in_resource_state'] = cost_expenses_res.get(
                resource_id)
            filtered_resource['savings'] = (cost / days * DAYS_IN_MONTH)
        return filtered_resources

    def _handle_dismissed(self, module_result):
        # empty or doesn't support suppressing
        if not module_result or not module_result[0].get('resource_id'):
            return module_result
        for i in range(0, len(module_result), BULK_SIZE):
            resource_id_pos_map = {
                r['resource_id']: i + n for n, r in enumerate(
                    module_result[i:i + BULK_SIZE])}
            dismissed_objs = self.mongo_client.restapi.resources.find({
                '_id': {'$in': list(resource_id_pos_map.keys())},
                'dismissed': self.get_name()
            })
            dismissed_objs = list(dismissed_objs)
            for dismissed_obj in dismissed_objs:
                module_res_pos = resource_id_pos_map.get(dismissed_obj['_id'])
                if module_res_pos is None:
                    continue
                module_result[module_res_pos]['is_dismissed'] = True
        return module_result

    def load_previous_result(self):
        pipeline = [
            {'$match': {'$and': [
                {'organization_id': self.organization_id},
                {'module': self.get_name()},
                {'data': {'$type': "array"}}
            ]}},
            {'$sort': {'created_at': -1}},
            {'$limit': 1},
            {'$unwind': "$data"},
            {'$replaceRoot': {'newRoot': "$data"}}
        ]
        return list(self.mongo_client.restapi.checklists.aggregate(
            pipeline, allowDiskUse=True))

    def get_record_key(self, record):
        return tuple(record[k] for k in self.unique_record_keys)

    def set_detection_field(self, module_res, previous_module_res):
        optimization_detection_map = {
            self.get_record_key(r): r.get('detected_at')
            for r in previous_module_res}
        for r in module_res:
            record_key = self.get_record_key(r)
            detected_at = optimization_detection_map.get(record_key)
            if not detected_at:
                LOG.info('Detected new optimization %s in %s for organization %s',
                         record_key, self.get_name(), self.organization_id)
                detected_at = self.created_at
            r['detected_at'] = detected_at
        return module_res

    def get(self):
        error = None
        previous_module_res = self.load_previous_result()
        try:
            with time_measure(self.get_name(), self.get_type(),
                              self.organization_id):
                module_res = self._get()
            module_res = self.set_detection_field(
                module_res, previous_module_res)
            if self.is_resource_based:
                module_res = self._handle_dismissed(module_res)
        except Exception as ex:
            error = str(ex) or str(type(ex))
            module_res = previous_module_res
            LOG.exception(
                'Error while processing %s (%s) for organization %s, failing back '
                'to previous result. Reason - %s',
                self.get_name(), self.get_type(), self.organization_id, error)
        return module_res, self.get_options(), error


class ArchiveBase(ModuleBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map = {
            ArchiveReason.OPTIONS_CHANGED: 'options changed',
            ArchiveReason.CLOUD_ACCOUNT_DELETED: 'cloud account deleted',
            ArchiveReason.RECOMMENDATION_IRRELEVANT: 'recommendation irrelevant',
            ArchiveReason.RESOURCE_DELETED: 'resource deleted',
            ArchiveReason.FAILED_DEPENDENCY: 'failed dependency',
            ArchiveReason.RECOMMENDATION_APPLIED: 'recommendation applied'
        }

    @property
    def supported_cloud_types(self):
        raise NotImplementedError

    def _set_reason_properties(self, recommendation_object, reason,
                               description=None):
        recommendation_object['reason'] = reason
        description_ = description or self.reason_description_map.get(reason)
        recommendation_object['description'] = description_

    def _load_checklists(self):
        """
        Load 2 latest checklists which supposed to be compared
        :return: list of checklists
        """
        pipeline = [
            {'$match': {'$and': [
                {'organization_id': self.organization_id},
                {'module': self.get_name()},
                {'data': {'$type': "array"}}
            ]}},
            {'$sort': {'created_at': -1}},
            {'$limit': 2},
        ]
        return list(self.mongo_client.restapi.checklists.aggregate(pipeline))

    def get_archive_candidates(self, module_data, previous_module_data,
                               cloud_accounts_map):
        result = []
        current_data = {self.get_record_key(r) for r in module_data}
        for record in previous_module_data:
            record_key = self.get_record_key(record)
            if record_key not in current_data:
                if not record.get('is_excluded', False) and not record.get(
                        'is_dismissed', False):
                    record['cloud_account_name'] = cloud_accounts_map.get(
                        record['cloud_account_id'], {}).get('name')
                    result.append(record)
        return result

    def _get(self, *args, **kwargs):
        raise NotImplementedError

    def _archive_data(self, data, archived_at):
        module = self.get_name()
        for obj in data:
            obj['organization_id'] = self.organization_id
            obj['module'] = module
            obj['archived_at'] = archived_at

        filter_fields = {'module', 'archived_at', 'organization_id'}
        filter_fields.update(self.unique_record_keys)
        self.mongo_client.restapi.archived_recommendations.bulk_write([
            UpdateOne(
                filter={k: obj[k] for k in filter_fields},
                update={
                    '$set': {k: v for k, v in obj.items()
                             if k not in filter_fields},
                    '$setOnInsert': {k: v for k, v in obj.items()
                                     if k in filter_fields},
                },
                upsert=True,
            ) for obj in data
        ])

    def get(self):
        try:
            error = None
            with time_measure(self.get_name(), self.get_type(),
                              self.organization_id):
                checklists = self._load_checklists()
                if len(checklists) == 0:
                    raise ValueError('Checklists not found')
                elif len(checklists) == 1:
                    if checklists[0].get('created_at') == self.created_at:
                        LOG.warning(
                            'Skipping %s (%s) initial run for organization %s',
                            self.get_name(), self.get_type(),
                            self.organization_id)
                    else:
                        raise ValueError('Running checklist not found')
                else:
                    current, previous = checklists
                    if current.get('created_at') != self.created_at:
                        raise ValueError('Running checklist not found')
                    previous_options = previous.get('options', {})
                    skip_cloud_accounts = previous_options['skip_cloud_accounts']
                    cloud_accounts_map = self.get_cloud_accounts(
                        self.supported_cloud_types, skip_cloud_accounts)
                    archive_candidates = self.get_archive_candidates(
                        current.get('data', []), previous.get('data', []),
                        cloud_accounts_map)
                    if archive_candidates:
                        res = self._get(previous_options, archive_candidates,
                                        cloud_accounts_map)
                        self._archive_data(res, previous['created_at'])
        except Exception as ex:
            error = str(ex) or str(type(ex))
            LOG.exception(
                'Error while processing %s (%s) for organization %s. Reason - %s',
                self.get_name(), self.get_type(), self.organization_id, error)
        return None, None, error
