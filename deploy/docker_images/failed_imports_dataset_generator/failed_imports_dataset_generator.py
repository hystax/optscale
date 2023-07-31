import boto3
import csv
import json
import logging
import os
from config_client.client import Client as ConfigClient
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib import parse

DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80
LOG = logging.getLogger(__name__)
IMPORT_THRESHOLD = 2 * 86400  # 2 days

HEADERS = [
    "cloud account id", "cloud account name", "cloud account type",
    "creation date", "last success report date", "last error",
    "organization id", "organization name", "latest token date",
    "latest employee email"
]

TAGS = {"public": "yes"}


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


def _get_aws_s3_session(access_key, secret_key):
    aws_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return aws_session.client('s3')


def _upload(s3_client, bucket, path, filename):
    LOG.info(f"Uploading to S3: {filename}")
    s3_client.upload_file(filename, bucket, os.path.join(path, filename),
                          ExtraArgs={"Tagging": parse.urlencode(TAGS)})
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
    return csv.writer(file, delimiter=',', quotechar='"',
                      quoting=csv.QUOTE_NONNUMERIC)


def _dt_to_human_readable(dt):
    try:
        return dt.strftime('%a %d %b %Y, %I:%M%p')
    except Exception:
        return None


def _timestamp_to_human_readable(ts):
    try:
        return _dt_to_human_readable(datetime.utcfromtimestamp(float(ts)))
    except Exception:
        return None


def _get_failed_cloud_accounts(mydb):
    now = datetime.utcnow().timestamp()
    import_dt = now - IMPORT_THRESHOLD
    query = f"""
        SELECT ca_t.id, ca_t.name, ca_t.type, ca_t.created_at,
            ca_t.last_import_at, ca_t.last_import_attempt_error,
            ca_t.organization_id, org_t.name
        FROM (
            SELECT id, name, organization_id, type, created_at, last_import_at, 
                last_import_attempt_error
            FROM cloudaccount
            WHERE deleted_at=0
                AND auto_import=true
                AND last_import_at<{import_dt}
                AND last_import_attempt_at>={import_dt}
        ) AS ca_t
        LEFT OUTER JOIN (
            SELECT id, name
            FROM organization
            WHERE deleted_at=0
                AND is_demo=0
        ) AS org_t ON ca_t.organization_id=org_t.id
        """
    result = []
    query_result = mydb.execute(query)
    for r in query_result:
        result.append([
            r[0], r[1], r[2], _timestamp_to_human_readable(r[3]),
            _timestamp_to_human_readable(r[4]), r[5], r[6], r[7]
        ])
    return result


def _get_last_employee_info(auth_db, organization_ids, config_cl):
    query = f"""
        SELECT assignment_t.resource_id, token_t.created_at, user_t.email
        FROM (
            SELECT user_id, resource_id
            FROM assignment
            WHERE deleted_at=0
                AND resource_id in ('{"', '".join(organization_ids)}')
        ) AS assignment_t
        JOIN (
            SELECT user_id, created_at
            FROM token
            WHERE created_at=(
                SELECT MAX(created_at)
                FROM token AS max_created_at
                WHERE max_created_at.user_id=token.user_id)
            )
            AS token_t ON token_t.user_id=assignment_t.user_id
        JOIN (
            SELECT id, email
            FROM user
            WHERE deleted_at=0
        ) AS user_t ON token_t.user_id=user_t.id
        """
    query_result = auth_db.execute(query)
    result = {}
    blacklist = domain_blacklist(config_cl)
    for r in query_result:
        r_id, dt, email = r
        if any(filter(lambda x: x in email, blacklist)):
            continue
        if not result.get(r_id) or dt > result[r_id][0]:
            result[r_id] = [dt, email]
    for s in result.values():
        s[0] = _dt_to_human_readable(s[0])
    return result


def domain_blacklist(_config):
    try:
        return _config.domains_blacklist(blacklist_key='failed_import_email')
    except Exception:
        return []


def main(config_cl):
    params = config_cl.read_branch('/failed_imports_dataset_generator')
    if params.get('enable') == "False":
        return
    aws_access_key = params['aws_access_key_id']
    aws_secret_key = params['aws_secret_access_key']
    bucket = params['bucket']
    s3_path = params.get('s3_path', '')
    filename = params['filename']
    auth_cl = _get_session_to_auth_db(config_cl)
    mydb_cl = _get_session_to_my_db(config_cl)
    result = _get_failed_cloud_accounts(mydb_cl)
    organization_ids = list(map(lambda x: x[6], result))
    employee_info = _get_last_employee_info(
        auth_cl, organization_ids, config_cl)
    for r in result:
        r.extend(employee_info.get(r[6], [None, None]))
    with open(filename, 'w') as f:
        csv_writer = _create_csv_writer(f)
        csv_writer.writerow(HEADERS)
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
