import datetime
import json
import os
import uuid

import boto3
from boto3.session import Config as BotoConfig

from kombu.log import get_logger

from pymongo import MongoClient, UpdateOne

from bumiworker.bumiworker.consts import TaskState
from bumiworker.bumiworker.modules.module import call_module, list_modules

from optscale_client.herald_client.client_v2 import Client as HeraldClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient


LOG = get_logger(__name__)
BUCKET_NAME = 'bumi-data'
SERVICE_FOLDER = 'service'
ARCHIVE_FOLDER = 'archive'
RECOMMENDATION_FOLDER = 'recommendations'


def task_str(task):
    return '%s (organization_id %s, module %s(%s), try %s)' % (
        task.get('created_at'), task.get('organization_id'),
        task.get('module'), task.get('module_type'), task.get('tries_count'))


class BumiTaskTimeoutError(Exception):
    pass


class BumiTaskWaitError(Exception):
    pass


class Base(object):
    def __init__(self, body, message, config_cl,
                 on_continue_cb, create_children_cb):
        self.message = message
        self.body = body
        self._rest_cl = None
        self._s3_client = None
        self._mongo_cl = None
        self.config_cl = config_cl
        self.on_continue_cb = on_continue_cb
        self.create_children_cb = create_children_cb

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

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

    @property
    def mongo_cl(self):
        if not self._mongo_cl:
            mongo_params = self.config_cl.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_cl = MongoClient(mongo_conn_string)
        return self._mongo_cl

    def _execute(self):
        raise NotImplementedError()

    def can_continue(self, ex):
        return not isinstance(
            ex, BumiTaskTimeoutError
        ) and not isinstance(
            ex, BumiTaskWaitError
        ) and self.body['tries_count'] < self.body['max_retries']

    @property
    def is_delayed(self):
        return False

    @property
    def step(self):
        return self.__class__.__name__

    def _handle_exception(self, exc):
        if self.can_continue(exc):
            self.body['tries_count'] += 1
        else:
            self.body['reason'] = '%s - %s' % (type(exc), str(exc) or None)
            self.body['state'] = TaskState.ERROR
        self.on_continue_cb(self.body, self.is_delayed)

    def check_timeout(self):
        pass

    def execute(self):
        LOG.info('Task %s, step %s', task_str(self.body), self.step)
        try:
            self.check_timeout()
            self._execute()
        except Exception as main_ex:
            try:
                self._handle_exception(main_ex)
            except Exception as set_error_ex:
                LOG.error(
                    'Task %s, step %s - %s', task_str(self.body), self.step,
                    str(set_error_ex))
            finally:
                self.message.ack()
                raise main_ex


class Cancel(Base):
    def _execute(self):
        pass


class Continue(Base):
    def _execute(self):
        self.on_continue_cb(self.body, self.is_delayed)
        self.message.ack()


class UpdateTimeout(Continue):
    def _execute(self):
        self.body['last_update'] = int(
            datetime.datetime.utcnow().timestamp())
        super()._execute()


class CheckTimeoutThreshold(UpdateTimeout):
    def check_timeout(self):
        # MAX_UPDATE_THRESHOLD from last step execution exceeded
        if (int(datetime.datetime.utcnow().timestamp()) -
                self.body['last_update'] > self.body['task_timeout']):
            raise BumiTaskTimeoutError(
                'Timeout error while process task %s, step %s' % (
                    task_str(self.body), self.step))


class CheckWaitThreshold(Continue):
    def _handle_exception(self, exc):
        # further waiters should be able to count from scratch
        self.body['last_update'] = int(
            datetime.datetime.utcnow().timestamp())
        super()._handle_exception(exc)

    def check_timeout(self):
        # MAX_WAIT_THRESHOLD from previous step execution exceeded
        if (int(datetime.datetime.utcnow().timestamp()) -
                self.body['last_update'] > self.body['wait_timeout']):
            raise BumiTaskWaitError(
                'Wait error while process task %s, step %s' % (
                    task_str(self.body), self.step))


class CompleteBase(Base):
    @property
    def is_delayed(self):
        return True

    def _handle_exception(self, exc):
        # put msg to queue and hope that it'll gracefully finish
        if (int(datetime.datetime.utcnow().timestamp()) -
                self.body['last_update'] <= self.body['wait_timeout']):
            self.on_continue_cb(self.body, self.is_delayed)
        else:
            LOG.error('Aborting task %s, step %s since graceful fail seems impossible',
                      task_str(self.body), self.step)

    def _execute(self):
        self.message.ack()

    def get_failed_modules(self):
        failed_modules = []
        for module_folder in [RECOMMENDATION_FOLDER, SERVICE_FOLDER,
                              ARCHIVE_FOLDER]:
            prefix = '%s/' % os.path.join(
                self.body['organization_id'], str(self.body['created_at']),
                module_folder)
            s3_objects = self.s3_client.list_objects_v2(
                Bucket=BUCKET_NAME, Prefix=prefix)
            modules_result = []
            for s3_object in s3_objects.get('Contents', []):
                temp_file_path = str(uuid.uuid4())
                try:
                    with open(temp_file_path, 'wb') as f_res:
                        self.s3_client.download_fileobj(
                            BUCKET_NAME, s3_object['Key'], f_res)
                    with open(temp_file_path, 'r') as f_in:
                        res = json.load(f_in)
                        if res:
                            modules_result.append(res)
                finally:
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            for module in modules_result:
                error = module.get('error') or module.get('timeout_error')
                if error:
                    failed_modules.append({
                        'module': module['module'],
                        'error': error})
        return failed_modules


class SetSucceeded(CompleteBase):
    def _execute(self):
        LOG.info(
            'Task %s succeeded', task_str(self.body))
        super()._execute()


class SetSucceededNotifiable(SetSucceeded):
    def send_modules_fail_service_email(self, organization_id, failed_modules):
        _, org = self.rest_cl.organization_get(organization_id)
        recipient = self.config_cl.optscale_error_email_recipient()
        if not recipient:
            return
        subject = '[%s] Recommendation module failed' % self.config_cl.public_ip()
        template_params = {
            'texts': {
                'organization': {'id': organization_id,
                                 'name': org['name']},
                'failed_modules': failed_modules
            }}
        HeraldClient(url=self.config_cl.herald_url(),
                     secret=self.config_cl.cluster_secret()).email_send(
            [recipient], subject, template_params=template_params,
            template_type="bumi_module_execution_failed")

    def _execute(self):
        self.get_failed_modules()
        # TODO: OS-6259: temporary mute service email
        # failed_modules = self.get_failed_modules()
        # if failed_modules:
        #     self.send_modules_fail_service_email(self.body['organization_id'],
        #                                          failed_modules)
        super()._execute()


class SetStarted(CheckTimeoutThreshold):
    def _execute(self):
        LOG.info(
            'Task %s started', task_str(self.body))
        self.body['state'] = TaskState.STARTED
        super()._execute()


class InitializeChildrenBase(CheckTimeoutThreshold):
    @property
    def module_type(self):
        raise NotImplementedError

    def update_task_state(self):
        raise NotImplementedError

    def _get_child_task(self, module):
        return {
                'last_update': int(
                    datetime.datetime.utcnow().timestamp()),
                'tries_count': 0,
                'created_at': self.body['created_at'],
                'checklist_id': self.body['checklist_id'],
                'organization_id': self.body['organization_id'],
                'state': TaskState.CREATED,
                'module': module,
                'module_type': self.module_type,
                'task_timeout': self.body['task_timeout'],
                'max_retries': self.body['max_retries'],
            }

    def create_children_tasks(self, modules):
        children_params = []
        for module in modules:
            children_params.append(self._get_child_task(module))
        if children_params:
            self.create_children_cb(children_params)


class InitializeChecklist(InitializeChildrenBase):
    @property
    def module_type(self):
        return RECOMMENDATION_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.INITIALIZED_CHECKLIST

    def _execute(self):
        modules = list_modules(self.module_type)
        if not modules:
            LOG.warning('No %s modules found', self.module_type)
            # Nothing to do, update checklist & complete
            self.body['state'] = TaskState.WAITED_SERVICE
        else:
            self.create_children_tasks(modules)
            self.body['children_count'] = len(modules)
            self.update_task_state()
        super()._execute()


class WaitTasksResult(CheckWaitThreshold):
    @property
    def is_delayed(self):
        return True

    @property
    def folder(self):
        raise NotImplementedError

    def update_task_state(self):
        raise NotImplementedError

    def _execute(self):
        prefix = '%s/' % os.path.join(
            self.body['organization_id'], str(self.body['created_at']),
            self.folder)
        s3_objects = self.s3_client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=prefix)
        if s3_objects['KeyCount'] == self.body['children_count']:
            self.body['last_update'] = int(
                datetime.datetime.utcnow().timestamp())
            self.update_task_state()
        super()._execute()


class WaitChecklist(WaitTasksResult):
    @property
    def folder(self):
        return RECOMMENDATION_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.WAITED_CHECKLIST


class WaitService(WaitTasksResult):
    @property
    def folder(self):
        return SERVICE_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.WAITED_SERVICE


class WaitArchive(WaitTasksResult):
    @property
    def folder(self):
        return ARCHIVE_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.WAITED_ARCHIVE


class CollectCheckResult(CheckTimeoutThreshold):
    def save_result(self, modules_result):
        update_fields = ['data']
        filter_filed = ['module', 'created_at', 'organization_id']
        self.mongo_cl.restapi['checklists'].bulk_write([
            UpdateOne(
                filter={k: res[k] for k in filter_filed},
                update={
                    '$set': {k: res[k] for k in update_fields},
                    '$setOnInsert': {k: v for k, v in res.items()
                                     if k not in update_fields},
                },
                upsert=True,
            ) for res in modules_result
        ])

    def _execute(self):
        prefix = '%s/' % os.path.join(
            self.body['organization_id'], str(self.body['created_at']),
            RECOMMENDATION_FOLDER)
        s3_objects = self.s3_client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=prefix)
        modules_result = []
        need_raise = False
        for s3_object in s3_objects.get('Contents', []):
            temp_file_path = str(uuid.uuid4())
            try:
                with open(temp_file_path, 'wb') as f_res:
                    self.s3_client.download_fileobj(
                        BUCKET_NAME, s3_object['Key'], f_res)
                with open(temp_file_path, 'r') as f_in:
                    res = json.load(f_in)
                    if res.get('timeout_error'):
                        need_raise = True
                    else:
                        modules_result.append(res)
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        if need_raise:
            self.body['state'] = TaskState.ERROR
        else:
            if modules_result:
                self.save_result(modules_result)
            self.body['state'] = TaskState.COLLECTED_CHECK_RESULT
        super()._execute()


class CheckArchiveResult(CheckTimeoutThreshold):
    def _execute(self):
        self.body['state'] = TaskState.CHECKED_ARCHIVE_RESULT
        prefix = '%s/' % os.path.join(
            self.body['organization_id'], str(self.body['created_at']),
            ARCHIVE_FOLDER)
        s3_objects = self.s3_client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=prefix)
        for s3_object in s3_objects.get('Contents', []):
            temp_file_path = str(uuid.uuid4())
            try:
                with open(temp_file_path, 'wb') as f_res:
                    self.s3_client.download_fileobj(
                        BUCKET_NAME, s3_object['Key'], f_res)
                with open(temp_file_path, 'r') as f_in:
                    res = json.load(f_in)
                    if res.get('timeout_error') or res.get('error'):
                        self.body['state'] = TaskState.ERROR
                        break
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        super()._execute()


class InitializeService(InitializeChildrenBase):
    @property
    def module_type(self):
        return SERVICE_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.INITIALIZED_SERVICE

    def _execute(self):
        modules = list_modules(self.module_type)
        self.create_children_tasks(modules)
        self.body['children_count'] = len(modules)
        self.update_task_state()
        super()._execute()


class InitializeArchive(InitializeService):
    @property
    def module_type(self):
        return ARCHIVE_FOLDER

    def update_task_state(self):
        self.body['state'] = TaskState.INITIALIZED_ARCHIVE


class UpdateChecklist(Continue):
    def _execute(self):
        self.rest_cl.checklist_update(
            self.body['checklist_id'],
            {'last_completed': self.body['created_at']})
        self.body['state'] = TaskState.UPDATED_CHECKLIST
        super()._execute()


class HandleTaskTimeout(CheckTimeoutThreshold):
    def save_result_to_file(self, module_data):
        result = {
            'organization_id': self.body['organization_id'],
            'created_at': self.body['created_at'],
            'module': self.body['module'],
            **module_data
        }
        temp_file_path = str(uuid.uuid4())
        module_obj_path = os.path.join(
            self.body['organization_id'], str(self.body['created_at']),
            self.body['module_type'], '%s.json' % self.body['module'])
        with open(temp_file_path, 'w') as outfile:
            json.dump(result, outfile)
        try:
            with open(temp_file_path, 'rb') as f_res:
                self.s3_client.upload_fileobj(
                    f_res, BUCKET_NAME, module_obj_path)
        finally:
            os.remove(temp_file_path)

    def check_timeout(self):
        try:
            super().check_timeout()
        except BumiTaskTimeoutError as exc:
            self.save_result_to_file({'timeout_error': str(exc)})
            raise


class Process(HandleTaskTimeout):
    def _execute(self):
        try:
            data, options, error = call_module(
                self.body['module'], self.body['module_type'],
                self.body['organization_id'], self.config_cl,
                created_at=self.body['created_at'])
        except Exception as ex:
            LOG.exception('Error while processing %s (%s) for organization %s - %s',
                          self.body['module'], self.body['module_type'],
                          self.body['organization_id'],
                          str(ex))
            data, options = None, None
            error = str(ex)
        module_data = {
            'data': data,
            'options': options,
            'error': error
        }
        self.save_result_to_file(module_data)
        self.body['state'] = TaskState.PROCESSED
        super()._execute()


class Cleanup(SetSucceeded):
    def _execute(self):
        prefix = '%s/' % self.body['organization_id']
        s3_objects = self.s3_client.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=prefix)
        delete_objects = []
        for obj in s3_objects.get('Contents', []):
            if str(self.body['created_at']) not in obj['Key']:
                delete_objects.append({'Key': obj['Key']})
        if delete_objects:
            self.s3_client.delete_objects(
                Bucket=BUCKET_NAME,
                Delete={'Objects': delete_objects})
        super()._execute()


class SetFailed(CompleteBase):
    def _execute(self):
        LOG.error('Task %s failed', task_str(self.body))

        # child task must not fail checklist
        if not self.body.get('module'):
            self.rest_cl.checklist_update(
                self.body['checklist_id'],
                {'last_completed': self.body['created_at']})
        super()._execute()


class SetFailedNotifiable(SetFailed):
    def send_failure_service_email(self, organization_id, reason,
                                   failed_modules):
        recipient = self.config_cl.optscale_error_email_recipient()
        if not recipient:
            return
        subject = '[%s] Bumi task execution failed' % self.config_cl.public_ip()
        template_params = {
            'texts': {
                'organization': {'id': organization_id},
                'reason': reason,
                'failed_modules': failed_modules
            }}
        HeraldClient(url=self.config_cl.herald_url(),
                     secret=self.config_cl.cluster_secret()).email_send(
            [recipient], subject, template_params=template_params,
            template_type="bumi_task_execution_failed")

    def _execute(self):
        msg = 'Task %s failed. ' % task_str(self.body)
        failed_modules = self.get_failed_modules()
        if failed_modules:
            msg += 'Failed modules: %s' % self.get_failed_modules()
        LOG.error(msg)
        # TODO: OS-6259: temporary mute service email
        # self.send_failure_service_email(
        #     self.body['organization_id'], self.body.get('reason'),
        #     failed_modules)
        super()._execute()
