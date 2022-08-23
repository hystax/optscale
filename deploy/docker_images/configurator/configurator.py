import logging
import os
import sys
import time

import pika
import pika.exceptions
import yaml
import etcd
from config_client.client import Client as EtcdClient
from retrying import retry
from sqlalchemy import create_engine
from pymongo import MongoClient
from influxdb import InfluxDBClient

LOG = logging.getLogger(__name__)

RETRY_ARGS = dict(stop_max_attempt_number=300, wait_fixed=500)
RABBIT_PRECONDIFITON_FAILED_CODE = 406


class Configurator(object):
    def __init__(self, config_path='config.yml', host='etcd', port=2379):
        self.config = yaml.load(open(config_path, 'r'))
        self.etcd_cl = EtcdClient(host=host, port=port)
        config = self.config['etcd']

        conn_str = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}'
        self.engine = create_engine(conn_str.format(
            user=config['restdb']['user'],
            password=config['restdb']['password'],
            host=config['restdb']['host'],
            port=config['restdb']['port'])
        )
        self.mongo_client = MongoClient("mongodb://%s:%s@%s:%s" % (
            config['mongo']['user'], config['mongo']['pass'],
            config['mongo']['host'], config['mongo']['port']
        ))

        rabbit_config = config['rabbit']
        credentials = pika.PlainCredentials(rabbit_config['user'],
                                            rabbit_config['pass'])
        rabbit_connection_parameters = pika.ConnectionParameters(
            host=rabbit_config['host'],
            port=int(rabbit_config['port']),
            credentials=credentials,
            connection_attempts=100,
            retry_delay=2
        )
        self.rabbit_client = pika.BlockingConnection(
            rabbit_connection_parameters)
        self.influx_client = InfluxDBClient(
            config['influxdb']['host'],
            config['influxdb']['port'],
            config['influxdb']['user'],
            config['influxdb']['pass'],
            config['influxdb']['database'],
        )

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_influx(self):
        self.influx_client.create_database(
            self.config['etcd']['influxdb']['database'])

    def commit_config(self):
        LOG.info("Creating /configured key")
        self.etcd_cl.write('/configured', time.time())

    def pre_configure(self):
        LOG.info("Creating databases")
        self.create_databases()
        self.configure_influx()
        # setting to 0 to block updates until update is finished
        # and new images pushed into registry
        self.etcd_cl.write('/registry_ready', 0)

        config = self.config.get('etcd')
        if self.config.get('skip_config_update', False):
            LOG.info('Only making structure updates')
            self.etcd_cl.update_structure('/', config, always_update=[
                '/cloud_agent_services',
                '/cluster_capabilities/supported_clouds',
                '/cluster_capabilities/common/acura_version',
            ])
            self.commit_config()
            return
        LOG.info("Writing default etcd keys")
        try:
            self.etcd_cl.delete('/logstash_host')
        except etcd.EtcdKeyNotFound:
            pass
        self.etcd_cl.write_branch('/', config, overwrite_lists=True)
        LOG.info("Configuring database server")
        self.configure_databases()
        self.configure_mongo()
        self.configure_rabbit()

        self.commit_config()

    def _declare_events_queue(self, channel):
        LOG.info('declaring queue')
        channel.queue_declare(
            self.config['etcd']['events_queue'], durable=True
        )

    def configure_rabbit(self):
        channel = self.rabbit_client.channel()
        try:
            self._declare_events_queue(channel)
        except pika.exceptions.ChannelClosed as e:
            if e.args and e.args[0] == RABBIT_PRECONDIFITON_FAILED_CODE:
                LOG.info(
                    'failed to declare queue - %s. Deleting existing queue', e)
                channel = self.rabbit_client.channel()
                channel.queue_delete(self.config['etcd']['events_queue'])
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
        _ = self.mongo_client[self.config['etcd']['mongo']['database']]

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def configure_databases(self):
        # in case of foreman model changes recreate db
        if self.config.get('drop_tasks_db'):
            self.engine.execute("DROP DATABASE IF EXISTS tasks")

    @retry(**RETRY_ARGS, retry_on_exception=lambda x: True)
    def create_databases(self):
        for db in self.config.get('databases'):
            # heat migrations fail with utf8mb4
            if db != 'heat':
                # http://dev.mysql.com/doc/refman/5.6/en/innodb-row-format-dynamic.html NOQA
                self.engine.execute(
                    "CREATE DATABASE IF NOT EXISTS `{0}` "
                    "DEFAULT CHARACTER SET `utf8mb4` "
                    "DEFAULT COLLATE `utf8mb4_unicode_ci`".format(db))
            else:
                self.engine.execute(
                    'CREATE DATABASE IF NOT EXISTS `{0}`'.format(db))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    etcd_host = os.environ.get('HX_ETCD_HOST')
    etcd_port = int(os.environ.get('HX_ETCD_PORT'))
    if len(sys.argv) > 1:
        conf = Configurator(sys.argv[1], host=etcd_host, port=etcd_port)
    else:
        conf = Configurator(host=etcd_host, port=etcd_port)
    stage = os.environ.get('HX_CONFIG_STAGE')
    conf.pre_configure()
