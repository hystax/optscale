import base64
import csv
import json
import os
from datetime import datetime, time, timedelta, timezone
from functools import cached_property
from typing import Dict, Iterable, Tuple

from azure.storage.blob import BlobServiceClient

import boto3
from boto3 import Session
from botocore.client import BaseClient as BotoClient

from clickhouse_driver import Client as ClickHouseClient
from pymongo import MongoClient
from kombu.log import get_logger

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

from bi_exporter.bumblebi.common.consts import HEADERS, CLOUD_NAME_MAP
from bi_exporter.bumblebi.common.enums import DataSetEnum

LOG = get_logger(__name__)
DEFAULT_REGION = 'us-east-1'
BI_FOLDER = 'bi_exporter/bi'


class BaseExporter:
    _config_cl: ConfigClient
    credentials: dict

    def __init__(self, config_cl, credentials):
        self._config_cl = config_cl
        self.credentials = credentials

    @cached_property
    def rest_cl(self) -> RestClient:
        return RestClient(
            url=self._config_cl.restapi_url(),
            secret=self._config_cl.cluster_secret(),
        )

    @cached_property
    def mongo_cl(self) -> MongoClient:
        mongo_params = self._config_cl.mongo_params()
        mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
        return MongoClient(mongo_conn_string)

    @cached_property
    def clickhouse_cl(self) -> ClickHouseClient:
        user, password, host, db_name = self._config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user
        )

    def _upload(
        self, org_bi: Dict, data_set: DataSetEnum, filename: str,
            dry: bool = False
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def _cleanup(file_path: str) -> None:
        try:
            os.remove(file_path)
        except OSError as exc:
            LOG.warning('Can\'t remove file %s, exception: %s',
                        file_path, str(exc))

    def _get_expenses_clickhouse(
        self,
        cloud_account_ids: Iterable[str],
        resource_ids: Iterable[str],
        start_date: int,
        end_date: int,
        limit: int = 0,
        offset: int = 0,
    ):
        query = """
            SELECT
                date,
                cloud_account_id,
                resource_id,
                SUM(cost * sign) AS total_cost
            FROM expenses
            WHERE date >= %(start_date)s
                AND date <= %(end_date)s
                AND cloud_account_id in cloud_account_ids
                AND resource_id in resource_ids
            GROUP BY date, cloud_account_id, resource_id
            ORDER BY cloud_account_id, resource_id
        """
        if limit:
            query += "LIMIT %(offset)s, %(limit)s"

        result = self.clickhouse_cl.execute(
            query=query,
            params={
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
                "offset": offset,
            },
            external_tables=[
                {
                    "name": "cloud_account_ids",
                    "structure": [("_id", "String")],
                    "data": [{"_id": r_id} for r_id in cloud_account_ids],
                },
                {
                    "name": "resource_ids",
                    "structure": [("_id", "String")],
                    "data": [{"_id": r_id} for r_id in resource_ids],
                }
            ],
        )

        return result

    __PROJECT_RESOURCE_FIELDS = {
        "_id": 1,
        "employee_id": 1,
        "pool_id": 1,
        "cluster_type_id": 1,
        "first_seen": 1,
        "last_seen": 1,
        "cloud_resource_id": 1,
        "cloud_console_link": 1,
        "name": 1,
        "region": 1,
        "resource_type": 1,
        "tags": 1,
        "active": 1,
        "recommendations": 1,
        "deleted_at": 1,
        "cloud_account_id": 1,
    }

    def _get_resources(
        self, cloud_acc_ids: Iterable[str], start_date: int, end_date: int
    ) -> Iterable[Dict]:
        res = self.mongo_cl.restapi.resources.find(
            {
                "cloud_account_id": {"$in": list(cloud_acc_ids)},
                "$and": [
                    {"first_seen": {"$lte": end_date}},
                    {"last_seen": {"$gte": start_date}},
                ],
            },
            list(self.__PROJECT_RESOURCE_FIELDS.keys()),
        )
        return res

    @staticmethod
    def _create_csv_writer(file):
        return csv.writer(file, delimiter=",", quotechar='"',
                          quoting=csv.QUOTE_NONNUMERIC)

    def _process_expenses(self, csv_writer, start: int, end: int,
                          resources: Iterable) -> Tuple[int, int]:
        cloud_accs = set()
        resource_ids = set()

        expenses_cnt, zero_expenses_cnt = 0, 0
        for resource in resources:
            cloud_accs.add(resource['cloud_account_id'])
            resource_ids.add(resource['_id'])

        expenses = self._get_expenses_clickhouse(
            list(cloud_accs),
            list(resource_ids),
            start,
            end,
        )

        existing_expenses_res_ids = set()
        for dt, _, resource_id, cost in expenses:
            csv_writer.writerow([dt, resource_id, round(cost, 5)])
            existing_expenses_res_ids.add(resource_id)

        expenses_cnt = len(expenses)

        without_exp_res_ids = resource_ids - existing_expenses_res_ids

        for resource in resources:
            if resource['_id'] not in without_exp_res_ids:
                continue
            start_res = max(start, resource.get("first_seen"))
            start_res = datetime.combine(
                datetime.fromtimestamp(
                    start_res), time.min
            )

            end_res = min(end, resource.get("last_seen"))
            end_dt = datetime.fromtimestamp(
                end_res)
            end_res = datetime.combine(end_dt,
                                       time.max)

            resource_id = resource["_id"]
            for dt in range(
                    int(start_res.timestamp()),
                    int(end_res.timestamp()),
                    int(timedelta(
                        days=1).total_seconds()),
            ):
                csv_writer.writerow(
                    [datetime.fromtimestamp(dt),
                     resource_id, 0]
                )
                zero_expenses_cnt = zero_expenses_cnt + 1

        return expenses_cnt, zero_expenses_cnt

    @staticmethod
    def decoded_tags(tags):
        if not tags:
            return {}
        new_map = {}
        for k, v in tags.items():
            new_key = base64.b64decode(k.encode('utf-8')).decode('utf-8')
            new_map[new_key] = v
        return new_map

    def export(self, organization_bi_id: str) -> None:
        _, org_bi = self.rest_cl.bi_get(organization_bi_id)
        bi_id = org_bi['id']
        days = org_bi["days"]
        LOG.info(
            "start export for organization BI %s for the last %s days",
            organization_bi_id, days)

        organization_id = org_bi["organization_id"]

        now = datetime.combine(datetime.now(), time.min, tzinfo=timezone.utc)
        end = int(now.timestamp()) - 1
        start = int((now - timedelta(days=days)).timestamp())

        _, org = self.rest_cl.organization_get(organization_id, details=True)

        _, res = self.rest_cl.cloud_account_list(organization_id)
        cloud_accs_map = {x["id"]: x for x in res["cloud_accounts"]}

        _, res = self.rest_cl.employee_list(organization_id)
        empls_map = {x["id"]: x for x in res["employees"]}

        _, org_pool = self.rest_cl.pool_get(org["pool_id"], children=True)
        pools_map = {x["id"]: x for x in org_pool["children"]}
        pools_map[org["pool_id"]] = org_pool

        _, res = self.rest_cl.cluster_type_list(organization_id)
        ctypes_map = {x["id"]: x for x in res["cluster_types"]}

        _, opt = self.rest_cl.optimizations_get(organization_id)
        opt_ts = opt.get('last_completed', 0)

        cnt = 0
        expenses_cnt, zero_expenses_cnt = 0, 0
        # I've tested on different sizes on buffer and the time of execution
        # mostly the same
        bulk_size = 3000
        buf = [None] * bulk_size
        timer_start = datetime.now()
        resources_f_name = os.path.join(
            BI_FOLDER, f"{bi_id}_{DataSetEnum.RESOURCES}.csv")
        recommendations_f_name = os.path.join(
            BI_FOLDER, f"{bi_id}_{DataSetEnum.RECOMMENDATIONS}.csv")
        expenses_f_name = os.path.join(
            BI_FOLDER, f"{bi_id}_{DataSetEnum.EXPENSES}.csv")
        with open(resources_f_name, "w") as res_f:
            with open(recommendations_f_name, "w") as rec_f:
                with open(expenses_f_name, "w") as exp_f:
                    # creating CSV writers and writing headers to each one
                    resources_csv = self._create_csv_writer(res_f)
                    resources_csv.writerow(HEADERS[DataSetEnum.RESOURCES])
                    recommendations_csv = self._create_csv_writer(rec_f)
                    recommendations_csv.writerow(HEADERS[DataSetEnum.RECOMMENDATIONS])
                    expenses_csv = self._create_csv_writer(exp_f)
                    expenses_csv.writerow(HEADERS[DataSetEnum.EXPENSES])

                    resources = self._get_resources(
                        cloud_accs_map.keys(), start, end)
                    # iterating over resources one by one
                    for resource in resources:
                        ca = cloud_accs_map.get(resource.get("cloud_account_id"))
                        if not ca:
                            LOG.info("oops, no CAcc for %s",
                                     resource.get('cloud_account_id'))
                            continue

                        empl_id = resource.get("employee_id")
                        employee = empls_map[empl_id]

                        pool_id = resource.get("pool_id")
                        pool = pools_map[pool_id]

                        cluster_type_id = resource.get("cluster_type_id")
                        if cluster_type_id:
                            cluster_name = ctypes_map[cluster_type_id].name
                        else:
                            cluster_name = None

                        fseen_dt = datetime.fromtimestamp(resource.get("first_seen"))
                        lseen_dt = datetime.fromtimestamp(resource.get("last_seen"))

                        tags = self.decoded_tags(resource.get("tags", {}))

                        resources_csv.writerow(
                            [
                                org["name"],
                                org["id"],
                                ca["id"],
                                CLOUD_NAME_MAP.get(ca["type"], ca["type"]),
                                ca["name"],
                                resource.get("_id"),
                                resource.get("cloud_resource_id"),
                                resource.get("cloud_console_link"),
                                employee["id"],
                                employee["name"],
                                tags,
                                fseen_dt,
                                lseen_dt,
                                resource.get("name"),
                                pool["id"],
                                pool["name"],
                                pool["purpose"],
                                pool["parent_id"],
                                resource.get("region"),
                                resource.get("resource_type"),
                                resource.get("active"),
                                cluster_type_id,
                                cluster_name,
                                resource.get("service_name"),
                            ]
                        )

                        # recommendations for the resource
                        recommendations = resource.get("recommendations", {})
                        if (
                                recommendations and
                                recommendations.get('run_timestamp', 0) == opt_ts and
                                not resource.get("deleted_at")
                        ):
                            for r in resource.get("recommendations", {}).get(
                                    "modules", []
                            ):
                                saving = r.get("saving", 0)
                                if saving:
                                    recommendations_csv.writerow(
                                        [
                                            resource.get("_id"),
                                            r.get("name"),
                                            round(saving, 4)
                                        ]
                                    )
                        # collecting buffer of resources for bulk
                        # processing of expenses

                        buf[cnt % bulk_size] = resource
                        cnt = cnt + 1

                        # when the buffer is full - collect expenses for
                        # processed resources
                        if cnt % bulk_size == 0:
                            LOG.info("Processing expenses for bulk: %s..%s",
                                     bulk_size, cnt)
                            e, zero_e = self._process_expenses(
                                expenses_csv, start, end, buf)
                            expenses_cnt += e
                            zero_expenses_cnt += zero_e

                    # if the last chunk was not full we need to write
                    # the rest expenses
                    if cnt % bulk_size != 0:
                        LOG.info(
                            "Processing expenses for the last bulk: %s..%s",
                            int(cnt / bulk_size) * bulk_size, cnt)
                        e, zero_e = self._process_expenses(
                            expenses_csv, start, end, buf[:cnt % bulk_size])
                        expenses_cnt += e
                        zero_expenses_cnt += zero_e

        timer_end = datetime.now()
        LOG.info(f"Statistics for BI {organization_bi_id} - organization_id {organization_id}:\n"
                 f"- Days: {days}\n"
                 f"- Between: {datetime.fromtimestamp(start)}..{datetime.fromtimestamp(end)}\n"
                 f"- Resource count: {cnt}\n"
                 f"- Expenses count: {expenses_cnt}\n"
                 f"- Zero Expenses count: {zero_expenses_cnt}\n"
                 f"- Time: {timer_end - timer_start}\n")
        self._upload(org_bi, DataSetEnum.RESOURCES, resources_f_name)
        self._upload(org_bi, DataSetEnum.RECOMMENDATIONS, recommendations_f_name)
        self._upload(org_bi, DataSetEnum.EXPENSES, expenses_f_name)
        self._cleanup(resources_f_name)
        self._cleanup(recommendations_f_name)
        self._cleanup(expenses_f_name)


class AwsExporter(BaseExporter):
    def __init__(self, config_cl: ConfigClient, credentials: dict):
        super().__init__(config_cl, credentials)

    @cached_property
    def _aws_session(self) -> Session:
        return boto3.Session(
            aws_access_key_id=self.credentials.get('access_key_id'),
            aws_secret_access_key=self.credentials.get('secret_access_key'),
            region_name=DEFAULT_REGION
        )

    @cached_property
    def _s3_client(self) -> BotoClient:
        return self._aws_session.client("s3")

    def _upload(self, org_bi: Dict, data_set: DataSetEnum, filename: str,
                dry: bool = False) -> None:
        if dry:
            return
        LOG.info("Uploading to S3: %s", filename)
        bucket = org_bi["meta"]["bucket"]
        s3_prefix = org_bi["meta"].get("s3_prefix", '')
        path = os.path.join(s3_prefix, data_set)

        fname = os.path.basename(filename)
        dest = os.path.join(path, fname)
        self._s3_client.upload_file(filename, bucket, dest)
        LOG.info("Uploaded to S3: %s", dest)

        manifest_file_name = "manifest.json"
        manifest = {
            "fileLocations": [{"URIPrefixes": [os.path.join(
                "s3://", bucket, path)]}],
            "globalUploadSettings": {
                "format": "CSV",
                "delimiter": ",",
                "textqualifier": "'",
                "containsHeader": "true",
            },
        }

        self._s3_client.put_object(
            Body=json.dumps(manifest),
            Bucket=bucket,
            Key=os.path.join(path, manifest_file_name),
        )
        LOG.info("Uploaded manifest: %s",
                 os.path.join(path, manifest_file_name))


class AzureExporter(BaseExporter):
    def __init__(self, config_cl: ConfigClient, credentials: dict):
        super().__init__(config_cl, credentials)

    @cached_property
    def _blob_service(self) -> BlobServiceClient:
        return BlobServiceClient.from_connection_string(
            self.credentials.get('connection_string'))

    def _upload(self, org_bi: Dict, data_set: DataSetEnum, filename: str,
                dry: bool = False) -> None:
        if dry:
            return
        LOG.info("Uploading to Azure Storage: %s", filename)
        blob_name = os.path.basename(filename)
        blob_client = self._blob_service.get_blob_client(
            container=self.credentials.get('container'), blob=blob_name)
        if blob_client.exists():
            blob_client.delete_blob()
        with open(file=filename, mode="rb") as data:
            blob_client.upload_blob(data)
