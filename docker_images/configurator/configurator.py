import argparse
import logging
import os
import time
from retrying import retry

import pika
import pika.exceptions
import yaml
import etcd
import boto3
from boto3.session import Config as BotoConfig
from sqlalchemy import create_engine
from pymongo import MongoClient
from influxdb import InfluxDBClient
from optscale_client.config_client.client import Client as EtcdClient


ETCD_KEYS_TO_DELETE = [
    "/logstash_host",
    "/optscale_meter_enabled",
    "/opentelemetry",
]
RETRY_ARGS = dict(stop_max_attempt_number=300, wait_fixed=500)
RABBIT_PRECONDIFITON_FAILED_CODE = 406

CH_HTTP_PORT = 8123
CH_LOCAL_NAME = "clickhouse"
logger = logging.getLogger(__name__)


class Configurator(object):
    def __init__(self, config_path: str, host="etcd", port=2379):
        self.config = yaml.safe_load(open(config_path, "r"))
        self.etcd_cl = EtcdClient(host=host, port=port)
        config = self.config["etcd"]

        conn_str = "mysql+mysqlconnector://{user}:{password}@{host}:{port}"
        self.engine = create_engine(
            conn_str.format(
                user=config["restdb"]["user"],
                password=config["restdb"]["password"],
                host=config["restdb"]["host"],
                port=config["restdb"]["port"],
            )
        )
        if "url" in config["mongo"]:
            mongo_url = config["mongo"]["url"]
        else:
            mongo_url = "mongodb://%s:%s@%s:%s" % (
                config["mongo"]["user"],
                config["mongo"]["pass"],
                config["mongo"]["host"],
                config["mongo"]["port"],
            )
        self.mongo_client = MongoClient(mongo_url)

        rabbit_config = config["rabbit"]
        credentials = pika.PlainCredentials(
            rabbit_config["user"], rabbit_config["pass"]
        )
        rabbit_connection_parameters = pika.ConnectionParameters(
            host=rabbit_config["host"],
            port=int(rabbit_config["port"]),
            credentials=credentials,
            connection_attempts=100,
            retry_delay=2,
        )
        self.rabbit_client = pika.BlockingConnection(rabbit_connection_parameters)
        self.influx_client = InfluxDBClient(
            config["influxdb"]["host"],
            config["influxdb"]["port"],
            config["influxdb"]["user"],
            config["influxdb"]["pass"],
            config["influxdb"]["database"],
        )
        s3_params = config["minio"]
        self.s3_client = boto3.client(
            "s3",
            endpoint_url="http://{}:{}".format(s3_params["host"], s3_params["port"]),
            aws_access_key_id=s3_params["access"],
            aws_secret_access_key=s3_params["secret"],
            config=BotoConfig(s3={"addressing_style": "path"}),
        )

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_influx(self):
        self.influx_client.create_database(self.config["etcd"]["influxdb"]["database"])

    def stitch_ch_to_http(self):
        try:
            ch_host = self.etcd_cl.get("/clickhouse/host").value
            ch_port = self.etcd_cl.get("/clickhouse/port").value
            # switch to http port only for local host
            logger.info("Ch host: %s", ch_host)
            logger.info("Ch port: %s", ch_port)
            if ch_host == CH_LOCAL_NAME and str(ch_port) != str(CH_HTTP_PORT):
                logger.info("Updating clickhouse port to %s", CH_HTTP_PORT)
                self.etcd_cl.write("/clickhouse/port", CH_HTTP_PORT)
        except etcd.EtcdKeyNotFound:
            logger.info("Skipping update ch port due to missing key")

    def commit_config(self):
        logger.info("Creating /configured key")
        self.etcd_cl.write("/configured", time.time())

    def pre_configure(self):
        logger.info("Creating databases")
        self.create_databases()
        logger.debug("Databases created.")
        logger.debug("Creating InfluxDB databases.")
        self.configure_influx()
        logger.debug("InfluxDB databases created.")
        logger.debug("Configuring ClickHouse databases")
        self.stitch_ch_to_http()
        logger.debug("ClickHouse databases created.")
        logger.debug("Creating Thanos.")
        self.configure_thanos()
        logger.debug("Thanos created.")
        self.configure_gemini()
        logger.debug("Gemini created.")
        # setting to 0 to block updates until update is finished
        # and new images pushed into registry
        logger.debug("Writing etc /registry_ready.")
        self.etcd_cl.write("/registry_ready", 0)
        logger.debug("etc /registry_ready wrote.")
        config = self.config.get("etcd")
        if self.config.get("skip_config_update", False):
            logger.info("Only making structure updates.")
            logger.debug("Updating etcd structure.")
            self.etcd_cl.update_structure("/", config)
            logger.debug("etcd structure updated.")
            logger.debug("Committing conf.")
            self.commit_config()
            return
        logger.info("Writing default etcd keys")
        for key in ETCD_KEYS_TO_DELETE:
            try:
                logger.debug("Deleting key %s from etc", key)
                self.etcd_cl.delete(key)
            except etcd.EtcdNotFile:
                try:
                    self.etcd_cl.delete(key, recursive=True, dir=True)
                except etcd.EtcdKeyNotFound:
                    pass
            except etcd.EtcdKeyNotFound:
                pass
        self.etcd_cl.write_branch("/", config, overwrite_lists=True)
        logger.info("Configuring database server")
        self.configure_databases()
        logger.debug("Databases configured.")
        logger.debug("Configuring auth salt")
        self.configure_auth_salt()
        logger.debug("Auth salt configured.")
        logger.debug("Configuring mongo.")
        self.configure_mongo()
        logger.debug("Mongo configured.")
        logger.debug("Configuring RabbitMQ.")
        self.configure_rabbit()
        logger.debug("RabbitMQ configured.")
        logger.debug("Committing conf.")
        self.commit_config()
        logger.debug("Configuration completed.")

    def _create_auth_salt_key(self):
        salt = ""
        try:
            salt = self.etcd_cl.encryption_salt()
        except etcd.EtcdKeyNotFound:
            pass
        self.etcd_cl.write("/encryption_salt_auth", salt)

    def configure_auth_salt(self):
        try:
            auth_salt = self.etcd_cl.encryption_salt_auth()
            if not auth_salt:
                self._create_auth_salt_key()
        except etcd.EtcdKeyNotFound:
            self._create_auth_salt_key()

    def _declare_events_queue(self, channel):
        logger.info("declaring queue")
        channel.queue_declare(self.config["etcd"]["events_queue"], durable=True)

    def configure_rabbit(self):
        channel = self.rabbit_client.channel()
        try:
            self._declare_events_queue(channel)
        except pika.exceptions.ChannelClosed as e:
            if e.args and e.args[0] == RABBIT_PRECONDIFITON_FAILED_CODE:
                logger.info("failed to declare queue - %s. Deleting existing queue", e)
                channel = self.rabbit_client.channel()
                channel.queue_delete(self.config["etcd"]["events_queue"])
                self._declare_events_queue(channel)
            else:
                raise

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_mongo(self):
        """
        according to pymongo documentation it's getting
        (creating if not exists) database
        http://api.mongodb.com/python/current/tutorial.html#getting-a-database
        :return:
        """
        _ = self.mongo_client[self.config["etcd"]["mongo"]["database"]]

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_databases(self):
        # in case of foreman model changes recreate db
        if self.config.get("drop_tasks_db"):
            self.engine.execute("DROP DATABASE IF EXISTS tasks")

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def create_databases(self):
        for db in self.config.get("databases"):
            # heat migrations fail with utf8mb4
            if db != "heat":
                # http://dev.mysql.com/doc/refman/5.6/en/innodb-row-format-dynamic.html NOQA
                self.engine.execute(
                    "CREATE DATABASE IF NOT EXISTS `{0}` "
                    "DEFAULT CHARACTER SET `utf8mb4` "
                    "DEFAULT COLLATE `utf8mb4_unicode_ci`".format(db)
                )
            else:
                self.engine.execute("CREATE DATABASE IF NOT EXISTS `{0}`".format(db))

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_thanos(self):
        bucket_name = "thanos"
        prefix = "data"
        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            logger.info("Created %s bucket in minio", bucket_name)
            self.s3_client.put_object(Bucket=bucket_name, Body="", Key="%s/" % prefix)
            logger.info("Created %s folder in %s bucket", prefix, bucket_name)
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.info(
                "Skipping bucket %s creation. Bucket already exists", bucket_name
            )

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_gemini(self):
        bucket_name = "gemini"
        prefix = "data"
        try:
            self.s3_client.create_bucket(Bucket=bucket_name)
            logger.info("Created %s bucket in minio", bucket_name)
        except self.s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.info("Skipping bucket %s creation. "
                        "Bucket already exists", bucket_name)
        lifecycle_config = {
            "Rules": [
                {
                    "ID": f"retention-1-day",
                    "Status": "Enabled",
                    "Filter": {
                        "Prefix": f"{prefix}/"
                    },
                    "Expiration": {"Days": 1},
                }
            ]
        }
        self.s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_config,
        )
        logger.info('Gemini bucket lifecycle configuration updated')


if __name__ == "__main__":
    etcd_host = os.environ.get("HX_ETCD_HOST")
    etcd_port = int(os.environ.get("HX_ETCD_PORT"))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_path",
        nargs="?",
        default="config.yml",
        help="Path to the configuration file (default: config.yml)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=[
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "debug",
            "info",
            "warning",
            "error",
        ],
        help="Set logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-format",
        default="%(levelname)s:%(name)s:%(message)s",
        help="Logging format string (default: %(levelname)s:%(name)s:%(message)s",
    )

    args = parser.parse_args()
    numeric_level = getattr(logging, args.log_level.upper())
    logger.setLevel(numeric_level)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            fmt=args.log_format, datefmt="%Y-%m-%d %H:%M:%S:%z"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    log_level = args.log_level.upper()

    conf = Configurator(config_path=args.config_path, host=etcd_host, port=etcd_port)
    stage = os.environ.get("HX_CONFIG_STAGE")
    logger.info(
        f"Starting Configurator with config: {args.config_path} and loglevel: {log_level}"
    )
    conf.pre_configure()
