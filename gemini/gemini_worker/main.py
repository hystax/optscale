import os
import logging
from itertools import combinations
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from kombu import Connection, Exchange, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging
from gemini.gemini_worker.duplicate_object_finder.factory import Factory
from etcd import Lock as EtcdLock
import clickhouse_connect
from clickhouse_connect.driver.httpclient import HttpClient as ClickHouseClient
from pymongo import MongoClient
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from gemini.gemini_worker.migrator import Migrator
from gemini.gemini_worker.duplicate_object_finder.aws.stats import Stats

DB_NAME = "gemini"
EXCHANGE_NAME = "gemini-tasks"
QUEUE_NAME = "gemini-task"
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type="direct")
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)
DEFAULT_ETCD_HOST = "etcd"
DEFAULT_ETCD_PORT = 80

DAYS_IN_MONTH = 30
PAIR = 2
STATUS_SUCCESS = "SUCCESS"

LOG = logging.getLogger(__name__)


class Worker(ConsumerMixin):
    def __init__(self, connection, config_client):
        self.connection = connection
        self.config_client = config_client
        self._rest_client = None
        self._clickhouse_client = None
        self._mongo_client = None

    @property
    def rest_client(self) -> RestClient:
        if self._rest_client is None:
            self._rest_client = RestClient(
                url=self.config_client.restapi_url(),
                secret=self.config_client.cluster_secret(),
            )
        return self._rest_client

    @property
    def clickhouse_client(self) -> ClickHouseClient:
        if self._clickhouse_client is None:
            user, password, host, _, port, secure = (
                self.config_client.clickhouse_params())
            self._clickhouse_client = clickhouse_connect.get_client(
                host=host, password=password, database=DB_NAME, user=user,
                port=port, secure=secure)
        return self._clickhouse_client

    @property
    def mongo_client(self) -> MongoClient:
        if self._mongo_client is None:
            mongo_params = self.config_client.mongo_params()
            self._mongo_client = MongoClient(mongo_params[0])
        return self._mongo_client

    @property
    def valid_states(self):
        return ["QUEUED", STATUS_SUCCESS]

    @staticmethod
    def get_now_timestamp() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=[TASK_QUEUE],
                accept=["json"],
                callbacks=[self.process_task],
                prefetch_count=10,
            )
        ]

    def _set_status(self, gemini_id: str, message: dict, status: str) -> None:
        body = {"status": status, **message}
        try:
            self.rest_client.gemini_update(gemini_id, body)
            LOG.info(f"Status updated to {status} for gemini {gemini_id}")
        except Exception as exc:
            LOG.exception(
                f"Not able to update status to {status} for gemini {gemini_id}: {exc}"
            )

    def _get_buckets_daily_cost(
        self, buckets: list[str], cloud_account_ids: list[str], last_run: int
    ) -> list:
        start_date = datetime.fromtimestamp(last_run).replace(
            hour=0, minute=0, second=0
        )
        end_date = datetime.fromtimestamp(last_run).replace(
            hour=23, minute=59, second=59
        )

        start_date = start_date - timedelta(days=3)
        end_date = end_date - timedelta(days=3)

        pipeline = [
            {
                "$match": {
                    "start_date": {
                        "$gte": start_date,
                        "$lte": end_date,
                    },
                    "pricing/unit": "GB-Mo",
                    "resource_id": {"$in": buckets},
                    "cloud_account_id": {"$in": cloud_account_ids},
                }
            },
            {
                "$group": {
                    "_id": "$resource_id",
                    "dailyCost": {"$sum": "$cost"},
                }
            },
        ]

        result = list(
            self.mongo_client.restapi.raw_expenses.aggregate(pipeline))

        found_buckets = [r["_id"] for r in result]
        for bucket in buckets:
            if bucket not in found_buckets:
                LOG.info(
                    f"Expenses was not found for bucket {bucket}, adding bucket to result"
                )
                result.append({"_id": bucket})

        return result

    def _add_bucket_monthly_cost(self, costs, buckets_stats):
        for cost in costs:
            if cost.get("dailyCost") is None:
                continue
            try:
                buckets_stats[cost["_id"]]["monthly_cost"] = (
                    cost["dailyCost"] * DAYS_IN_MONTH
                )
            except Exception as exc:
                LOG.error(
                    f"Could not calculate daily cost for bucket {cost['_id']}: {exc}"
                )
        return buckets_stats

    def _get_savings(self, stats, total_cost) -> float:
        try:
            return stats.duplicates_size / stats.total_size * total_cost
        except Exception as exc:
            LOG.error(f"Could not get savings, {exc}")
            return 0

    def _update_stats(
        self,
        gemini: dict,
        stats: Stats,
        matrix: dict,
        bucket_stats: dict,
        monthly_savings: float,
    ) -> None:
        gemini_id = gemini["id"]
        body = {
            "stats": {
                "total_objects": stats.total_objects,
                "filtered_objects": stats.filtered_objects,
                "total_size": stats.total_size,
                "duplicates_size": stats.duplicates_size,
                "duplicated_objects": stats.duplicated_objects,
                "monthly_savings": monthly_savings,
                "buckets": bucket_stats,
                "matrix": matrix,
            }
        }

        self.rest_client.gemini_update(gemini_id, body)
        LOG.info(f"Stats updated for gemini {gemini_id}, {body}")

    def _calculate_buckets_stats(
        self,
        buckets: list[str],
        cloud_account_ids: list[str],
        stats: Stats,
        last_run: int,
    ) -> None:
        """Calculate potential savings.
        1. Calculate total raw expenses for cloud accounts and buckets (resource IDs) passed as filters.
        2. Additional filters:
            - resource_id: Bucket name, indexed.
            - pricing/unit: "GB-Mo". Include only storage related expenses.
            - start_date and end_date: take expenses for 1 day,
              3 days before the last run time to guarantee raw expenses data from a cloud.
        3. Calculate potential savings proportionally to duplicates storage
           (duplicates storage/total storage = X/total cost,
           where X is duplicates cost or potential savings, when deleted)
        """

        buckets_daily_cost_list = self._get_buckets_daily_cost(
            buckets, cloud_account_ids, last_run
        )

        buckets_stats = self._add_bucket_monthly_cost(
            buckets_daily_cost_list, stats.buckets
        )

        total_daily_cost = sum(
            cost.get("dailyCost", 0) for cost in buckets_daily_cost_list
        )
        monthly_savings = self._get_savings(
            stats, total_daily_cost) * DAYS_IN_MONTH

        return buckets_stats, monthly_savings

    def _calculate_monthly_savings(
        self, duplicates_size: int, size: int, monthly_cost: float
    ) -> float:
        return (
            duplicates_size /
            size *
            monthly_cost) if size and monthly_cost else 0

    def _calculate_cross_matrix(
        self, gemini_id: str, buckets: list[str], buckets_stats: dict
    ) -> dict:
        """
        A query to get duplicated objects across bucket pairs, resulted in a dictionary matrix.
        Example for ["bucket_1", "bucket_2", "bucket_3"]:

        Query:
            WITH base AS (
                SELECT
                    tag,
                    bucket,
                    count(id) AS cnt,
                    sum(size) AS size
                FROM gemini
                WHERE id = %(gemini_id)s
                  AND bucket IN %(buckets)s
                GROUP BY tag, bucket
            )
            SELECT
                b1.bucket AS bucket_1,
                b2.bucket AS bucket_2,
                sum(b1.cnt + b2.cnt) AS total_count,
                sum(b1.size) AS total_size
            FROM base b1
            INNER JOIN base b2
                ON b1.tag = b2.tag
            GROUP BY
                b1.bucket,
                b2.bucket

        Result: {
                    "bucket_1": {
                        "bucket_1": {
                            "duplicated_objects": 128,
                            "duplicates_size": 3142458.0,
                            "monthly_savings": 5222
                        }
                        "bucket_2": {
                            "duplicated_objects": 3,
                            "duplicates_size": 142458.0,
                            "monthly_savings": 3331
                        },
                        "bucket_3": {
                            "duplicated_objects": 0,
                            "duplicates_size": 0,
                        },
                    },
                    "bucket_2": {
                        "bucket_1": {"duplicated_objects": 3, "duplicates_size": 142458.0, "monthly_savings": 3331},
                        "bucket_2": {"duplicated_objects": 0, "duplicates_size": 0, "monthly_savings": 0},
                        "bucket_3": {"duplicated_objects": 0, "duplicates_size": 0},
                    },
                    "bucket_3": {
                        "bucket_1": {"duplicated_objects": 0, "duplicates_size": 0},
                        "bucket_2": {"duplicated_objects": 0, "duplicates_size": 0},
                        "bucket_3": {"duplicated_objects": 0, "duplicates_size": 0},
                    }
                }
        """

        query = f"""
            WITH base AS (
                SELECT
                    tag,
                    bucket,
                    count(id) AS cnt,
                    sum(size) AS size
                FROM gemini
                WHERE id = %(gemini_id)s
                  AND bucket IN %(buckets)s
                GROUP BY tag, bucket
            )
            SELECT
                b1.bucket AS bucket_1,
                b2.bucket AS bucket_2,
                sum(b1.cnt + b2.cnt) AS total_count,
                sum(b1.size) AS total_size
            FROM base b1
            INNER JOIN base b2
                ON b1.tag = b2.tag
            GROUP BY
                b1.bucket,
                b2.bucket
        """
        result_q = self.clickhouse_client.query(query, parameters={
            'buckets': buckets, 'gemini_id': gemini_id
        })
        cross_matrix = defaultdict(lambda: defaultdict(dict))
        for r in result_q.result_rows:
            bucket_0 = r[0]
            bucket_1 = r[1]
            bucket_0_duplicates_size = r[3]
            bucket_0_size = buckets_stats.get(bucket_0, {}).get("size", 0)
            bucket_0_monthly_cost = buckets_stats.get(
                bucket_0, {}).get("monthly_cost")
            duplicated_objects = r[2]
            if bucket_0 == bucket_1:
                # because of sum(b1.cnt + b2.cnt) for the same bucket
                duplicated_objects = int(duplicated_objects / 2)
            info = {
                'duplicated_objects': duplicated_objects,
                'duplicates_size': bucket_0_duplicates_size
            }
            if bucket_0_monthly_cost is not None:
                info.update({
                    'monthly_savings': self._calculate_monthly_savings(
                        bucket_0_duplicates_size, bucket_0_size,
                        bucket_0_monthly_cost)
                })
            cross_matrix[bucket_0][bucket_1] = info

        # fill empty values
        bucket_pairs = list(combinations(buckets, PAIR))
        for b in buckets:
            bucket_pairs.append((b, b))
        for pair in bucket_pairs:
            for k in [
                'duplicated_objects', 'duplicates_size', 'monthly_savings'
            ]:
                bucket_0, bucket_1 = pair[:2]
                if k not in cross_matrix[bucket_0][bucket_1]:
                    cross_matrix[bucket_0][bucket_1][k] = 0
                if bucket_0 != bucket_1:
                    if k not in cross_matrix[bucket_1][bucket_0]:
                        cross_matrix[bucket_1][bucket_0][k] = 0
        LOG.info(f"Cross matrix {cross_matrix}")
        return cross_matrix

    def _calculate_objects_with_duplicates(
        self, gemini_id: str, buckets: list[str], buckets_stats: dict
    ) -> dict:
        """
        A query to get duplicated objects across all bucket with some aggregation.
        It shows how many duplicated objects exist either in the same or other buckets.
        Example for ["bucket_1", "bucket_2", "bucket_3"]

        Query: SELECT groupArray(bucket), count(bucket), count(distinct bucket), size
               FROM gemini
               WHERE id='1' AND tag in
                    (
                        SELECT tag
                        FROM gemini
                        WHERE id='1'
                        GROUP BY tag HAVING COUNT(tag) > 1
                    )
               GROUP BY tag, size

        Result: {
                    "bucket_1": { "objects_with_duplicates": 7,
                                  "objects_with_duplicates_size": 323123,
                                  "monthly_savings": 3312 },
                    "bucket_2": { "objects_with_duplicates": 0,
                                  "objects_with_duplicates_size": 0 },
                    "bucket_3": { "objects_with_duplicates": 1,
                                  "objects_with_duplicates_size": 11,
                                  "monthly_savings": 21 },
                }
        """

        result_q = self.clickhouse_client.query(
            """
            SELECT groupArray(bucket), count(bucket), count(distinct bucket), size
            FROM gemini
            WHERE id=%(gemini_id)s AND tag in
                (
                    SELECT tag
                    FROM gemini
                    WHERE id=%(gemini_id)s
                    GROUP BY tag HAVING COUNT(tag) > 1
                ) GROUP BY tag, size
            """,
            parameters={"gemini_id": gemini_id},
        )

        duplicates_stats = {}

        for bucket in buckets:
            objects_with_duplicates = 0
            objects_with_duplicates_size = 0
            for r in result_q.result_rows:
                # If bucket is not in results (no duplicates anywhere), skip.
                bucket_occurance = r[0].count(bucket)
                if bucket_occurance == 0:
                    continue

                # If there is only 1 bucket, this is a self-duplicates case.
                # Number of objects equals the number of all items in the bucket.
                # Size is calculated for all items, except for one.
                if r[2] == 1:
                    objects_with_duplicates += r[1]
                    objects_with_duplicates_size += (r[1] - 1) * r[3]

                # Cross-duplicates case.
                # Number of objects equals the number of bucket occurances.
                # Size is calculated for all the items.
                if r[2] > 1:
                    objects_with_duplicates += bucket_occurance
                    objects_with_duplicates_size += bucket_occurance * r[3]

            size = buckets_stats.get(bucket, {}).get("size", 0)
            monthly_cost = buckets_stats.get(bucket, {}).get("monthly_cost")

            duplicates_stats[bucket] = {
                "objects_with_duplicates": objects_with_duplicates,
                "objects_with_duplicates_size": objects_with_duplicates_size,
            }

            if monthly_cost is not None:
                duplicates_stats[bucket][
                    "monthly_savings"
                ] = self._calculate_monthly_savings(
                    objects_with_duplicates_size,
                    size,
                    monthly_cost,
                )

        return duplicates_stats

    def process_task(self, body, message: Message):
        gemini_id = body.get("id")

        if not gemini_id:
            LOG.error(f"Invalid task body. gemini_id is missing: {body}")
            message.reject()
            return

        try:
            _, gemini = self.rest_client.gemini_get(gemini_id)
            status = gemini.get("status")
            org_id = gemini.get("organization_id")
            _, org = self.rest_client.organization_get(org_id)
            if org.get('disabled'):
                raise Exception(f"Organization {org_id} is disabled")

            if status not in self.valid_states:
                raise Exception(
                    f"Gemini {gemini['id']} in wrong status: {status}")
            if status == STATUS_SUCCESS:
                LOG.info(f"Found success Gemini {gemini['id']}")
                return
            last_run = self.get_now_timestamp()

            self._set_status(gemini_id, {"last_run": last_run}, "RUNNING")

            filters = gemini.get("filters", {})

            buckets = filters.get("buckets", [])

            data = []
            all_bucket_names = []

            cloud_account_ids = list(
                set([bucket.get("cloud_account_id") for bucket in buckets])
            )

            for cloud_account_id in cloud_account_ids:
                _, cloud_account = self.rest_client.cloud_account_get(
                    cloud_account_id)
                cloud_account.update(cloud_account['config'])
                target_bucket_names = list(
                    set(
                        [
                            bucket.get("name")
                            for bucket in buckets
                            if bucket.get("cloud_account_id") == cloud_account_id
                        ]
                    )
                )

                data.append((cloud_account, target_bucket_names))
                all_bucket_names += target_bucket_names

            duplicates, stats = Factory.get(data, filters)
            column_names = ["id", "tag", "bucket", "key", "size"]

            self.clickhouse_client.insert(
                "gemini",
                [
                    [
                        gemini_id,
                        duplicate.tag,
                        duplicate.bucket,
                        duplicate.key,
                        duplicate.size,
                    ]
                    for duplicate in duplicates
                ],
                column_names=column_names
            )

            buckets_stats, monthly_savings = self._calculate_buckets_stats(
                all_bucket_names, cloud_account_ids, stats, last_run
            )

            matrix = self._calculate_cross_matrix(
                gemini_id, all_bucket_names, buckets_stats)

            duplicates_stats = self._calculate_objects_with_duplicates(
                gemini_id, all_bucket_names, buckets_stats
            )

            updated_bucket_stats = buckets_stats
            for key in duplicates_stats.keys():
                updated_bucket_stats[key].update(duplicates_stats[key])

            LOG.info(f"Final matrix {matrix}")

            self._update_stats(
                gemini, stats, matrix, updated_bucket_stats, monthly_savings
            )

            self._set_status(
                gemini_id, {
                    "last_completed": self.get_now_timestamp()}, STATUS_SUCCESS)

            LOG.info(f"Successful gemini run for {gemini_id}")

        except Exception as exc:
            LOG.exception(f"Failed gemini run for {gemini_id}: {exc}")
            self._set_status(gemini_id, {"last_error": str(exc)}, "FAILED")
        finally:
            message.ack()


def run(config_client: ConfigClient) -> None:
    conn_str = "amqp://{user}:{pass}@{host}:{port}".format(
        **config_client.read_branch("/rabbit")
    )
    with Connection(conn_str) as conn:
        try:
            migrator = Migrator(config_client)
            with EtcdLock(config_client, "gemini_migrations"):
                migrator.migrate()

            worker = Worker(conn, config_client)
            LOG.info("Starting to consume...")
            worker.run()
        except KeyboardInterrupt:
            LOG.info("Interrupted by user")


if __name__ == "__main__":
    setup_logging(loglevel="INFO", loggers=[""])

    config_client = ConfigClient(
        host=os.environ.get("HX_ETCD_HOST", DEFAULT_ETCD_HOST),
        port=int(os.environ.get("HX_ETCD_PORT", DEFAULT_ETCD_PORT)),
    )
    config_client.wait_configured()
    run(config_client)
