import os
import logging
from itertools import combinations
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from kombu import Connection, Exchange, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging
from duplicate_object_finder.factory import Factory
from etcd import Lock as EtcdLock
from clickhouse_driver import Client as ClickHouseClient
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
            user, password, host, _ = self.config_client.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=DB_NAME, user=user
            )
        return self._clickhouse_client

    @property
    def mongo_client(self) -> MongoClient:
        if self._mongo_client is None:
            mongo_params = self.config_client.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def valid_states(self):
        return ["QUEUED"]

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

    def _calculate_self_matrix(
        self, gemini_id: str, buckets: list[str], buckets_stats: dict
    ) -> dict:
        """
        Combined query to get duplicated objects within each bucket, resulted in a dictionary matrix.
        Example for ["bucket_1", "bucket_2"]:

        Query:  SELECT bucket, count, size * (1 - 1/count) FROM
                (
                    SELECT bucket, tag, count(id) count, sum(size) size
                    FROM gemini WHERE id="1" AND bucket = "bucket_1"
                    GROUP BY bucket, tag
                    HAVING count > 1

                    UNION ALL

                    SELECT bucket, tag, count(id) count, sum(size) size
                    FROM gemini WHERE id="1" AND bucket = "bucket_2"
                    GROUP BY bucket, tag
                    HAVING count > 1
                )
        Result: {
                    "bucket_1": {
                        "bucket_1": {
                            "duplicated_objects": 3,
                            "duplicates_size": 142458.0,
                            "monthly_savings": 5551
                        }
                    },
                    "bucket_2": {
                        "bucket_2": {
                            "duplicated_objects": 0,
                            "duplicates_size": 0
                        }
                    }
                }
        """
        self_query = ""
        params = {"gemini_id": gemini_id}

        for index, bucket in enumerate(buckets):
            params[bucket] = bucket
            self_query += f"""
                SELECT bucket, tag, count(id) count, sum(size) size
                FROM gemini
                WHERE id=%(gemini_id)s AND bucket=%({bucket})s
                GROUP BY bucket, tag
                HAVING count > 1
            """
            if index < len(buckets) - 1:
                self_query += " UNION ALL "

        self_result = self.clickhouse_client.execute(
            f"SELECT bucket, count, size * (1 - 1/count) FROM ({self_query})",
            params=params,
        )

        self_matrix = {}

        for bucket in buckets:
            if self_matrix.get(bucket) is None:
                self_matrix[bucket] = {
                    bucket: {"duplicated_objects": 0, "duplicates_size": 0}
                }

            for row in self_result:
                if bucket in row:
                    self_matrix[bucket][bucket]["duplicated_objects"] += row[1]
                    self_matrix[bucket][bucket]["duplicates_size"] += row[2]

            size = buckets_stats.get(bucket, {}).get("size", 0)
            monthly_cost = buckets_stats.get(bucket, {}).get("monthly_cost")

            if monthly_cost is not None:
                self_matrix[bucket][bucket][
                    "monthly_savings"
                ] = self._calculate_monthly_savings(
                    self_matrix[bucket][bucket]["duplicates_size"], size, monthly_cost
                )

        LOG.info(f"Self matrix: {self_matrix}")
        return self_matrix

    def _calculate_cross_matrix(
        self, gemini_id: str, buckets: list[str], buckets_stats: dict
    ) -> dict:
        """
        A query to get duplicated objects across bucket pairs, resulted in a dictionary matrix.
        Example for ["bucket_1", "bucket_2", "bucket_3"]:

        Query: SELECT index, sum(count) count, size * (1 - 1/count) FROM
               (
                    SELECT 0 index, tag, count(id) count, sum(size) size
                    FROM gemini
                    WHERE id="1" AND bucket IN ["bucket_1", "bucket_2"] AND tag in
                    (
                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_1"

                        INTERSECT

                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_2"
                    ) GROUP BY tag

                    UNION ALL

                    SELECT 1 index, tag, count(id) count, sum(size) size
                    FROM gemini
                    WHERE id="1" AND bucket IN ["bucket_2", "bucket_3"] AND tag in
                    (
                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_2"

                        INTERSECT

                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_3"
                    ) GROUP BY tag

                    UNION ALL

                    SELECT 2 index, tag, count(id) count, sum(size) size
                    FROM gemini
                    WHERE id="1" AND bucket IN ["bucket_3", "bucket_1"] AND tag in
                    (
                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_3"

                        INTERSECT

                        SELECT tag
                        FROM gemini
                        WHERE id="1" AND bucket="bucket_1"
                    ) GROUP BY tag
                ) GROUP BY index, size ORDER BY index

        Result: {
                    "bucket_1": {
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
                        "bucket_3": {"duplicated_objects": 0, "duplicates_size": 0},
                    },
                    "bucket_3": {
                        "bucket_1": {"duplicated_objects": 0, "duplicates_size": 0},
                        "bucket_3": {"duplicated_objects": 0, "duplicates_size": 0},
                    }
                }
        """

        bucket_pairs = list(combinations(buckets, PAIR))
        cross_query = ""
        params = {"gemini_id": gemini_id}

        for index, pair in enumerate(bucket_pairs):
            params[str(index)] = pair
            params[pair[0]] = pair[0]
            params[pair[1]] = pair[1]

            cross_query += f"""
                SELECT {index} index, tag, bucket, count(id) count, sum(size) size
                FROM gemini
                WHERE id=%(gemini_id)s AND bucket IN %({index})s AND tag in (
                    SELECT tag
                    FROM gemini
                    WHERE id=%(gemini_id)s AND bucket=%({pair[0]})s

                    INTERSECT

                    SELECT tag
                    FROM gemini
                    WHERE id=%(gemini_id)s AND bucket=%({pair[1]})s
                ) GROUP BY tag, bucket
                """

            if index < len(bucket_pairs) - 1:
                cross_query += " UNION ALL "

        cross_result = self.clickhouse_client.execute(
            f"""
                SELECT index, bucket, sum(count) count, size FROM ({cross_query})
                GROUP BY index, bucket, size ORDER BY index
            """,
            params=params,
            # Query-level paramters to set the values to unlimited.
            # The query body exceeds the default limits if there are a lot of
            # buckets.
            settings={"max_query_size": 0, "max_ast_elements": 0},
        )

        cross_matrix = defaultdict(lambda: defaultdict(dict))

        for index, pair in enumerate(bucket_pairs):
            bucket_0 = pair[0]
            bucket_1 = pair[1]
            duplicated_objects = 0
            bucket_0_duplicates_size = 0
            bucket_1_duplicates_size = 0

            filtered_cross_result = [
                item for item in cross_result if item[0] == index]

            if filtered_cross_result:
                for item in filtered_cross_result:
                    duplicated_objects += item[2]
                    if item[1] == bucket_0:
                        bucket_0_duplicates_size += item[3]
                    if item[1] == bucket_1:
                        bucket_1_duplicates_size += item[3]

            cross_matrix[bucket_0][bucket_1]["duplicated_objects"] = duplicated_objects
            cross_matrix[bucket_0][bucket_1][
                "duplicates_size"
            ] = bucket_0_duplicates_size
            cross_matrix[bucket_1][bucket_0]["duplicated_objects"] = duplicated_objects
            cross_matrix[bucket_1][bucket_0][
                "duplicates_size"
            ] = bucket_1_duplicates_size

            bucket_0_size = buckets_stats.get(bucket_0, {}).get("size", 0)
            bucket_0_monthly_cost = buckets_stats.get(
                bucket_0, {}).get("monthly_cost")
            bucket_1_size = buckets_stats.get(bucket_1, {}).get("size", 0)
            bucket_1_monthly_cost = buckets_stats.get(
                bucket_1, {}).get("monthly_cost")

            if bucket_0_monthly_cost is not None:
                cross_matrix[bucket_0][bucket_1][
                    "monthly_savings"
                ] = self._calculate_monthly_savings(
                    bucket_0_duplicates_size,
                    bucket_0_size,
                    bucket_0_monthly_cost,
                )

            if bucket_1_monthly_cost is not None:
                cross_matrix[bucket_1][bucket_0][
                    "monthly_savings"
                ] = self._calculate_monthly_savings(
                    bucket_1_duplicates_size,
                    bucket_1_size,
                    bucket_1_monthly_cost,
                )

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

        result = self.clickhouse_client.execute(
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
            params={"gemini_id": gemini_id},
        )

        duplicates_stats = {}

        for bucket in buckets:
            objects_with_duplicates = 0
            objects_with_duplicates_size = 0
            for r in result:
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

            if status not in self.valid_states:
                raise Exception(
                    f"Gemini {gemini['id']} in wrong status: {status}")

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
                config = cloud_account.get("config", {})
                target_bucket_names = list(
                    set(
                        [
                            bucket.get("name")
                            for bucket in buckets
                            if bucket.get("cloud_account_id") == cloud_account_id
                        ]
                    )
                )

                data.append((config, target_bucket_names))
                all_bucket_names += target_bucket_names

            duplicates, stats = Factory.get(data, filters)

            self.clickhouse_client.execute(
                """INSERT INTO gemini VALUES""",
                [
                    (
                        gemini_id,
                        duplicate.tag,
                        duplicate.bucket,
                        duplicate.key,
                        duplicate.size,
                    )
                    for duplicate in duplicates
                ],
            )

            buckets_stats, monthly_savings = self._calculate_buckets_stats(
                all_bucket_names, cloud_account_ids, stats, last_run
            )

            self_matrix = self._calculate_self_matrix(
                gemini_id, all_bucket_names, buckets_stats
            )
            matrix = self_matrix

            # Skip cross matrix if there is just one bucket
            if len(buckets) > 1:
                cross_matrix = self._calculate_cross_matrix(
                    gemini_id, all_bucket_names, buckets_stats
                )
                for key in self_matrix.keys():
                    matrix[key].update(cross_matrix[key])

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
                    "last_completed": self.get_now_timestamp()}, "SUCCESS")

            LOG.info(f"Successful gemini run for {gemini_id}")

        except Exception as exc:
            LOG.exception(f"Failed gemini run for {gemini_id}: {ex}")
            self._set_status(gemini_id, {"last_error": str(ex)}, "FAILED")
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
