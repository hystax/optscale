from arcee_client.client import Client as ArceeClient
from rest_api_server.controllers.base import BaseController
from rest_api_server.models.models import ProfilingToken
from sqlalchemy.exc import IntegrityError
from rest_api_server.utils import Config


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


class Application(ArceeObject):
    REPLACE_KEYS = {
        **ArceeObject.REPLACE_KEYS,
        'applicationGoals': 'goals'
    }
    INNER_OBJECTS = {'goals': ArceeObject}


class Run(ArceeObject):
    REPLACE_KEYS = {
        **ArceeObject.REPLACE_KEYS,
        'runExecutors': 'executors'
    }
    INNER_OBJECTS = {
        'application': Application,
        'executors': ArceeObject
    }

    @classmethod
    def format(cls, obj):
        super().format(obj)
        if not obj.get('executors'):
            obj['executors'] = []


class BaseProfilingController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._arcee_client = None

    @property
    def arcee_client(self):
        if not self._arcee_client:
            self._arcee_client = ArceeClient(url=Config().arcee_url)
            self._arcee_client.secret = self.get_secret()
        return self._arcee_client

    def get_arcee_client(self, token=None):
        self.arcee_client.token = token
        return self.arcee_client

    @ staticmethod
    def get_secret():
        return Config().cluster_secret

    def _get_profiling_token(self, organization_id):
        return self.session.query(ProfilingToken).filter(
            ProfilingToken.deleted.is_(False),
            ProfilingToken.organization_id == organization_id
        ).one_or_none()

    def get_or_create_profiling_token(self, organization_id):
        item = self._get_profiling_token(organization_id)
        if not item:
            try:
                item = ProfilingToken(organization_id=organization_id)
                self.session.add(item)
                self.session.commit()
            except IntegrityError:
                self.session.rollback()
                item = self._get_profiling_token(organization_id)
            try:
                self.create_token(item.token)
            except Exception:
                self.session.delete(item)
                self.session.commit()
                raise
        return item

    def get_profiling_token(self, organization_id):
        profiling_token = self.get_or_create_profiling_token(organization_id)
        return profiling_token.token

    def create_application(self, profiling_token, application_key, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, app = arcee.application_create(
            application_key=application_key, **kwargs)
        Application.format(app)
        return app

    def get_application(self, profiling_token, application_id):
        arcee = self.get_arcee_client(profiling_token)
        _, application = arcee.application_get(application_id)
        Application.format(application)
        return application

    def list_applications(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.applications_get()
        for r in response:
            Application.format(r)
        return response

    def update_application(self, profiling_token, application_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated_app = arcee.application_update(application_id, **kwargs)
        return updated_app

    def delete_application(self, profiling_token, application_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.application_delete(application_id)

    def list_runs(self, profiling_token, application_id):
        arcee = self.get_arcee_client(profiling_token)
        _, runs = arcee.applications_runs_get(application_id)
        for r in runs:
            Run.format(r)
        return runs

    def get_executors(self, profiling_token, application_ids, run_ids=None):
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.executors_get(application_ids, run_ids)
        for r in response:
            ArceeObject.format(r)
        return response

    def list_logs(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, logs = arcee.run_logs_get(run_id)
        for l in logs:
            ArceeObject.format(l)
        return logs

    def list_proc_data(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, proc_data = arcee.proc_data_get(run_id)
        for d in proc_data:
            ArceeObject.format(d)
        return proc_data

    def get_goal(self, profiling_token, goal_id):
        arcee = self.get_arcee_client(profiling_token)
        _, goal = arcee.goal_get(goal_id)
        ArceeObject.format(goal)
        return goal

    def list_goals(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        _, response = arcee.goals_get()
        for r in response:
            ArceeObject.format(r)
        return response

    def create_goal(self, profiling_token, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, goal = arcee.goals_create(**kwargs)
        ArceeObject.format(goal)
        return goal

    def update_goal(self, profiling_token, goal_id, **kwargs):
        arcee = self.get_arcee_client(profiling_token)
        _, updated = arcee.goals_update(goal_id, **kwargs)
        return updated

    def delete_goal(self, profiling_token, goal_id):
        arcee = self.get_arcee_client(profiling_token)
        arcee.goal_delete(goal_id)

    def create_token(self, profiling_token):
        arcee = self.get_arcee_client()
        arcee.token_create(profiling_token)

    def delete_token(self, profiling_token):
        arcee = self.get_arcee_client(profiling_token)
        arcee.token_delete(profiling_token)

    def get_run(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, run = arcee.run_get(run_id)
        Run.format(run)
        return run

    def list_milestones(self, profiling_token, run_id):
        arcee = self.get_arcee_client(profiling_token)
        _, milestones = arcee.run_milestones_get(run_id)
        for m in milestones:
            ArceeObject.format(m)
        return milestones

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
