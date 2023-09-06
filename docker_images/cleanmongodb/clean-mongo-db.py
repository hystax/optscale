import os
import logging
from optscale_client.config_client.client import Client as ConfigClient
from datetime import datetime
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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

    @staticmethod
    def delete_rows(collection, cloud_account_id,  chunk_size, rows_limit):
        row_ids = list(collection.find(
            {'cloud_account_id': cloud_account_id}, ['_id']).limit(rows_limit))
        for j in range(0, len(row_ids), chunk_size):
            chunk = [row['_id'] for row in row_ids[j: j + chunk_size]]
            collection.delete_many({'_id': {'$in': chunk}})

    def recursive_delete_rows(self, chunk_size, exp_limit, res_limit):
        cloud_account_id = self.get_deleted_cloud_account()
        if cloud_account_id:
            LOG.info(f'Started processing for cloud account {cloud_account_id}')
            exp_count = self.mongo_client.restapi.raw_expenses.count_documents(
                {'cloud_account_id': cloud_account_id})
            if exp_count:
                self.delete_rows(
                    self.mongo_client.restapi.raw_expenses, cloud_account_id,
                    chunk_size, exp_limit)
            res_count = self.mongo_client.restapi.resources.count_documents(
                {'cloud_account_id': cloud_account_id})
            if res_count:
                self.delete_rows(
                    self.mongo_client.restapi.resources, cloud_account_id,
                    chunk_size, res_limit)
            if exp_count <= exp_limit and res_count <= res_limit:
                self.update_cleaned_at(cloud_account_id)
                exp_limit = exp_limit - exp_count
                res_limit = res_limit - res_count
                self.recursive_delete_rows(chunk_size, exp_limit, res_limit)

    def clean_mongo(self):
        settings = self.get_settings()
        chunk_size = int(settings.get('chunk_size') or CHUNK_SIZE)
        rows_limit = int(settings.get('rows_limit') or ROWS_LIMIT)
        self.recursive_delete_rows(chunk_size, rows_limit, rows_limit)
        LOG.info('Processing completed')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleanmongo = CleanMongoDB()
    cleanmongo.clean_mongo()
