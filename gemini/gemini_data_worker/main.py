import os
import logging
import csv
import io
from datetime import datetime, timezone, timedelta
from kombu import Connection, Exchange, Queue, Message
from kombu.mixins import ConsumerMixin
from kombu.utils.debug import setup_logging
import boto3
from boto3.session import Config as BotoConfig
import clickhouse_connect
from clickhouse_connect.driver.httpclient import HttpClient as ClickHouseClient
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

DB_NAME = "gemini"
EXCHANGE_NAME = "gemini-tasks"
QUEUE_NAME = "gemini-data"
TASK_EXCHANGE = Exchange(EXCHANGE_NAME, type="direct")
TASK_QUEUE = Queue(QUEUE_NAME, TASK_EXCHANGE, routing_key=QUEUE_NAME)
DEFAULT_ETCD_HOST = "etcd"
DEFAULT_ETCD_PORT = 80
STATUS_SUCCESS = "SUCCESS"
STATUS_QUEUED = "QUEUED"
STATUS_FAILED = "FAILED"
STATUS_RUNNING = "RUNNING"
BUCKET_NAME = "gemini"
PREFIX = "data"
URL_LIFETIME_SECONDS = 24 * 60 * 60

LOG = logging.getLogger(__name__)


class IteratorIO(io.RawIOBase):
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = b""
        self.stream_ended = False

    def readable(self):
        return True

    def read(self, size=-1):
        if self.stream_ended:
            return b""
        while size < 0 or len(self.buffer) < size:
            try:
                self.buffer += next(self.iterator)
            except StopIteration:
                self.stream_ended = True
                break
        if size < 0:
            result, self.buffer = self.buffer, b""
        else:
            result, self.buffer = self.buffer[:size], self.buffer[size:]
        return result


class Worker(ConsumerMixin):
    def __init__(self, connection, config_client):
        self.connection = connection
        self.config_client = config_client
        self._rest_client = None
        self._clickhouse_client = None
        self._s3_client = None

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

    @staticmethod
    def get_now_timestamp() -> int:
        return int(datetime.now(tz=timezone.utc).timestamp())

    @property
    def s3_client(self):
        if self._s3_client is None:
            s3_params = self.config_client.read_branch('/minio')
            self._s3_client = boto3.client(
                's3',
                endpoint_url=f'http://{s3_params['host']}:{s3_params['port']}',
                aws_access_key_id=s3_params['access'],
                aws_secret_access_key=s3_params['secret'],
                config=BotoConfig(s3={'addressing_style': 'path'})
            )
        return self._s3_client

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=[TASK_QUEUE],
                accept=["json"],
                callbacks=[self.process_task],
                prefetch_count=10,
            )
        ]

    def _set_status(self, gemini_data_id: str, status: str) -> None:
        body = {"status": status}
        try:
            self.rest_client.geminis_data_update(gemini_data_id, body)
            LOG.info(f"Status updated to {status} for gemini data {gemini_data_id}")
        except Exception as exc:
            LOG.error(f"Not able to update status to {status} for gemini data"
                      f" {gemini_data_id}: {exc}")

    @staticmethod
    def csv_generator(stream, header):
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(header)
        yield buffer.getvalue().encode("utf-8")
        buffer.seek(0)
        buffer.truncate(0)
        for row in stream:
            writer.writerow(row)
            yield buffer.getvalue().encode("utf-8")
            buffer.seek(0)
            buffer.truncate(0)

    def upload_csv_stream(self, stream_context, bucket_name, object_name):
        with stream_context as stream:
            csv_iter = self.csv_generator(
                stream,
                ["tag", "bucket", "key", "size"]
            )
            fileobj = IteratorIO(csv_iter)
            self.s3_client.upload_fileobj(
                Fileobj=fileobj,
                Bucket=bucket_name,
                Key=object_name,
                ExtraArgs={"ContentType": "text/csv"},
            )

    def generate_presigned_url(self, bucket_name, object_path):
        url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_path
            },
            ExpiresIn=URL_LIFETIME_SECONDS
        )
        return url

    def delete_file(self, bucket_name, object_path):
        self.s3_client.delete_object(Bucket=bucket_name, Key=object_path)

    def _calculate(self, gemini_id, buckets: list):
        unique_buckets = list(set(buckets))
        unique_buckets_length = len(unique_buckets)

        # The endpoint is intended to download duplicated records
        # for 1 (self duplicates) or 2 (cross duplicates) buckets
        if unique_buckets_length == 1:
            return self.clickhouse_client.query_rows_stream("""
                SELECT tag, bucket, key, size
                FROM gemini
                WHERE id=%(gemini_id)s
                  AND bucket=%(bucket)s
                  AND tag IN (
                    SELECT tag
                    FROM gemini
                    WHERE id=%(gemini_id)s
                      AND bucket=%(bucket)s
                    GROUP BY tag
                    HAVING COUNT (tag) > 1
                    )
            """, parameters={
                "gemini_id": gemini_id, "bucket": unique_buckets[0]
            })
        return self.clickhouse_client.query_rows_stream("""
            SELECT tag, bucket, key, size
            FROM gemini
            WHERE id = %(gemini_id)s
              AND bucket IN %(buckets)s
              AND tag IN (
                SELECT tag
                FROM gemini
                WHERE id = %(gemini_id)s
              AND bucket IN (%(bucket_1)s , %(bucket_2)s)
                GROUP BY tag
                HAVING COUNT (DISTINCT bucket) = 2
                )
        """, parameters={
            "gemini_id": gemini_id,
            "buckets": unique_buckets,
            "bucket_1": unique_buckets[0],
            "bucket_2": unique_buckets[1],
        })

    def process_task(self, body, message: Message):
        file_created = None
        gemini_data_id = body.get("gemini_data_id")
        try:
            if not gemini_data_id:
                LOG.error(
                    f"Invalid task body. gemini_data_id is missing: {body}")
                message.reject()
                return
            _, gemini_data = self.rest_client.geminis_data_get(gemini_data_id)
            status = gemini_data.get("status")
            if status not in [STATUS_SUCCESS, STATUS_QUEUED]:
                raise Exception(
                    f"Gemini data {gemini_data_id} in wrong status: {status}")
            if status == STATUS_SUCCESS:
                LOG.info(f"Found success Gemini data {gemini_data_id}")
                return
            self._set_status(gemini_data_id, STATUS_RUNNING)
            gemini_id = gemini_data.get("gemini_id")
            buckets_str = gemini_data.get("buckets")
            buckets = buckets_str.split(",") if buckets_str else []
            stream_context = self._calculate(gemini_id, buckets)
            object_path = f'{PREFIX}/{gemini_id},{buckets_str}.csv'
            self.upload_csv_stream(stream_context, BUCKET_NAME, object_path)
            file_created = object_path
            url = self.generate_presigned_url(BUCKET_NAME, object_path)
            valid_until = int((datetime.now(tz=timezone.utc) + timedelta(
                seconds=URL_LIFETIME_SECONDS)).timestamp())
            self.rest_client.geminis_data_update(gemini_data_id, {
                'status': STATUS_SUCCESS,
                'url': url,
                'valid_until': valid_until
            })
        except Exception as ex:
            LOG.error(f"Failed gemini data {gemini_data_id}: %s", str(ex))
            self._set_status(gemini_data_id, STATUS_FAILED)
            if file_created:
                self.delete_file(BUCKET_NAME, file_created)
        finally:
            message.ack()


def run(config_client: ConfigClient) -> None:
    conn_str = "amqp://{user}:{pass}@{host}:{port}".format(
        **config_client.read_branch("/rabbit")
    )
    with Connection(conn_str) as conn:
        try:
            worker = Worker(conn, config_client)
            LOG.info("Starting to consume...")
            worker.run()
        except KeyboardInterrupt:
            LOG.info("Shutdown received")


if __name__ == "__main__":
    setup_logging(loglevel="INFO", loggers=[""])

    config_client = ConfigClient(
        host=os.environ.get("HX_ETCD_HOST", DEFAULT_ETCD_HOST),
        port=int(os.environ.get("HX_ETCD_PORT", DEFAULT_ETCD_PORT)),
    )
    config_client.wait_configured()
    run(config_client)
