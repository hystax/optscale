import json
import os
import logging
from bson.objectid import ObjectId
from optscale_client.config_client.client import Client as ConfigClient
from datetime import datetime
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ARCHIVE_ENABLED = False
ARCHIVE_PATH = '/src/archive'
FILE_MAX_ROWS = 10000
CHUNK_SIZE = 500
ROWS_LIMIT = 10000

LOG = logging.getLogger(__name__)


class CleanMongoDB(object):
    def __init__(self):
        super().__init__()
        self._config_client = None
        self._mongo_client = None
        self._archive_enable = ARCHIVE_ENABLED
        self._file_max_rows = FILE_MAX_ROWS
        self._chunk_size = CHUNK_SIZE
        self._limits = {
            # linked to cloud_account_id
            self.mongo_client.restapi.raw_expenses: ROWS_LIMIT,
            self.mongo_client.restapi.resources: ROWS_LIMIT,
            # linked to run_id
            self.mongo_client.arcee.console: ROWS_LIMIT,
            self.mongo_client.arcee.log: ROWS_LIMIT,
            self.mongo_client.arcee.milestone: ROWS_LIMIT,
            self.mongo_client.arcee.proc_data: ROWS_LIMIT,
            self.mongo_client.arcee.stage: ROWS_LIMIT,
            self.mongo_client.arcee.model_version: ROWS_LIMIT,
            # linked to task_id
            self.mongo_client.arcee.run: ROWS_LIMIT,
            # linked to profiling_token.token
            self.mongo_client.arcee.task: ROWS_LIMIT,
            self.mongo_client.arcee.dataset: ROWS_LIMIT,
            self.mongo_client.arcee.goal: ROWS_LIMIT,
            self.mongo_client.arcee.leaderboard: ROWS_LIMIT,
            self.mongo_client.arcee.leaderboard_dataset: ROWS_LIMIT,
            self.mongo_client.arcee.model: ROWS_LIMIT,
            # linked to profiling_token.infrastructure_token
            self.mongo_client.bulldozer.template: ROWS_LIMIT,
            self.mongo_client.bulldozer.runset: ROWS_LIMIT,
            self.mongo_client.bulldozer.runner: ROWS_LIMIT,
        }

    @property
    def config_client(self):
        if not self._config_client:
            etcd_host = os.environ.get('HX_ETCD_HOST')
            etcd_port = int(os.environ.get('HX_ETCD_PORT'))
            self._config_client = ConfigClient(host=etcd_host, port=etcd_port)
        return self._config_client

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self.config_client.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    def get_settings(self):
        try:
            result = self.config_client.read_branch('/cleanmongodb')
        except Exception as exc:
            LOG.error(f'Error getting settings for cleaner: {exc}, '
                      f'will use default values')
            result = {}
        return result

    def get_session(self):
        engine = create_engine(
            'mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4' %
            self.config_client.rest_db_params(),
            pool_size=200,
            max_overflow=25,
            pool_pre_ping=True,
        )
        return Session(bind=engine)

    @property
    def limits(self):
        return self._limits

    @limits.setter
    def limits(self, value):
        self._limits = value

    @property
    def chunk_size(self):
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value):
        self._chunk_size = value

    @property
    def archive_enable(self):
        return self._archive_enable

    @archive_enable.setter
    def archive_enable(self, value):
        self._archive_enable = value

    @property
    def file_max_rows(self):
        return self._file_max_rows

    @file_max_rows.setter
    def file_max_rows(self, value):
        self._file_max_rows = value

    def get_deleted_organization_info(self):
        result = None
        session = self.get_session()
        stmt = """
            SELECT organization.id, p_token.token, p_token.infrastructure_token
            FROM organization
            LEFT JOIN profiling_token as p_token
            ON organization.id = p_token.organization_id
            WHERE organization.deleted_at != 0 AND
                organization.cleaned_at = 0
            LIMIT 1
        """
        try:
            result = next(session.execute(stmt))
        except StopIteration:
            pass
        finally:
            session.close()
        return result

    def delete_in_chunks(self, collection, filter_name, filter_value,
                         archive=False, archive_cloud_account_id=None):
        rows_limit = self.limits.get(collection, 0)
        if not rows_limit:
            return 0
        if isinstance(filter_value, list):
            filter_value = {'$in': filter_value}
        row_ids = list(collection.find({filter_name: filter_value}, ['_id']
                                       ).limit(rows_limit))
        for j in range(0, len(row_ids), self.chunk_size):
            chunk = [row['_id'] for row in row_ids[j: j + self.chunk_size]]
            if archive:
                LOG.info('Archiving raw expenses')
                last_file_name = self.get_archive_file(
                    archive_cloud_account_id)
                file_length = self.get_file_length(last_file_name)
                split_data = self.split_chunk_by_files(
                    chunk, self.file_max_rows - file_length, last_file_name,
                    archive_cloud_account_id, self.file_max_rows)
                for file, raw_expenses in split_data.items():
                    path = os.path.join(ARCHIVE_PATH, file)
                    exp_count = len(raw_expenses)
                    full_expenses_rows = collection.find(
                        {'_id': {'$in': raw_expenses}})
                    with open(path, 'a+') as f:
                        if raw_expenses:
                            LOG.info(
                                f'Saving {exp_count} expenses to file {path}')
                            for row in full_expenses_rows:
                                f.write(self._row_to_json(row) + '\n')
            collection.delete_many({'_id': {'$in': chunk}})
        remainder_rows = rows_limit - len(row_ids)
        return remainder_rows

    def _delete_runs(self, runs_ids_chunk):
        run_collections = [self.mongo_client.arcee.console,
                           self.mongo_client.arcee.log,
                           self.mongo_client.arcee.milestone,
                           self.mongo_client.arcee.stage,
                           self.mongo_client.arcee.proc_data,
                           self.mongo_client.arcee.model_version]
        if all(self.limits.get(x) == 0 for x in run_collections):
            # maximum number of entities related to runs have already
            # been deleted
            return False
        for collection in run_collections:
            filter_name = 'run_id'
            if collection == self.mongo_client.arcee.log:
                filter_name = 'run'
            self.limits[collection] = self.delete_in_chunks(
                collection, filter_name, runs_ids_chunk)
        if all(self.limits.get(x) != 0 for x in run_collections):
            # all entities related to runs chunk are cleaned up, runs
            # can be deleted
            self.limits[
                self.mongo_client.arcee.run] = self.delete_in_chunks(
                self.mongo_client.arcee.run, '_id', runs_ids_chunk)
            return True
        return False

    def _delete_by_task(self, token):
        all_tasks_deleted = False
        rows_limit = self.limits.get(self.mongo_client.arcee.task)
        tasks = list(self.mongo_client.arcee.task.find(
            {'token': token}, ['_id']).limit(rows_limit))
        are_runs_deleted = []
        for i in range(0, len(tasks), CHUNK_SIZE):
            tasks_chunk = [
                row['_id'] for row in tasks[i:i + CHUNK_SIZE]]
            runs_limit = self.limits.get(self.mongo_client.arcee.run)
            runs = list(self.mongo_client.arcee.run.find(
                {'task_id': {'$in': tasks_chunk}}, ['_id']
            ).limit(runs_limit))
            for j in range(0, len(runs), CHUNK_SIZE):
                runs_chunk = [row['_id'] for row in runs[i:i + CHUNK_SIZE]]
                are_runs_deleted.append(self._delete_runs(runs_chunk))
            if all(are_runs_deleted):
                self.limits[
                    self.mongo_client.arcee.task] = self.delete_in_chunks(
                    self.mongo_client.arcee.task, '_id', tasks_chunk)
            else:
                # can't delete more tasks as can't delete more runs
                break
        else:
            all_tasks_deleted = True
        return all_tasks_deleted

    def get_deleted_cloud_account(self):
        result = (None, None)
        session = self.get_session()
        stmt = """SELECT cloudaccount.id, organization.is_demo
                  FROM cloudaccount
                  JOIN organization
                  ON organization.id = cloudaccount.organization_id
                  WHERE (organization.deleted_at != 0
                  OR cloudaccount.deleted_at != 0)
                  AND cloudaccount.cleaned_at = 0
                  LIMIT 1"""
        try:
            result = next(session.execute(stmt))
        except StopIteration:
            pass
        finally:
            session.close()
        return result

    def update_cleaned_at(self, cloud_account_id=None, organization_id=None):
        session = self.get_session()
        now = int(datetime.utcnow().timestamp())
        if cloud_account_id:
            LOG.info(
                f'Updating cleaned_at for cloud account {cloud_account_id}')
            stmt = f"""UPDATE cloudaccount
                       SET cleaned_at={now} WHERE id='{cloud_account_id}'"""
        elif organization_id:
            LOG.info(
                f'Updating cleaned_at for organization {organization_id}')
            stmt = f"""UPDATE organization
                       SET cleaned_at={now} WHERE id='{organization_id}'"""
        else:
            return
        try:
            session.execute(stmt)
            session.commit()
        finally:
            session.close()

    def get_archive_file(self, cloud_account_id):
        last_file_name = f'{cloud_account_id}_1.json'
        os.makedirs(ARCHIVE_PATH, exist_ok=True)
        files = os.listdir(ARCHIVE_PATH)
        cloud_acc_files = sorted(
            [x for x in files if cloud_account_id in x],
            key=lambda x: self.get_file_number(x), reverse=True)
        if cloud_acc_files:
            last_file_name = cloud_acc_files[0]
        return last_file_name

    @staticmethod
    def get_file_length(filename):
        path = os.path.join(ARCHIVE_PATH, filename)
        if not os.path.isfile(path):
            result = 0
        else:
            with open(path, 'r') as f:
                result = len(f.readlines())
        return result

    @staticmethod
    def get_file_number(filename):
        return int(filename.split('_')[1].split('.json')[0])

    @staticmethod
    def _row_to_json(row):
        # wrap not json data types to use by mongoimport
        for k, v in row.items():
            if isinstance(v, datetime):
                row[k] = {'$date': v.strftime('%Y-%m-%dT%H:%M:%SZ')}
            elif isinstance(v, ObjectId):
                row[k] = {'$oid': str(v)}
        return json.dumps(row)

    def split_chunk_by_files(self, chunk, available_rows_count, filename,
                             cloud_account_id, file_max_rows):
        result = {}
        if available_rows_count < 0:
            available_rows_count = 0
        result[filename] = chunk[:available_rows_count]
        new_filename = filename
        for i in range(available_rows_count, len(chunk), file_max_rows):
            count = self.get_file_number(new_filename) + 1
            new_filename = f'{cloud_account_id}_{count}.json'
            result[new_filename] = chunk[i:i+file_max_rows]
        return result

    def _delete_by_organization(self, org_id, token, infra_token):
        if not token:
            self.update_cleaned_at(organization_id=org_id)
            return
        arcee_collections = [self.mongo_client.arcee.dataset,
                             self.mongo_client.arcee.goal,
                             self.mongo_client.arcee.leaderboard,
                             self.mongo_client.arcee.leaderboard_dataset,
                             self.mongo_client.arcee.model]
        bulldozer_collections = [self.mongo_client.bulldozer.template,
                                 self.mongo_client.bulldozer.runset,
                                 self.mongo_client.bulldozer.runner]
        LOG.info('Start processing ML objects for organization %s', org_id)
        for collection in arcee_collections:
            self.limits[collection] = self.delete_in_chunks(
                collection, 'token', token)
        for collection in bulldozer_collections:
            self.limits[collection] = self.delete_in_chunks(
                collection, 'token', infra_token)
        tasks_deleted = self._delete_by_task(token)

        if tasks_deleted and all(
                limit > 0 for collection, limit in self.limits.items()
                if collection in arcee_collections + bulldozer_collections):
            self.update_cleaned_at(organization_id=org_id)

    def organization_limits(self):
        collections = [self.mongo_client.arcee.task,
                       self.mongo_client.arcee.dataset,
                       self.mongo_client.arcee.goal,
                       self.mongo_client.arcee.leaderboard,
                       self.mongo_client.arcee.leaderboard_dataset,
                       self.mongo_client.arcee.run,
                       self.mongo_client.arcee.console,
                       self.mongo_client.arcee.log,
                       self.mongo_client.arcee.milestone,
                       self.mongo_client.arcee.stage,
                       self.mongo_client.arcee.proc_data,
                       self.mongo_client.arcee.model,
                       self.mongo_client.arcee.model_version,
                       self.mongo_client.bulldozer.template,
                       self.mongo_client.bulldozer.runset,
                       self.mongo_client.bulldozer.runner]
        return [self.limits[x] for x in collections]

    def delete_by_organization(self):
        info = self.get_deleted_organization_info()
        if not info:
            return
        while info and all(limit > 0 for limit in self.organization_limits()):
            org_id, token, infra_token = info
            self._delete_by_organization(org_id, token, infra_token)
            info = self.get_deleted_organization_info()
        LOG.info('Organizations ML objects processing is completed')

    def _delete_by_cloud_account(self, cloud_account_id, is_demo):
        restapi_collections = [self.mongo_client.restapi.raw_expenses,
                               self.mongo_client.restapi.resources]
        LOG.info(f'Started processing for cloud account {cloud_account_id}')
        for collection in restapi_collections:
            archive = False
            if (collection == self.mongo_client.restapi.raw_expenses
                    and self.archive_enable and not is_demo):
                archive = True
            self.limits[collection] = self.delete_in_chunks(
                    collection, 'cloud_account_id', cloud_account_id,
                    archive=archive, archive_cloud_account_id=cloud_account_id)
        if all(limit > 0 for collection, limit in self.limits.items()
               if collection in restapi_collections):
            self.update_cleaned_at(cloud_account_id=cloud_account_id)

    def cloud_account_limits(self):
        collections = [self.mongo_client.restapi.resources,
                       self.mongo_client.restapi.raw_expenses]
        return [self.limits[x] for x in collections]

    def delete_by_cloud_account(self):
        cloud_account_id, is_demo = self.get_deleted_cloud_account()
        while cloud_account_id and all(
                limit > 0 for limit in self.cloud_account_limits()):
            self._delete_by_cloud_account(cloud_account_id, is_demo)
            cleaned_cloud_account_id = cloud_account_id
            cloud_account_id, is_demo = self.get_deleted_cloud_account()
            if cleaned_cloud_account_id == cloud_account_id:
                # last cloud account that can't be cleaned up in current
                # iteration, should be cleaned in the next run
                break
        LOG.info('Cloud accounts processing is completed')

    def clean_mongo(self):
        settings = self.get_settings()
        self.archive_enable = bool(
            settings.get('archive_enable', False)) or ARCHIVE_ENABLED
        self.file_max_rows = int(settings.get(
            'file_max_rows', 0)) or FILE_MAX_ROWS
        self.chunk_size = int(settings.get('chunk_size') or CHUNK_SIZE)
        rows_limit = int(settings.get('rows_limit') or ROWS_LIMIT)
        for collection in self.limits:
            self.limits[collection] = rows_limit
        self.delete_by_cloud_account()
        self.delete_by_organization()
        LOG.info('Processing completed')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleanmongo = CleanMongoDB()
    cleanmongo.clean_mongo()
