import boto3
import csv
import json
import logging
import re
import os
from clickhouse_driver import Client as ClickHouseClient
from collections import defaultdict
from config_client.client import Client as ConfigClient
from datetime import datetime, timedelta
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)

HEADERS = ["user id", "email", "name", "user_created_at", "last_login_at",
           "employee_id", "organization_joined_at", "organization_id",
           "organization name", "currency", "pools count", "total_saving",
           "last_30_days_cost"]


def _get_session_to_auth_db(config_cl):
    user, password, host, db_name = config_cl.auth_db_params()
    auth_url = 'mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4' % (
        user, password, host, db_name)
    engine = create_engine(auth_url, encoding='utf-8')
    return sessionmaker(bind=engine)()


def _get_session_to_my_db(config_cl):
    user, password, host, db_name = config_cl.rest_db_params()
    mydb_url = 'mysql+mysqlconnector://%s:%s@%s/%s?charset=utf8mb4' % (
        user, password, host, db_name)
    engine = create_engine(mydb_url, encoding='utf-8')
    return sessionmaker(bind=engine)()


def _get_mongo_client(config_cl):
    user, password, host, port, db_name = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % (
        user, password, host, port)
    return MongoClient(mongo_conn_string)


def _get_clickhouse_client(config_cl):
    user, password, host, db_name = config_cl.clickhouse_params()
    return ClickHouseClient(
        host=host, password=password, database=db_name, user=user)


def _get_aws_s3_session(access_key, secret_key):
    aws_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return aws_session.client('s3')


def _upload(s3_client, bucket, path, filename):
    LOG.info(f"Uploading to S3: {filename}")
    s3_client.upload_file(filename, bucket, os.path.join(path, filename))
    LOG.info(f"Uploaded to S3: {filename}")
    manifest_file_name = f"manifest.yaml"
    manifest = {
        "fileLocations": [
            {
                "URIPrefixes": [
                    os.path.join("s3://", bucket, path)
                ]
            }
        ],
        "globalUploadSettings": {
            "format": "CSV",
            "delimiter": ",",
            "textqualifier": "'",
            "containsHeader": "true"
        }
    }
    s3_client.put_object(
        Body=json.dumps(manifest),
        Bucket=bucket,
        Key=os.path.join(path, manifest_file_name)
    )
    LOG.info("Uploaded manifest")


def _create_csv_writer(file):
    return csv.writer(file, delimiter=',', quotechar="'",
                      quoting=csv.QUOTE_MINIMAL)


def _get_organization_ids(mydb):
    query = """
    SELECT id
    FROM organization
    WHERE deleted_at=0 and is_demo=0
    """
    result = mydb.execute(query)
    return [x[0] for x in result]


def _get_cloud_account_types(mydb):
    res = dict(mydb.execute('DESC cloudaccount type').first())['Type']
    return re.findall("[A-Z_]+", res)


def _get_cloud_account_counts(mydb, organization_id):
    cloud_acc_count_map = defaultdict(list)
    query = f"""
    SELECT type, id
    FROM cloudaccount
    WHERE deleted_at=0 AND organization_id='{organization_id}'
    """
    result = mydb.execute(query)
    for ca_type, ca_id in result:
        cloud_acc_count_map[ca_type].append(ca_id)
    return cloud_acc_count_map


def _get_auth_data(auth, user_ids_str):
    auth_query = f"""
        SELECT user_t.id, user_t.email, user_t.display_name, user_t.created_at,
          token_t.last_login
        FROM (
          SELECT user.id, user.email, user.display_name,
            user.created_at
          FROM user
          WHERE email NOT LIKE "%@hystax.com" AND deleted_at=0 AND
            id in ('{user_ids_str}')
        ) AS user_t
        LEFT JOIN (
          SELECT user_id, created_at AS "last_login"
          FROM `token`
          WHERE created_at=(
            SELECT MAX(created_at)
            FROM token AS max_created_at
            WHERE max_created_at.user_id=token.user_id)
        ) AS token_t
        ON user_t.id=token_t.user_id
    """
    auth_result = auth.execute(auth_query)
    return {x[0]: x for x in auth_result}


def _get_mydb_data(mydb, organization_id):
    mydb_query = f"""
            SELECT emp_t.auth_user_id, emp_t.id,
              emp_t.created_at AS "organization_joined_at",
              org_t.name, org_t.currency, pool_t.pool_count
            FROM (
              SELECT auth_user_id, id, created_at, organization_id
              FROM employee
              WHERE organization_id='{organization_id}'
            ) AS emp_t
            LEFT JOIN (
              SELECT id, name, currency
              FROM organization
              WHERE id='{organization_id}'
            ) AS org_t
            ON org_t.id=emp_t.organization_id
            LEFT JOIN (
              SELECT organization_id, count(*) AS "pool_count"
              FROM pool
              WHERE organization_id='{organization_id}' AND deleted_at=0
              GROUP BY organization_id
            ) AS pool_t
            ON emp_t.organization_id = pool_t.organization_id
        """
    return mydb.execute(mydb_query)


def _get_checklist(mydb, org_id):
    result = mydb.execute(f"""
        SELECT last_completed
        FROM checklist
        WHERE organization_id='{org_id}' AND deleted_at=0
        """).first()
    return result[0]


def _get_expenses_by_clouds(ch_cl, cloud_account_ids):
    if not cloud_account_ids:
        return {}
    start_date = datetime.utcnow() - timedelta(days=30)
    query = """
        SELECT
            cloud_account_id,
            SUM(cost * sign) AS total_cost
        FROM expenses
        WHERE date >= %(start_date)s
            AND cloud_account_id IN cloud_account_ids
        GROUP BY cloud_account_id
    """
    result = ch_cl.execute(
        query=query,
        params={
            "start_date": start_date,
        },
        external_tables=[
            {
                'name': 'cloud_account_ids',
                'structure': [('_id', 'String')],
                'data': [{'_id': r_id} for r_id in cloud_account_ids]
            }
        ],
    )
    return {ca_id: cost for ca_id, cost in result}


def main(config_cl):
    params = config_cl.read_branch('/users_dataset_generator')
    if params.get('enable') == "False":
        return

    aws_access_key = params['aws_access_key_id']
    aws_secret_key = params['aws_secret_access_key']
    bucket = params['bucket']
    s3_path = params.get('s3_path', '')
    filename = params['filename']

    result = []
    mongo_cl = _get_mongo_client(config_cl)
    auth_cl = _get_session_to_auth_db(config_cl)
    mydb_cl = _get_session_to_my_db(config_cl)
    ch_cl = _get_clickhouse_client(config_cl)

    cad_types = _get_cloud_account_types(mydb_cl)
    organization_ids = _get_organization_ids(mydb_cl)
    for org_id in organization_ids:
        mydb_result = _get_mydb_data(mydb_cl, org_id)
        acc_type_ids_map = _get_cloud_account_counts(mydb_cl, org_id)
        cl_acc_ids = []
        for acc_ids in acc_type_ids_map.values():
            cl_acc_ids += acc_ids
        acc_cost_map = _get_expenses_by_clouds(ch_cl, cl_acc_ids)

        auth_user_org_data = defaultdict(list)
        for r in mydb_result:
            auth_user_org_data[r[0]].append(r)

        auth_user_ids_str = "', '".join(auth_user_org_data.keys())
        users = _get_auth_data(auth_cl, auth_user_ids_str)

        for user_id, user_data in users.items():
            _, email, display_name, created_at, last_login = user_data
            for row in auth_user_org_data.get(user_id, (
                    None, None, None, None, None)):
                (_, employee_id, emp_created_at, organization_name,
                 organization_currency, pools_count) = row

                total_saving = 0
                last_completed = _get_checklist(mydb_cl, org_id)
                if last_completed:
                    pipeline = [{
                        '$match': {'$and': [
                            {'created_at': last_completed},
                            {'organization_id': org_id}]}}, {
                        '$unwind': '$data'}, {
                        '$group': {'_id': '$organization_id',
                                   'total_saving': {'$sum': '$data.saving'}}}
                    ]
                    savings = list(mongo_cl.restapi.checklists.aggregate(
                        pipeline))
                    if savings:
                        total_saving = savings[0]['total_saving']

                expenses = 0
                org_acc_ids = list(acc_cost_map.keys())
                for cacc_id in org_acc_ids:
                    if cacc_id in acc_cost_map:
                        expenses += acc_cost_map[cacc_id]

                caccs_stat = []
                for acc_type in cad_types:
                    caccs_stat.append(len(acc_type_ids_map.get(acc_type, [])))

                result.append([user_id, email, display_name,
                               datetime.fromtimestamp(created_at), last_login,
                               employee_id, datetime.fromtimestamp(emp_created_at),
                               org_id, organization_name, organization_currency,
                               pools_count or 0, total_saving, expenses] + caccs_stat)

    with open(filename, 'w') as f:
        csv_writer = _create_csv_writer(f)
        csv_writer.writerow(HEADERS + cad_types)
        for r in result:
            csv_writer.writerow(r)
    LOG.info(f'Dataset file {filename} was generated. '
             f'Will upload to s3 bucket {bucket}')

    s3_client = _get_aws_s3_session(aws_access_key, aws_secret_key)
    _upload(s3_client, bucket, s3_path, filename)
    LOG.info("Finished processing. Rows count: %s" % len(result))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    config_cl = ConfigClient(host=etcd_host, port=int(etcd_port))
    config_cl.wait_configured()
    main(config_cl)
