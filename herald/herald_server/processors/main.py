from datetime import datetime
import json
import logging
import os

from herald_server.controllers.notification import NotificationController
from herald_server.models.db_base import BaseDB
from herald_server.models.enums import ReactionTypes
from herald_server.processors.factory import ProcessorFactory

import boto3
from boto3.session import Config as BotoConfig


LOG = logging.getLogger(__name__)


TASK_RETRY_COUNT = 5


class MainProcessor:
    def __init__(self, task_producer, engine, config_cl):
        self.task_producer = task_producer
        self._session = BaseDB.session(engine)
        self._config = config_cl
        self._s3_client = None

    def session(self):
        return self._session()

    def close_session(self):
        self.session().close()

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self._config.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url='http://{}:{}'.format(
                    s3_params['host'], s3_params['port']),
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
        return self._s3_client

    @property
    def notification_controller(self):
        return NotificationController(self.session())

    def _matching_reactions(self, event):
        reactions = self.notification_controller.event_user_reactions(event)
        reaction_dict = {reaction_type: [] for reaction_type in ReactionTypes}

        for reaction in reactions:
            reaction_dict[reaction.type].append(reaction)

        return reaction_dict

    def process_event(self, event):
        LOG.info('processing new event %s', event)
        matching_reactions = self._matching_reactions(event)

        for reaction_type, reactions in matching_reactions.items():
            LOG.info('found %d matching reactions of type %s',
                     len(reactions), reaction_type)
            if not reactions:
                continue
            processor = ProcessorFactory.get(reaction_type)
            tasks = processor.create_tasks(event, reactions, self._config)
            for task in tasks:
                task['retries'] = TASK_RETRY_COUNT
                self.task_producer.publish_message(task)

    def perform_reaction(self, task):
        task_type = task.get('reaction_type')
        LOG.info("processing task type %s", task_type)
        task_type = ReactionTypes[task_type]
        processor = ProcessorFactory.get(task_type)
        processor.process_task(task, self._config)
        LOG.info("task %s processed successfully", task_type)

    def perform_email(self, email_task):
        LOG.info("processing new email task %s" % email_task)
        processor_email = ProcessorFactory.get(ReactionTypes.EMAIL)
        processor_email.process_email_task(email_task, self._config)
        template_type = email_task.get('template_type')
        LOG.info("task %s processed successfully", template_type)

    def load_task(self, task, cleanup_on_fail=True):
        bucket, filename = task['download_url'].split('/')
        report_path = 'task_%s' % int(datetime.utcnow().timestamp())
        LOG.info('loading %s from %s', bucket, filename)

        res = None
        try:
            with open(report_path, 'wb') as f_report:
                self.s3_client.download_fileobj(bucket, filename, f_report)
            with open(report_path, 'r') as f_in:
                res = json.load(f_in)
                return res
        finally:
            if os.path.exists(report_path):
                os.remove(report_path)
            if res or cleanup_on_fail:
                self.s3_client.delete_object(Bucket=bucket, Key=filename)

    def process_task(self, task, ack_callback):
        try:
            task = json.loads(task.decode("utf-8"))
            if 'reaction_type' in task:
                self.perform_reaction(task)
            elif 'template_type' in task:
                self.perform_email(task)
            elif 'download_url' in task:
                res = self.load_task(task, task.get('retries', 0) <= 0)
                self.perform_email(res)
            else:
                self.process_event(task)
        except Exception:
            LOG.exception("failed to process task %s", task)
            retries_left = task.get('retries', 1) - 1
            if retries_left > 0:
                LOG.info('%d retry attempts left', retries_left)
                task['retries'] = retries_left
                self.task_producer.publish_delayed_message(task)
            else:
                LOG.info('no retry attempts left, dropping task %s', task)
        finally:
            self.close_session()
        ack_callback()
