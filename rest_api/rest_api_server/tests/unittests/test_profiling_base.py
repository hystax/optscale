from datetime import datetime, timezone
import uuid
from typing import Optional, List

from rest_api.rest_api_server.tests.unittests.test_api_base import TestApiBase
from unittest.mock import patch, PropertyMock
from requests.exceptions import HTTPError
from requests.models import Response
from collections import defaultdict, OrderedDict


class TestProfilingBase(TestApiBase):
    def setUp(self, version='v2'):
        super().setUp(version)
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.arcee_client',
              new_callable=PropertyMock,
              return_value=ArceeMock(self.mongo_client)).start()
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.bulldozer_client',
              new_callable=PropertyMock).start()
        patch('rest_api.rest_api_server.controllers.base.'
              'BaseProfilingTokenController.get_secret').start()

    def _gen_executor(self, token, **kwargs):
        executor_id = kwargs.pop('_id', None)
        if not executor_id:
            executor_id = str(uuid.uuid4())
        executor = {
            '_id': str(uuid.uuid4()),
            'platform_type': 'aws',
            'instance_id': 'i-%s' % executor_id[:5],
            'account_id': executor_id[:5],
            'local_ip': '172.31.24.6',
            'public_ip': '3.123.31.120',
            'instance_lc': 'OnDemand',
            'instance_type': 't2.large',
            'instance_region': 'eu-central-1',
            'availability_zone': 'eu-central-1a',
            'token': token,
        }
        if kwargs:
            executor.update(kwargs)
        return executor

    def _gen_dataset(self, token, **kwargs):
        dataset = {
            '_id': str(uuid.uuid4()),
            'path': str(uuid.uuid4()),
            'name': f'Dataset {int(datetime.now(tz=timezone.utc).timestamp())}',
            'description': 'Discovered in training <task_key> - <run_name>(<run_id>)',
            'labels': ['test'],
            'created_at': int(datetime.now(tz=timezone.utc).timestamp()),
            'deleted_at': 0,
            'token': token,
            'training_set': {
                'path': str(uuid.uuid4()),
                'timespan_from': int(datetime.now(tz=timezone.utc).timestamp()),
                'timespan_to': int(datetime.now(tz=timezone.utc).timestamp())
            },
            'validation_set': {
                'path': str(uuid.uuid4()),
                'timespan_from': int(datetime.now(tz=timezone.utc).timestamp()),
                'timespan_to': int(datetime.now(tz=timezone.utc).timestamp())
            }
        }
        if kwargs:
            dataset.update(kwargs)
        return dataset

    def _gen_run(self, token, task_id, executor_ids, dataset_id, **kwargs):
        run = {
            '_id': str(uuid.uuid4()),
            'task_id': task_id,
            'start': 1665523835,
            'finish': 1665527774,
            'state': 2,
            'number': 1,
            'tags': {'key': 'value', 'project': 'regression'},
            'data': {'step': 2000, 'loss': 0.153899},
            'token': token,
        }
        if executor_ids:
            run['executors'] = executor_ids
        if dataset_id:
            run['dataset_id'] = dataset_id
        if kwargs:
            run.update(kwargs)
        return run

    def _create_task(self, organization_id, owner_id, **kwargs):
        task_obj = {
            'owner_id': owner_id,
            'name': 'task_key',
            'key': 'task_key',
            'metrics': []
        }
        if kwargs:
            task_obj.update(kwargs)
        code, task = self.client.task_create(organization_id, task_obj)
        self.assertEqual(code, 201)
        return task

    def _create_metric(self, organization_id, key, func='avg', **kwargs):
        metric_obj = {
            'target_value': 0.7,
            'tendency': 'more',
            'name': key,
            'key': key,
            'function': func
        }
        if kwargs:
            metric_obj.update(kwargs)
        code, metric = self.client.metric_create(organization_id, metric_obj)
        self.assertEqual(code, 201)
        return metric

    def _create_run(self, organization_id, task_id, executor_ids=None,
                    dataset_path=None, **kwargs):
        _, resp = self.client.profiling_token_get(organization_id)
        profiling_token = resp['token']
        if executor_ids:
            for executor_id in executor_ids:
                self.mongo_client.arcee.executors.insert_one(
                    self._gen_executor(profiling_token, instance_id=executor_id))
        dataset_id = None
        if dataset_path:
            res = self.mongo_client.arcee.datasets.insert_one(
                self._gen_dataset(profiling_token, path=dataset_path))
            dataset_id = res.inserted_id
        run = self._gen_run(
            profiling_token, task_id, executor_ids, dataset_id, **kwargs)
        self.mongo_client.arcee.runs.insert_one(run)
        return run

    def _create_log(self, run_id, time, data=None, **kwargs):
        r = {
            '_id': str(uuid.uuid4()),
            'run_id': run_id,
            'timestamp': time,
            'data': data
        }
        if kwargs:
            r.update(kwargs)
        self.mongo_client.arcee.logs.insert_one(r)
        return r

    def _create_console(self, run_id, output, error):
        console = {
            '_id': str(uuid.uuid4()),
            'run_id': run_id,
            'output': output,
            'error': error
        }
        self.mongo_client.arcee.consoles.insert_one(console)
        return console

    def _create_proc_stats(
            self, run_id, time, instance_id, cpu_percent, used_ram_mb,
            proc_cpu_percent=None, proc_ram_in_bytes=None, gpu_load=None,
            gpu_memory_free=None, gpu_memory_total=None, gpu_memory_used=None,
            **kwargs):
        proc_data = {
            '_id': str(uuid.uuid4()),
            'run_id': run_id,
            'timestamp': time,
            'instance_id': instance_id,
            'proc_stats': {
                'ps_stats': {
                    'cpu_percent': cpu_percent,
                    'used_ram_mb': used_ram_mb
                }
            }
        }
        gpu_stats = {}
        for k, v in {
            'avg_gpu_load': gpu_load,
            'avg_gpu_memory_free': gpu_memory_free,
            'avg_gpu_memory_total': gpu_memory_total,
            'avg_gpu_memory_used': gpu_memory_used
        }.items():
            if v is not None:
                gpu_stats[k] = v
        proc_data['proc_stats'].update({
            'gpu_stats': gpu_stats
        })
        proc = {}
        if proc_cpu_percent is not None:
            proc['cpu'] = proc_cpu_percent
        if proc_ram_in_bytes is not None:
            proc['mem'] = {'vms': {'t': proc_ram_in_bytes}}
        proc_data['proc_stats'].update({
            'proc': proc
        })
        if kwargs:
            proc_data.update(kwargs)
        self.mongo_client.arcee.proc_data.insert_one(proc_data)
        return proc_data

    def _create_milestone(self, run_id, time, milestone):
        r = {
            '_id': str(uuid.uuid4()),
            'run_id': run_id,
            'timestamp': time,
            'milestone': milestone
        }
        self.mongo_client.arcee.milestones.insert_one(r)
        return r


class ArceeMock:
    def __init__(self, mongo_cl, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiling_task = mongo_cl.arcee.task
        self.profiling_metrics = mongo_cl.arcee.metrics
        self.profiling_executors = mongo_cl.arcee.executors
        self.profiling_runs = mongo_cl.arcee.runs
        self.profiling_logs = mongo_cl.arcee.logs
        self.profiling_milestones = mongo_cl.arcee.milestones
        self.profiling_stages = mongo_cl.arcee.stages
        self.profiling_proc_data = mongo_cl.arcee.proc_data
        self.profiling_leaderboards = mongo_cl.arcee.leaderboards
        self.profiling_leaderboard_datasets = mongo_cl.arcee.leaderboard_datasets
        self.profiling_datasets = mongo_cl.arcee.datasets
        self.profiling_consoles = mongo_cl.arcee.consoles
        self.profiling_models = mongo_cl.arcee.models
        self.profiling_model_versions = mongo_cl.arcee.model_versions
        self._token = None

    @staticmethod
    def _raise_http_error(code):
        resp = Response()
        resp.status_code = code
        raise HTTPError(response=resp)

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    def _get_task_metrics(self, metrics):
        db_metrics = list(self.profiling_metrics.find(
            {'_id': {'$in': metrics}, 'token': self.token}))
        return db_metrics

    def _get_run_executors(self, executors):
        db_executors = list(self.profiling_executors.find(
            {'instance_id': {'$in': executors}, 'token': self.token}))
        return db_executors

    def _join_task_metrics(self, task):
        metrics = task.get('metrics')
        task_metrics = []
        if isinstance(metrics, list):
            task_metrics = self._get_task_metrics(metrics)
        task['taskMetrics'] = task_metrics

    def _join_run_executors(self, run):
        executors = run.get('executors')
        run_executors = []
        if isinstance(executors, list):
            run_executors = self._get_run_executors(executors)
        run['runExecutors'] = run_executors

    def task_create(self, task_key, owner_id, name=None,
                    metrics=None, description=None):
        b = {
            'key': task_key,
            'owner_id': owner_id,
            'name': name,
            'metrics': metrics,
            'token': self.token,
            '_id': str(uuid.uuid4()),
            'deleted_at': 0,
            'description': description
        }
        existing = list(self.profiling_task.find(
            {'token': self.token, 'key': task_key, 'deleted_at': 0}))
        if existing:
            self._raise_http_error(409)
        inserted = self.profiling_task.insert_one(b)
        result = list(self.profiling_task.find(
            {'_id': inserted.inserted_id}))[0]
        self._join_task_metrics(result)
        return 201, result

    def tasks_get(self):
        tasks = list(self.profiling_task.find(
            {'token': self.token, 'deleted_at': 0}))
        for a in tasks:
            self._join_task_metrics(a)
        return 200, tasks

    def tasks_bulk_get(self, task_ids, include_deleted=False):
        q = {
            'token': self.token,
            '_id': {'$in': task_ids},
            'deleted_at': 0
        }
        if include_deleted:
            q.pop('deleted_at')
        tasks = list(self.profiling_task.find(q))
        for a in tasks:
            self._join_task_metrics(a)
        return 200, tasks

    def task_get(self, id: str):
        tasks = list(self.profiling_task.find(
            {'token': self.token, '_id': id, 'deleted_at': 0}))
        if not tasks:
            self._raise_http_error(404)
        self._join_task_metrics(tasks[0])
        return 200, tasks[0]

    def task_update(self, task_id, owner_id=None, name=None,
                    metrics=None, **params):
        b = dict()
        if owner_id is not None:
            b.update({
                "owner_id": owner_id
            })
        if name is not None:
            b.update({
                "name": name
            })
        if metrics is not None:
            b.update({
                "metrics": metrics
            })
        b.update(params)
        if b:
            self.profiling_task.update_one(
                filter={
                    '_id': task_id,
                    'token': self.token,
                    'deleted_at': 0
                },
                update={'$set': b}
            )
        return 200, {'updated': bool(b)}

    def task_delete(self, id):
        res = self.profiling_task.update_one(
            {'token': self.token, '_id': id, 'deleted_at': 0},
            {'$set': {
                'deleted_at': int(datetime.now(tz=timezone.utc).timestamp())
            }}
        )
        if res.modified_count == 0:
            self._raise_http_error(404)
        return 204, None

    def metrics_get(self):
        return 200, list(self.profiling_metrics.find(
            {'token': self.token}))

    def metrics_create(self, key, target_value, tendency, name, func):
        existing = list(self.profiling_metrics.find(
            {'token': self.token, 'key': key}))
        if existing:
            self._raise_http_error(409)
        b = {
            "name": name,
            "target_value": target_value,
            "tendency": tendency,
            "key": key,
            "func": func,
            'token': self.token,
            '_id': str(uuid.uuid4())
        }
        inserted = self.profiling_metrics.insert_one(b)
        return 201, list(self.profiling_metrics.find(
            {'_id': inserted.inserted_id}))[0]

    def metrics_update(self, metric_id, target_value=None, tendency=None,
                       name=None, func=None):

        b = dict()
        if target_value is not None:
            b.update({
                "target_value": target_value,
            })
        if tendency is not None:
            b.update({
                "tendency": tendency
            })
        if name is not None:
            b.update({
                "name": name,
            })
        if func is not None:
            b.update({
                "func": func,
            })
        self.profiling_metrics.update_one(
            filter={
                '_id': metric_id,
                'token': self.token
            },
            update={'$set': b}
        )
        return 200, {'updated': True}

    def metric_get(self, metric_id):
        metrics = list(self.profiling_metrics.find(
            {'token': self.token, '_id': metric_id}))
        if not metrics:
            self._raise_http_error(404)
        return 200, metrics[0]

    def metric_delete(self, metric_id):
        res = self.profiling_metrics.delete_one(
            {'token': self.token, '_id': metric_id})
        if res.deleted_count == 0:
            self._raise_http_error(404)
        return 204, None

    def executors_breakdown_get(self):
        task_ids = self.profiling_task.distinct(
            "_id", {"token": self.token, "deleted_at": 0})
        if not task_ids:
            return 200, {}

        pipeline = [
            {"$match": {"task_id": {"$in": task_ids}}},
            {"$project": {
                "_id": 0,
                "timestamp": "$start",
                "executor": "$executors"
            }},
            {"$unwind": '$executor'}
        ]
        ts_executors = defaultdict(list)
        for data in self.profiling_runs.aggregate(pipeline):
            dt = datetime.fromtimestamp(data['timestamp']).replace(
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=timezone.utc)
            ts_executors[int(dt.timestamp())].append(data['executor'])

        breakdown = {}
        day_in_sec = 60 * 60 * 24
        if ts_executors:
            min_ts = min(ts_executors.keys())
            max_ts = max(ts_executors.keys())
            for ts in range(min_ts, max_ts + day_in_sec, day_in_sec):
                breakdown[ts] = len(set(ts_executors.get(ts, [])))
        return 200, breakdown

    def executors_get(self, tasks_ids=None, run_ids=None):
        if not tasks_ids and not run_ids:
            self._raise_http_error(400)
        match = {
            '$or': [],
            'token': self.token
        }
        if run_ids:
            match['$or'].append({'_id': {'$in': run_ids}})
        if tasks_ids:
            match['$or'].append(
                {'task_id': {'$in': tasks_ids}})
        runs = self.profiling_runs.find(match)
        task_runs_map = defaultdict(list)
        for r in runs:
            task_runs_map[r['task_id']].append(r)
        result = []
        for task_id, runs in task_runs_map.items():
            executors = set()
            for r in runs:
                executors.update(r.get('executors', []))
            res = list(self.profiling_executors.find({
                'instance_id': {'$in': list(executors)},
                'token': self.token
            }))
            result.extend(res)
        return 200, result

    def run_get(self, run_id):
        runs = list(self.profiling_runs.find({
            '_id': run_id,
        }))
        if not runs:
            self._raise_http_error(404)
        for r in runs:
            if r['token'] != self.token:
                self._raise_http_error(403)
        run = runs[0]
        self._join_run_executors(run)
        task = list(self.profiling_task.find({
            'token': self.token, '_id': run['task_id'], 'deleted_at': 0
        }))[0]
        run['task'] = task
        return 200, run

    def runs_bulk_get(self, runset_ids=None):
        runs_q = {'token': self.token}
        if runset_ids:
            runs_q['runset_id'] = {'$in': runset_ids}
        runs = list(self.profiling_runs.find(runs_q))
        return 200, runs

    def tasks_runs_get(self, task_id):
        _, task = self.task_get(task_id)
        runs = list(self.profiling_runs.find({
            'token': self.token,
            'task_id': task['_id']
        }))
        return 200, runs

    def run_milestones_get(self, run_id):
        milestones = list(self.profiling_milestones.find({
            'run_id': run_id
        }))
        return 200, milestones

    def run_logs_get(self, run_id):
        logs = list(self.profiling_logs.find({
            'run_id': run_id
        }))
        return 200, logs

    def run_delete(self, run_id):
        run = self.profiling_runs.find_one({"_id": run_id})
        if not run:
            self._raise_http_error(404)
        task = self.profiling_task.find_one({
            "_id": run["task_id"],
            "token": self.token,
            "deleted_at": 0
        })
        if not task:
            self._raise_http_error(403)
        self.profiling_runs.delete_one({'_id': run_id})
        return 204, None

    def token_create(self, token):
        return 200, {}

    def token_delete(self, token):
        return 200, {}

    def stages_get(self, run_id):
        stages = list(self.profiling_stages.find({
            'run_id': run_id
        }))
        return 200, stages

    def proc_data_get(self, run_id):
        proc_data = list(self.profiling_proc_data.find({
            'run_id': run_id
        }))
        return 200, proc_data

    def leaderboards_create(self, task_id, primary_metric, grouping_tags,
                            other_metrics=None,
                            filters=None, group_by_hp=True):
        existing = list(self.profiling_leaderboards.find(
            {'token': self.token, 'task_id': task_id,
             'deleted_at': 0}))
        if existing:
            self._raise_http_error(409)
        if other_metrics is None:
            other_metrics = []
        if filters is None:
            filters = []
        leaderboard = {
            "task_id": task_id,
            "primary_metric": primary_metric,
            "other_metrics": other_metrics,
            "filters": filters,
            "grouping_tags": grouping_tags,
            "group_by_hp": group_by_hp,
            "token": self.token,
            "_id": str(uuid.uuid4()),
            "deleted_at": 0,
            "created_at": int(datetime.now(tz=timezone.utc).timestamp())
        }
        inserted = self.profiling_leaderboards.insert_one(leaderboard)
        return 201, list(self.profiling_leaderboards.find(
            {'_id': inserted.inserted_id}))[0]

    def leaderboard_dataset_create(self, leaderboard_id, name, dataset_ids):
        leaderboard_dataset = {
            "leaderboard_id": leaderboard_id,
            "dataset_ids": dataset_ids,
            "name": name,
            "token": self.token,
            "_id": str(uuid.uuid4()),
            "deleted_at": 0,
            "created_at": int(datetime.now(tz=timezone.utc).timestamp())
        }
        inserted = self.profiling_leaderboard_datasets.insert_one(leaderboard_dataset)
        return 201, list(self.profiling_leaderboard_datasets.find(
            {'_id': inserted.inserted_id}))[0]

    def leaderboard_dataset_update(self, leaderboard_dataset_id, name, dataset_ids):
        leaderboard_dataset = self.profiling_leaderboard_datasets.find_one(
            {'token': self.token, '_id': leaderboard_dataset_id,
             'deleted_at': 0})
        if not leaderboard_dataset:
            self._raise_http_error(404)
        if name:
            leaderboard_dataset.update({
                'name': name
            })
        if dataset_ids:
            leaderboard_dataset.update({
                'dataset_ids': dataset_ids
            })
        self.profiling_leaderboard_datasets.update_one(
            filter={
                '_id': leaderboard_dataset['_id'],
                'token': self.token,
                'deleted_at': 0
            },
            update={'$set': leaderboard_dataset}
        )
        return 200, list(self.profiling_leaderboard_datasets.find(
            {'_id': leaderboard_dataset_id}))[0]

    def leaderboard_dataset_get(self, leaderboard_dataset_id):
        leaderboard_dataset = list(self.profiling_leaderboard_datasets.find(
            {'token': self.token, '_id': leaderboard_dataset_id,
             'deleted_at': 0}))
        if not leaderboard_dataset:
            self._raise_http_error(404)
        return 200, leaderboard_dataset[0]

    def leaderboard_dataset_delete(self, leaderboard_dataset_id):
        res = self.profiling_leaderboard_datasets.delete_one(
            {'token': self.token, '_id': leaderboard_dataset_id,
             'deleted_at': 0})
        if res.deleted_count == 0:
            self._raise_http_error(404)
        return 204, None

    @staticmethod
    def leaderboard_dataset_details(leaderboard_dataset_id):
        # this method contains complex logic, so not need emulate it here
        # just interface test
        return 200, []

    @staticmethod
    def leaderboard_generate(leaderboard_dataset_id):
        # this method contains complex logic, so not need emulate it here
        # just interface test
        return 200, []

    def runs_bulk_get_by_ids(self, task_id, run_ids):
        if not run_ids:
            self._raise_http_error(400)
        runs_q = {'task_id': task_id,
                  '_id': {'$in': run_ids}}
        runs = list(self.profiling_runs.find(runs_q))
        return 200, runs

    def leaderboard_update(self, task_id, primary_metric=None,
                           grouping_tags=None, other_metrics=None, filters=None,
                           group_by_hp=None):
        leaderboard = self.profiling_leaderboards.find_one(
            {'token': self.token, 'task_id': task_id,
             'deleted_at': 0})
        if not leaderboard:
            self._raise_http_error(404)
        for key, param in {
            'primary_metric': primary_metric,
            'grouping_tags': grouping_tags,
            'other_metrics': other_metrics,
            'filters': filters,
            'group_by_hp': group_by_hp
        }.items():
            if param is not None:
                leaderboard.update({
                    key: param
                })
        self.profiling_leaderboards.update_one(
            filter={
                '_id': leaderboard['_id'],
                'token': self.token,
                'deleted_at': 0
            },
            update={'$set': leaderboard}
        )
        return 200, {'updated': True}

    def leaderboard_datasets_get(self, leaderboard_id):
        match_filter = {
            "leaderboard_id": leaderboard_id,
            'token': self.token,
            'deleted_at': 0
        }
        datasets = list(self.profiling_leaderboard_datasets.find(match_filter))
        return 200, datasets

    def leaderboard_get(self, task_id):
        leaderboards = list(self.profiling_leaderboards.find(
            {'token': self.token, 'task_id': task_id,
             'deleted_at': 0}))
        if not leaderboards:
            return 200, {}
        return 200, leaderboards[0]

    def leaderboard_delete(self, task_id):
        res = self.profiling_leaderboards.delete_one(
            {'token': self.token, 'task_id': task_id,
             'deleted_at': 0})
        if res.deleted_count == 0:
            self._raise_http_error(404)
        return 204, None

    def leaderboard_details_get(self, task_id):
        # TODO: implement leaderboard details
        return 200, {}

    def dataset_create(
            self,
            path: str,
            labels: List[str] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            training_set: Optional[dict] = None,
            validation_set: Optional[dict] = None
    ):
        d = {
            "_id": str(uuid.uuid4()),
            "path": path,
            "name": name,
            "description": description,
            "labels": labels or list(),
            "token": self.token,
            "created_at": int(datetime.now(tz=timezone.utc).timestamp()),
            "deleted_at": 0,
            "training_set": training_set,
            "validation_set": validation_set,
        }
        inserted = self.profiling_datasets.insert_one(d)
        dataset = list(self.profiling_datasets.find(
            {'_id': inserted.inserted_id}))[0]
        return 201, dataset

    def dataset_list(self, include_deleted=False):
        match_filter = {
            'token': self.token,
            'deleted_at': 0
        }
        if include_deleted:
            match_filter.pop('deleted_at')
        datasets = list(self.profiling_datasets.find(match_filter))
        return 200, datasets

    def dataset_get(self, id_):
        datasets = list(self.profiling_datasets.find(
            {'token': self.token, '_id': id_}))
        if not datasets:
            self._raise_http_error(404)
        return 200, datasets[0]

    def dataset_update(self, id_: str, **params):
        if params:
            self.profiling_datasets.update_one(
                filter={
                    '_id': id_,
                    'token': self.token
                },
                update={'$set': params}
            )
        return 200, self.dataset_get(id_)[1]

    def dataset_delete(self, id_):
        res = self.profiling_datasets.update_one(
            filter={'token': self.token, '_id': id_},
            update={'$set': {
                'deleted_at': int(datetime.now(tz=timezone.utc).timestamp())}
            }
        )
        if res.modified_count == 0:
            self._raise_http_error(404)
        return 204, None

    def labels_list(self):
        pipeline = [
            {"$match": {"token": self.token, "deleted_at": 0}},
            {"$sort": {"created_at": -1}},
            {"$unwind": "$labels"},
            {"$group": {"_id": None, "labels": {"$push": "$labels"}}},
        ]
        labels = []
        cur = self.profiling_datasets.aggregate(pipeline)
        try:
            res = cur.next()
        except StopIteration:
            pass
        else:
            # keep insertion order
            labels.extend(OrderedDict.fromkeys(res.get('labels', [])).keys())
        return 200, labels

    def console_create(self, run_id: str, output: str, error: str):
        d = {
            "_id": str(uuid.uuid4()),
            "run_id": run_id,
            "output": output,
            "error": error,
        }
        inserted = self.profiling_consoles.insert_one(d)
        console = list(self.profiling_consoles.find(
            {'_id': inserted.inserted_id}))[0]
        return 201, console

    def console_get(self, run_id: str):
        consoles = list(self.profiling_consoles.find({'run_id': run_id}))
        if not consoles:
            self._raise_http_error(404)
        return 200, consoles[0]

    def model_create(self, key, name=None, tags=None, description=None):
        b = {
            'key': key,
            'name': name,
            'tags': tags,
            'token': self.token,
            '_id': str(uuid.uuid4()),
            'description': description,
            'created_at': int(datetime.now(tz=timezone.utc).timestamp())
        }
        existing = list(self.profiling_models.find(
            {'token': self.token, 'key': key}))
        if not existing:
            inserted = self.profiling_models.insert_one(b)
            id_ = inserted.inserted_id
        else:
            id_ = existing[0]['_id']
        result = self.profiling_models.find_one(
            {'_id': id_})
        return 201, result

    def models_get(self):
        models = list(self.profiling_models.find({'token': self.token}))
        for model in models:
            model['last_version'] = {}
            model['aliased_versions'] = []
            last_version = list(self.profiling_model_versions.find(
                {'model_id': model['_id'], 'deleted_at': 0}).sort(
                [('created_at', -1)]).limit(1))
            if last_version:
                model['last_version'] = last_version[0]
            aliased_versions = list(self.profiling_model_versions.find(
                {'model_id': model['_id'],
                 'deleted_at': 0,
                 'aliases': {'$ne': []}}).sort([('created_at', -1)]).limit(5))
            if aliased_versions:
                aliased_versions_list = []
                for version in aliased_versions:
                    for alias in version['aliases']:
                        if len(aliased_versions_list) < 5:
                            n_version = version.copy()
                            n_version['alias'] = alias
                            aliased_versions_list.append(n_version)
                model['aliased_versions'] = aliased_versions
        return 200, models

    def model_get(self, model_id: str):
        models = list(self.profiling_models.find(
            {'token': self.token, '_id': model_id}))
        if not models:
            self._raise_http_error(404)
        versions = list(self.profiling_model_versions.find(
            {'model_id': model_id}))
        model = models[0]
        model['versions'] = versions
        return 200, model

    def model_update(self, model_id, **params):
        model = list(self.profiling_models.find(
            {'token': self.token, '_id': model_id}))
        if not model:
            self._raise_http_error(404)
        if params:
            if 'key' in params:
                key = params['key']
                model = list(self.profiling_models.find(
                    {'token': self.token,
                     'key': key,
                     '_id': {'$ne': model_id}}))
                if model:
                    self._raise_http_error(409)
            self.profiling_models.update_one(
                filter={
                    '_id': model_id,
                    'token': self.token
                },
                update={'$set': params}
            )
        model = self.profiling_models.find_one(
            {'token': self.token, '_id': model_id})
        return 200, model

    def model_delete(self, model_id):
        model = list(self.profiling_models.find(
            {'token': self.token, '_id': model_id}))
        if not model:
            self._raise_http_error(404)
        self.profiling_models.delete_one(
            {'token': self.token, '_id': model_id})
        return 204, None

    def model_version_create(self, model_id, run_id, **params):
        b = {
            'model_id': model_id,
            'run_id': run_id,
            '_id': str(uuid.uuid4()),
            'deleted_at': 0,
            'created_at': int(datetime.now(tz=timezone.utc).timestamp())
        }
        b.update(params)
        version = self.profiling_model_versions.find_one(
            {'model_id': model_id, 'run_id': run_id})
        if version:
            self._raise_http_error(409)
        inserted = self.profiling_model_versions.insert_one(b)
        result = self.profiling_model_versions.find_one(
            {'_id': inserted.inserted_id})
        return 201, result

    def model_version_update(self, model_id, run_id, **params):
        version = self.profiling_model_versions.find_one(
            {'model_id': model_id, 'run_id': run_id})
        if not version:
            self._raise_http_error(404)
        self.profiling_model_versions.update_one(
            filter={
                '_id': version['_id']
            },
            update={'$set': params}
        )
        model = self.profiling_model_versions.find_one({'_id': version['_id']})
        return 200, model

    def model_version_delete(self, model_id, run_id):
        model_version = list(self.profiling_model_versions.find(
            {'model_id': model_id, 'run_id': run_id}))
        if not model_version:
            self._raise_http_error(404)
        self.profiling_model_versions.delete_one(
            {'token': self.token, '_id': model_version[0]['_id']})
        return 204, None

    def model_versions_by_task(self, task_id):
        runs = [x for x in self.profiling_runs.find(
                {'task_id': task_id},
                {'_id': 1, 'name': 1, 'number': 1})]
        runs_map = {x['_id']: x for x in runs}
        if not runs_map:
            return 200, []
        versions = list(self.profiling_model_versions.find(
            {'run_id': {'$in': list(runs_map.keys())}}))
        for version in versions:
            version['run'] = runs_map.get(version['run_id'], {})
            version.pop('run_id', None)
            version.pop('model_id', None)
        return 200, versions
