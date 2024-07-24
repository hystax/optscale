from collections import defaultdict
from datetime import datetime, timedelta

from rest_api.rest_api_server.controllers.base import (
    BaseProfilingTokenController, MongoMixin, ClickHouseMixin)
from rest_api.rest_api_server.models.enums import RunStates
from rest_api.rest_api_server.models.models import CloudAccount
from rest_api.rest_api_server.utils import handle_http_exc

DAY_IN_HOURS = 24
HOUR_IN_SEC = 3600


def format_cloud_account(cloud_account: CloudAccount) -> dict:
    return {
        'id': cloud_account.id,
        'name': cloud_account.name,
        'type': cloud_account.type.value
    }


def format_task(task: dict):
    if task is None:
        return {}
    return {
        'id': task['_id'],
        'name': task['name'],
        'deleted': task['deleted_at'] != 0
    }


def format_dataset(dataset: dict) -> dict:
    return {
        'id': dataset.get('id') or dataset.get('_id'),
        'name': dataset['name'],
        'deleted': dataset['deleted_at'] != 0,
        'path': dataset['path'],
        'labels': dataset['labels'],
        'timespan_from': dataset['timespan_from'],
        'timespan_to': dataset['timespan_to'],
        'description': dataset.get('description')
    }


class ArceeObject:
    INNER_OBJECTS = {}
    REMOVE_KEYS = ['token']
    REPLACE_KEYS = {'_id': 'id'}

    @classmethod
    def format(cls, obj):
        for k in cls.REMOVE_KEYS:
            obj.pop(k, None)
        for k, new_k in cls.REPLACE_KEYS.items():
            if k in obj:
                obj[new_k] = obj.pop(k)
        for k, cl in cls.INNER_OBJECTS.items():
            if k in obj:
                v = obj.get(k, None)
                if not v:
                    continue
                if isinstance(v, list):
                    for i in v:
                        if isinstance(i, dict):
                            cl.format(i)
                elif isinstance(v, dict):
                    cl.format(v)


class Task(ArceeObject):
    REPLACE_KEYS = {
        **ArceeObject.REPLACE_KEYS,
        'taskMetrics': 'metrics'
    }
    INNER_OBJECTS = {'metrics': ArceeObject}


class Run(ArceeObject):
    REPLACE_KEYS = {
        **ArceeObject.REPLACE_KEYS,
        'runExecutors': 'executors'
    }
    INNER_OBJECTS = {
        'task': Task,
        'executors': ArceeObject
    }

    @classmethod
    def format(cls, obj):
        super().format(obj)
        if not obj.get('executors'):
            obj['executors'] = []


class RunCostsMixin(MongoMixin, ClickHouseMixin):
    @staticmethod
    def __calculate_instance_work(expenses) -> float:
        working_hours = 0
        for e in expenses:
            if e.get('lineItem/UsageAmount'):
                working_hours += float(e['lineItem/UsageAmount'])
            elif e.get('usage_quantity'):
                working_hours += float(e['usage_quantity'])
            elif e.get('Usage'):
                working_hours += float(e['Usage'])
        return working_hours or DAY_IN_HOURS

    def _get_run_costs(self, cloud_account_ids: list, runs: list) -> dict:
        if not runs:
            return {}
        min_dt, max_dt = None, None
        executors = set()
        run_executor_duration_map = defaultdict(dict)
        now = datetime.utcnow().timestamp()
        for r in runs:
            r_start = r.get('start') or 0
            r_finish = r.get('finish') or 0
            if not r_finish and r['state'] == RunStates.running:
                r_finish = now
            duration = r_finish - r_start
            r_start = datetime.fromtimestamp(r_start).replace(
                hour=0, minute=0, second=0, microsecond=0)
            r_finish = datetime.fromtimestamp(r_finish).replace(
                hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            if not min_dt or min_dt > r_start:
                min_dt = r_start
            if not max_dt or max_dt < r_finish:
                max_dt = r_finish
            for executor in r['executors']:
                if isinstance(executor, dict):
                    executor = executor['id']
                executors.add(executor)
                run_executor_duration_map[r['id']][executor] = duration
        pipeline = [
            {'$match': {
                'cloud_account_id': {'$in': cloud_account_ids},
                'start_date': {'$gte': min_dt, '$lt': max_dt},
                'end_date': {'$lte': max_dt},
                'resource_id': {'$in': list(executors)},
                'box_usage': True
            }},
            {'$project': {
                'resource_id': 1,
                'lineItem/UsageAmount': 1,  # aws
                'usage_quantity': 1,  # azure
                'Usage': 1,  # ali
            }}
        ]
        exp_map = defaultdict(list)
        for exp in self.raw_expenses_collection.aggregate(pipeline):
            exp_map[exp['resource_id']].append(exp)
        result = {}
        executor_work_map = {}
        for resource_id, expenses in exp_map.items():
            executor_work_map[resource_id] = self.__calculate_instance_work(
                expenses)
        executor_costs = self._get_executor_costs(
            cloud_account_ids, list(executors), min_dt, max_dt)
        for run in runs:
            run_id = run['id']
            cost = 0
            for executor, duration in run_executor_duration_map.get(
                    run_id, {}).items():
                w_cost = executor_costs.get(executor, 0)
                working_hours = executor_work_map.get(
                    executor, DAY_IN_HOURS)
                # cost for what period in hours was collected
                w_time = working_hours * HOUR_IN_SEC
                cost += w_cost * duration / w_time
            result[run_id] = cost
        return result

    def _get_resource_ids_map(self, cloud_account_ids, cloud_resource_ids):
        resources = self.resources_collection.find({
            'cloud_account_id': {'$in': cloud_account_ids},
            'cloud_resource_id': {'$in': cloud_resource_ids}
        }, ['_id', 'cloud_resource_id'])
        return {r['_id']: r['cloud_resource_id'] for r in resources}

    def _get_executor_costs(self, cloud_account_ids, cloud_resource_ids,
                            start_date, end_date):
        resource_ids_map = self._get_resource_ids_map(cloud_account_ids,
                                                      cloud_resource_ids)
        query = """
            SELECT
                resource_id, SUM(cost * sign)
            FROM expenses
            WHERE cloud_account_id IN cloud_account_ids
                AND resource_id IN resource_ids
                AND date >= %(start_date)s
                AND date <= %(end_date)s
            GROUP BY resource_id
            HAVING SUM(sign) > 0
        """
        expenses = self.execute_clickhouse(
            query=query,
            params={
                'start_date': start_date,
                'end_date': end_date,
            },
            external_tables=[
                {
                    'name': 'resource_ids',
                    'structure': [('_id', 'String')],
                    'data': [
                        {'_id': r_id} for r_id in list(resource_ids_map.keys())
                    ]
                },
                {
                    'name': 'cloud_account_ids',
                    'structure': [('_id', 'String')],
                    'data': [{'_id': r_id} for r_id in cloud_account_ids]
                }
            ],
        )
        result = {}
        for r_id, cost in expenses:
            result[resource_ids_map[r_id]] = cost
        return result


class BaseProfilingController(BaseProfilingTokenController):
    def _get_cloud_accounts(self, organization_id) -> dict[str, dict]:
        cloud_accounts_q = self.session.query(CloudAccount).filter(
            CloudAccount.deleted.is_(False),
            CloudAccount.organization_id == organization_id
        )
        return {ca.id: format_cloud_account(ca)
                for ca in cloud_accounts_q.all()}

    def get_profiling_token(self, organization_id):
        profiling_token = self.get_or_create_profiling_token(organization_id)
        return profiling_token.token

    @handle_http_exc
    def create_task(self, profiling_token, task_key, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, task = arcee.task_create(
            task_key=task_key, **kwargs)
        Task.format(task)
        return task

    @handle_http_exc
    def get_task(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, task = arcee.task_get(task_id)
        Task.format(task)
        return task

    @handle_http_exc
    def list_tasks(self, profiling_token) -> list[dict]:
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.tasks_get()
        for r in response:
            Task.format(r)
        return response

    @handle_http_exc
    def bulk_get_tasks(self, profiling_token, task_ids, include_deleted=False):
        arcee = self.get_arcee_client(profiling_token)
        _, tasks = arcee.tasks_bulk_get(
            task_ids, include_deleted)
        return tasks

    @handle_http_exc
    def update_task(self, profiling_token, task_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated_task = arcee.task_update(task_id, **kwargs)
        return updated_task

    @handle_http_exc
    def delete_task(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.task_delete(task_id)

    @handle_http_exc
    def list_task_runs(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, runs = arcee.tasks_runs_get(task_id)
        for r in runs:
            Run.format(r)
        return runs

    @handle_http_exc
    def list_runs(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, runs = arcee.runs_bulk_get()
        for r in runs:
            Run.format(r)
        return runs

    @handle_http_exc
    def get_executors(self, profiling_token, task_ids=None, run_ids=None):
        if not task_ids and not run_ids:
            return []
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.executors_get(task_ids, run_ids)
        for r in response:
            ArceeObject.format(r)
        return response

    @handle_http_exc
    def list_logs(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, logs = arcee.run_logs_get(run_id)
        for log in logs:
            ArceeObject.format(log)
        return logs

    @handle_http_exc
    def list_proc_data(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, proc_data = arcee.proc_data_get(run_id)
        for d in proc_data:
            ArceeObject.format(d)
        return proc_data

    @handle_http_exc
    def get_metric(self, profiling_token, metric_id):
        arcee = self.get_arcee_client(profiling_token)
        _, metric = arcee.metric_get(metric_id)
        ArceeObject.format(metric)
        return metric

    @handle_http_exc
    def list_metrics(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.metrics_get()
        for r in response:
            ArceeObject.format(r)
        return response

    @handle_http_exc
    def create_metric(self, profiling_token, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, metric = arcee.metrics_create(**kwargs)
        ArceeObject.format(metric)
        return metric

    @handle_http_exc
    def update_metric(self, profiling_token, metric_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated = arcee.metrics_update(metric_id, **kwargs)
        return updated

    @handle_http_exc
    def delete_metric(self, profiling_token, metric_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.metric_delete(metric_id)

    @handle_http_exc
    def get_run(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, run = arcee.run_get(run_id)
        Run.format(run)
        return run

    @handle_http_exc
    def delete_run(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.run_delete(run_id)

    @handle_http_exc
    def list_milestones(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, milestones = arcee.run_milestones_get(run_id)
        for m in milestones:
            ArceeObject.format(m)
        return milestones

    @handle_http_exc
    def list_stages(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, run = arcee.run_get(run_id)
        _, stages = arcee.stages_get(run_id)
        stages_count = len(stages)
        stages_result = list()
        for i, v in enumerate(stages):
            start = v.pop("timestamp")
            stages_result.append(v)
            stages_result[i]['start'] = start
            if i > 0:
                stages_result[i - 1]['end'] = start
            if i == stages_count - 1:
                stages_result[i]['end'] = run['finish']
            ArceeObject.format(stages_result[i])
        return stages_result

    @handle_http_exc
    def get_leaderboard(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard = arcee.leaderboard_get(task_id)
        ArceeObject.format(leaderboard)
        return leaderboard

    @handle_http_exc
    def create_leaderboard(self, profiling_token, task_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard = arcee.leaderboards_create(task_id, **kwargs)
        ArceeObject.format(leaderboard)
        return leaderboard

    @handle_http_exc
    def create_leaderboard_dataset(self, profiling_token, leaderboard_id,
                                   **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard = arcee.leaderboard_dataset_create(leaderboard_id,
                                                          **kwargs)
        ArceeObject.format(leaderboard)
        return leaderboard

    @handle_http_exc
    def update_leaderboard_dataset(self, profiling_token,
                                   leaderboard_dataset_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard_dataset = arcee.leaderboard_dataset_update(
            leaderboard_dataset_id, **kwargs)
        ArceeObject.format(leaderboard_dataset)
        return leaderboard_dataset

    @handle_http_exc
    def list_leaderboard_dataset(self, profiling_token, leaderboard_id,
                                 **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard_datasets = arcee.leaderboard_datasets_get(
            leaderboard_id, **kwargs)
        for leaderboard_dataset in leaderboard_datasets:
            ArceeObject.format(leaderboard_dataset)
        return leaderboard_datasets

    @handle_http_exc
    def get_leaderboard_dataset(self, profiling_token, leaderboard_dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard_dataset = arcee.leaderboard_dataset_get(
            leaderboard_dataset_id)
        ArceeObject.format(leaderboard_dataset)
        return leaderboard_dataset

    @handle_http_exc
    def delete_leaderboard_dataset(self, profiling_token,
                                   leaderboard_dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.leaderboard_dataset_delete(leaderboard_dataset_id)

    @handle_http_exc
    def update_leaderboard(self, profiling_token, task_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated = arcee.leaderboard_update(task_id, **kwargs)
        return updated

    @handle_http_exc
    def delete_leaderboard(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.leaderboard_delete(task_id)

    @handle_http_exc
    def get_leaderboard_details(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard = arcee.leaderboard_details_get(task_id)
        ArceeObject.format(leaderboard)
        return leaderboard

    @handle_http_exc
    def get_leaderboard_dataset_details(self, profiling_token, leaderboard_dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard_dataset_details = arcee.leaderboard_dataset_details(leaderboard_dataset_id)
        for i in leaderboard_dataset_details:
            ArceeObject.format(i)
        return leaderboard_dataset_details

    @handle_http_exc
    def generate_leaderboard(self, profiling_token, leaderboard_dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        _, leaderboard = arcee.leaderboard_generate(leaderboard_dataset_id)
        return leaderboard

    @handle_http_exc
    def bulk_gen_runs(self, profiling_token, task_id, run_ids):
        arcee = self.get_arcee_client(profiling_token)
        _, runs = arcee.runs_bulk_get_by_ids(task_id, run_ids)
        return runs

    @handle_http_exc
    def get_dataset(self, profiling_token, dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        _, dataset = arcee.dataset_get(dataset_id)
        ArceeObject.format(dataset)
        return dataset

    @handle_http_exc
    def list_datasets(self, profiling_token, include_deleted=False):
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.dataset_list(include_deleted)
        for r in response:
            ArceeObject.format(r)
        return response

    @handle_http_exc
    def create_dataset(self, profiling_token, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, dataset = arcee.dataset_create(**kwargs)
        ArceeObject.format(dataset)
        return dataset

    @handle_http_exc
    def update_dataset(self, profiling_token, dataset_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, dataset = arcee.dataset_update(dataset_id, **kwargs)
        return dataset

    @handle_http_exc
    def delete_dataset(self, profiling_token, dataset_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.dataset_delete(dataset_id)

    @handle_http_exc
    def list_labels(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, labels = arcee.labels_list()
        return labels

    @handle_http_exc
    def list_tags(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, tags = arcee.tags_list(task_id)
        return tags

    @handle_http_exc
    def get_console(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, console = arcee.console_get(run_id)
        return console

    @handle_http_exc
    def get_executors_breakdown(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, breakdown = arcee.executors_breakdown_get()
        return breakdown

    @handle_http_exc
    def create_model(self, profiling_token, key, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, model = arcee.model_create(key=key, **kwargs)
        ArceeObject.format(model)
        return model

    @handle_http_exc
    def list_models(self, profiling_token) -> list[dict]:
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.models_get()
        for r in response:
            ArceeObject.format(r)
            ArceeObject.format(r['last_version'])
            for version in r['aliased_versions']:
                ArceeObject.format(version)
        return response

    @handle_http_exc
    def get_model(self, profiling_token, model_id):
        arcee = self.get_arcee_client(profiling_token)
        _, model = arcee.model_get(model_id)
        ArceeObject.format(model)
        for version in model['versions']:
            ArceeObject.format(version)
            ArceeObject.format(version.get('run', {}))
        return model

    @handle_http_exc
    def update_model(self, profiling_token, model_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated_app = arcee.model_update(model_id, **kwargs)
        ArceeObject.format(updated_app)
        return updated_app

    @handle_http_exc
    def delete_model(self, profiling_token, model_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.model_delete(model_id)

    @handle_http_exc
    def create_model_version(self, profiling_token, run_id, model_id,
                             **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, model_version = arcee.model_version_create(
            run_id, model_id, **kwargs)
        ArceeObject.format(model_version)
        return model_version

    @handle_http_exc
    def update_model_version(self, profiling_token, run_id, model_id,
                             **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated_version = arcee.model_version_update(
            run_id, model_id, **kwargs)
        ArceeObject.format(updated_version)
        return updated_version

    @handle_http_exc
    def delete_model_version(self, profiling_token, run_id, model_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.model_version_delete(run_id, model_id)

    @handle_http_exc
    def get_model_version_by_task(self, profiling_token, task_id):
        arcee = self.get_arcee_client(profiling_token)
        _, model_versions = arcee.model_versions_by_task(task_id)
        for model_version in model_versions:
            ArceeObject.format(model_version)
            ArceeObject.format(model_version.get('model', {}))
            ArceeObject.format(model_version.get('run', {}))
        return model_versions

    @handle_http_exc
    def create_artifact(self, profiling_token, run_id, path, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, artifact = arcee.artifact_create(
            run_id=run_id, path=path, **kwargs)
        ArceeObject.format(artifact)
        ArceeObject.format(artifact['run'])
        return artifact

    @handle_http_exc
    def list_artifacts(self, profiling_token, **kwargs) -> list[dict]:
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.artifacts_get(**kwargs)
        for r in response['artifacts']:
            r.pop('_created_at_dt', None)
            ArceeObject.format(r)
            ArceeObject.format(r['run'])
        return response

    @handle_http_exc
    def get_artifact(self, profiling_token, artifact_id):
        arcee = self.get_arcee_client(profiling_token)
        _, artifact = arcee.artifact_get(artifact_id)
        artifact.pop('_created_at_dt', None)
        ArceeObject.format(artifact)
        ArceeObject.format(artifact['run'])
        return artifact

    @handle_http_exc
    def update_artifact(self, profiling_token, artifact_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated_artifact = arcee.artifact_update(artifact_id, **kwargs)
        updated_artifact.pop('_created_at_dt', None)
        ArceeObject.format(updated_artifact)
        ArceeObject.format(updated_artifact['run'])
        return updated_artifact

    @handle_http_exc
    def delete_artifact(self, profiling_token, artifact_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.artifact_delete(artifact_id)
