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

    def get_deleted_cloud_account(self):
        session = self.get_session()
        stmt = """SELECT cloudaccount.id FROM cloudaccount
                  JOIN organization
                  ON organization.id = cloudaccount.organization_id
                  WHERE (organization.deleted_at != 0
                  OR cloudaccount.deleted_at != 0)
                  AND cloudaccount.cleaned_at = 0
                  LIMIT 1"""
        try:
            result = session.execute(stmt).scalar()
        finally:
            session.close()
        return result

    def update_cleaned_at(self, cloud_account_id):
        LOG.info(f'Updating cleaned_at for {cloud_account_id}')
        session = self.get_session()
        now = int(datetime.utcnow().timestamp())
        stmt = f"""UPDATE cloudaccount
                   SET cleaned_at={now} WHERE id='{cloud_account_id}'"""
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

    def delete_rows(self, collection, cloud_account_id,  chunk_size, rows_limit,
                    archive_enable=False, file_max_rows=0):
        rows = list(collection.find(
            {'cloud_account_id': cloud_account_id}).limit(rows_limit))
        for j in range(0, len(rows), chunk_size):
            chunk = rows[j: j + chunk_size]
            chunk_ids = [row['_id'] for row in chunk]
            if archive_enable:
                LOG.info('Archiving raw expenses')
                last_file_name = self.get_archive_file(cloud_account_id)
                file_length = self.get_file_length(last_file_name)
                split_data = self.split_chunk_by_files(
                    chunk, file_max_rows - file_length, last_file_name,
                    cloud_account_id, file_max_rows)
                for file, raw_expenses in split_data.items():
                    path = os.path.join(ARCHIVE_PATH, file)
                    exp_count = len(raw_expenses)
                    with open(path, 'a+') as f:
                        if raw_expenses:
                            LOG.info(
                                f'Saving {exp_count} expenses to file {path}')
                            for row in raw_expenses:
                                f.write(self._row_to_json(row) + '\n')
            collection.delete_many({'_id': {'$in': chunk_ids}})

    def clean_cloud_account(self, chunk_size, exp_limit, res_limit,
                            archive_enable, file_max_rows):
        cloud_account_id = self.get_deleted_cloud_account()
        if cloud_account_id:
            LOG.info(f'Started processing for cloud account {cloud_account_id}')
            exp_count = self.mongo_client.restapi.raw_expenses.count_documents(
                {'cloud_account_id': cloud_account_id})
            if exp_count:
                self.delete_rows(
                    self.mongo_client.restapi.raw_expenses, cloud_account_id,
                    chunk_size, exp_limit, archive_enable, file_max_rows)
            res_count = self.mongo_client.restapi.resources.count_documents(
                {'cloud_account_id': cloud_account_id})
            if res_count:
                self.delete_rows(self.mongo_client.restapi.resources,
                                 cloud_account_id, chunk_size, res_limit)
            return cloud_account_id, exp_count, res_count

    def clean(self, chunk_size, exp_limit, res_limit,
              archive_enable, file_max_rows):
        while exp_limit and res_limit:
            result = self.clean_cloud_account(
                chunk_size, exp_limit, res_limit, archive_enable, file_max_rows)
            if result is None:
                return
            cloud_account_id, exp_count, res_count = result
            if exp_count <= exp_limit and res_count <= res_limit:
                self.update_cleaned_at(cloud_account_id)
            exp_limit = exp_limit - exp_count
            res_limit = res_limit - res_count

    def clean_mongo(self):
        settings = self.get_settings()
        chunk_size = int(settings.get('chunk_size', 0) or CHUNK_SIZE)
        rows_limit = int(settings.get('rows_limit', 0) or ROWS_LIMIT)
        archive_enable = bool(
            settings.get('archive_enable', False)) or ARCHIVE_ENABLED
        file_max_rows = int(settings.get('file_max_rows', 0)) or FILE_MAX_ROWS
        self.clean(chunk_size, rows_limit, rows_limit,
                   archive_enable, file_max_rows)
        LOG.info('Processing completed')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleanmongo = CleanMongoDB()
    cleanmongo.clean_mongo()
