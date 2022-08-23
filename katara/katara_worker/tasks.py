import datetime
import json
import os

from kombu.log import get_logger

import boto3
from boto3.session import Config as BotoConfig

from katara_worker.consts import TaskState
from katara_worker.reports_generators.report import create_report

from auth_client.client_v2 import Client as AuthClient
from katara_client.client import Client as KataraClient
from rest_api_client.client_v2 import Client as RestClient


LOG = get_logger(__name__)


MAX_RETRIES = 10
MAX_UPDATE_THRESHOLD = 60 * 60
BUCKET_NAME = 'katara-reports'


class KataraTaskTimeoutError(Exception):
    pass


class Base(object):
    def __init__(self, body, message, config_cl,
                 on_continue_cb, on_complete_cb):
        self.message = message
        self.body = body
        self._rest_cl = None
        self._auth_cl = None
        self._katara_cl = None
        self._s3_client = None
        self.config_cl = config_cl
        self.on_continue_cb = on_continue_cb
        self.on_complete_cb = on_complete_cb

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    @property
    def auth_cl(self):
        if self._auth_cl is None:
            self._auth_cl = AuthClient(
                url=self.config_cl.auth_url(), verify=False)
            self._auth_cl.secret = self.config_cl.cluster_secret()
        return self._auth_cl

    @property
    def katara_cl(self):
        if self._katara_cl is None:
            self._katara_cl = KataraClient(
                url=self.config_cl.katara_url(), verify=False)
            self._katara_cl.secret = self.config_cl.cluster_secret()
        return self._katara_cl

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self.config_cl.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
            try:
                self._s3_client.create_bucket(Bucket=BUCKET_NAME)
            except self._s3_client.exceptions.BucketAlreadyOwnedByYou:
                pass
        return self._s3_client

    @classmethod
    def step(cls):
        return cls.__name__

    def execute(self):
        raise NotImplementedError()

    def _can_continue(self, ex):
        return not isinstance(
            ex, KataraTaskTimeoutError
        ) and self.body['tries_count'] < MAX_RETRIES

    @staticmethod
    def _load_result(result):
        if result is None:
            result = {}
        if isinstance(result, str):
            result = json.loads(result)
        return result

    def _handle_exception(self, ex):
        if self._can_continue(ex):
            self.body['tries_count'] += 1
            task_class = Continue
        else:
            task_class = SetFailed
        task_class(body=self.body, message=self.message,
                   config_cl=self.config_cl,
                   on_continue_cb=self.on_continue_cb,
                   on_complete_cb=self.on_complete_cb).execute()

    def run(self):
        LOG.info('Task %s, step %s', self.body['task_id'], self.step())
        try:
            self.execute()
        except Exception as main_ex:
            try:
                self._handle_exception(main_ex)
            except Exception as set_error_ex:
                LOG.error("Task %s, error %s", self.step(), set_error_ex)
                self.message.ack()
            finally:
                raise main_ex


class Cancel(Base):
    def execute(self):
        pass


class Continue(Base):
    def execute(self):
        self.on_continue_cb(self.body)
        self.message.ack()


class UpdateTimeout(Continue):
    def execute(self):
        self.body['last_update'] = int(
            datetime.datetime.utcnow().timestamp())
        super().execute()


class CheckTimeoutThreshold(UpdateTimeout):
    def execute(self):
        # MAX_UPDATE_THRESHOLD from last step execution exceeded
        if (int(datetime.datetime.utcnow().timestamp()) -
                self.body['last_update'] > MAX_UPDATE_THRESHOLD):
            raise KataraTaskTimeoutError()
        super().execute()


class SetCompleted(Base):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'],
            state=TaskState.COMPLETED)
        self.message.ack()


class SetStarted(CheckTimeoutThreshold):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'], state=TaskState.STARTED)
        super().execute()


class SetGettingScopes(CheckTimeoutThreshold):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'], state=TaskState.GETTING_SCOPES)
        super().execute()


class GetScopes(CheckTimeoutThreshold):
    def execute(self):
        _, task = self.katara_cl.task_get(
            self.body['task_id'], expanded=True)
        schedule = task.get('schedule') or {}
        recipient = schedule.get('recipient', {})
        if not recipient:
            # schedule was removed
            LOG.warning('Recipient not found, completing task %s',
                        self.body['task_id'])
            SetCompleted(body=self.body, message=self.message,
                         config_cl=self.config_cl,
                         on_continue_cb=self.on_continue_cb,
                         on_complete_cb=self.on_complete_cb).execute()
            return

        _, org = self.rest_cl.organization_get(recipient['scope_id'])
        _, org_pool = self.rest_cl.pool_get(org['pool_id'], children=True)
        scope_ids = [recipient['scope_id']]
        if org_pool['children']:
            for child in org_pool['children']:
                scope_ids.append(child['id'])

        result = {'scope_ids': scope_ids}
        self.katara_cl.task_update(
            self.body['task_id'], result=json.dumps(result),
            state=TaskState.GOT_SCOPES)
        super().execute()


class SetGettingRecipients(CheckTimeoutThreshold):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'], state=TaskState.GETTING_RECIPIENTS)
        super().execute()


class GetRecipients(CheckTimeoutThreshold):
    def execute(self):
        _, task = self.katara_cl.task_get(
            self.body['task_id'], expanded=True)
        schedule = task.get('schedule') or {}
        recipient = schedule.get('recipient', {})
        if not recipient:
            # schedule was removed
            LOG.warning('Recipient not found, completing task %s',
                        self.body['task_id'])
            SetCompleted(body=self.body, message=self.message,
                         config_cl=self.config_cl,
                         on_continue_cb=self.on_continue_cb,
                         on_complete_cb=self.on_complete_cb).execute()
            return
        user_ids = None
        if recipient.get('user_id'):
            user_ids = [recipient['user_id']]
        role_purposes = None
        if recipient.get('role_purpose'):
            role_purposes = [recipient['role_purpose']]
        result = self._load_result(task['result'])
        scope_ids = result['scope_ids']
        _, user_roles = self.auth_cl.user_roles_get(
            user_ids=user_ids, scope_ids=scope_ids,
            role_purposes=role_purposes)
        if not user_roles:
            # nobody to send
            LOG.warning('User roles not found, completing task %s',
                        self.body['task_id'])
            SetCompleted(body=self.body, message=self.message,
                         config_cl=self.config_cl,
                         on_continue_cb=self.on_continue_cb,
                         on_complete_cb=self.on_complete_cb).execute()
            return
        # user may have several assignments in org. Removing duplicates to
        # avoid extra reports
        ids = []
        for user_role in user_roles.copy():
            if user_role['user_id'] in ids:
                user_roles.remove(user_role)
                continue
            ids.append(user_role['user_id'])
        result.update({'user_roles': user_roles})
        self.katara_cl.task_update(
            self.body['task_id'], result=json.dumps(result),
            state=TaskState.GOT_RECIPIENTS)
        super().execute()


class SetGeneratingReportData(SetCompleted):
    def execute(self):
        _, task = self.katara_cl.task_get(self.body['task_id'])
        result = self._load_result(task['result'])
        user_roles = result.pop('user_roles')
        new_tasks = []
        for user_role in user_roles:
            result['user_role'] = user_role
            new_tasks.append({
                'schedule_id': task['schedule_id'],
                'state': TaskState.GENERATING_DATA,
                'result': json.dumps(result),
                'parent_id': task['id']})
        self.katara_cl.tasks_create(tasks=new_tasks)
        super().execute()


class GenerateReportData(CheckTimeoutThreshold):
    def execute(self):
        _, task = self.katara_cl.task_get(
            self.body['task_id'], expanded=True)
        schedule = task.get('schedule') or {}
        report_details = schedule.get('report', {})
        recipient_details = schedule.get('recipient', {})
        result = self._load_result(task['result'])
        user_role = result['user_role']
        report_data = create_report(
            report_details.get('module_name'),
            recipient_details.get('scope_id'),
            user_role,
            self.config_cl)
        if not report_data:
            # nothing to process
            LOG.info('No report data generated, completing task %s',
                     self.body['task_id'])
            SetCompleted(body=self.body, message=self.message,
                         config_cl=self.config_cl,
                         on_continue_cb=self.on_continue_cb,
                         on_complete_cb=self.on_complete_cb).execute()
            return
        report_name = 'task_%s_%s' % (
            self.body['task_id'],
            int(datetime.datetime.utcnow().timestamp()))
        with open(report_name, 'w') as outfile:
            json.dump(report_data, outfile)
        try:
            with open(report_name, 'rb') as f_report:
                self.s3_client.upload_fileobj(
                    f_report, BUCKET_NAME, report_name)
        finally:
            os.remove(report_name)
        result['download_url'] = os.path.join(BUCKET_NAME, report_name)
        self.katara_cl.task_update(
            self.body['task_id'], result=json.dumps(result),
            state=TaskState.GENERATED_DATA)
        super().execute()


class SetPuttingToHerald(CheckTimeoutThreshold):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'], state=TaskState.PUTTING_TO_HERALD)
        super().execute()


class PutToHerald(SetCompleted):
    def execute(self):
        _, task = self.katara_cl.task_get(
            self.body['task_id'], expanded=False)
        try:
            result = self._load_result(task['result'])
            herald_task = {
                'download_url': result['download_url'],
                'task_id': self.body['task_id'],
                'retries': MAX_RETRIES
            }
            self.on_complete_cb(herald_task)
        except KeyError as ex:
            # most likely schedule was deleted
            LOG.error("Task %s, error %s", self.body['task_id'], ex)
        finally:
            super().execute()


class SetFailed(Base):
    def execute(self):
        self.katara_cl.task_update(
            self.body['task_id'], state=TaskState.ERROR)
        self.message.ack()
