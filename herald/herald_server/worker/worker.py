import os
import logging
import argparse

import config_client.client

from herald_server.controllers.message_consumer import Consumer
from herald_server.models.db_factory import DBFactory, DBType
from herald_server.processors.main import MainProcessor

LOG = logging.getLogger(__name__)

DEFAULT_ETCD_HOST = '127.0.0.1'
DEFAULT_ETCD_PORT = 2379


def make_app(etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    rabbit_user, rabbit_pass, rabbit_host, rabbit_port = \
        config_cl.rabbit_params()

    events_queue = config_cl.events_queue()
    consumer = Consumer(
        events_queue, rabbit_host, rabbit_port, rabbit_user, rabbit_pass)

    db = DBFactory(DBType.MySQL, config_cl).db
    engine = db.engine

    tasks_processor = MainProcessor(consumer, engine, config_cl)

    config_cl.tell_everybody_that_i_am_ready()

    consumer.run(tasks_processor.process_task)


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()
    make_app(args.etcdhost, args.etcdport, wait=False)


if __name__ == "__main__":
    main()
