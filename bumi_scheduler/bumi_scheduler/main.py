import argparse
import logging
import os

import tornado.ioloop
import tornado.web

import config_client.client

from bumi_scheduler.controllers.schedule import ScheduleController


DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)


def get_scheduler_timeout(config_cl):
    return int(config_cl.get("/bumi_scheduler_timeout").value)


def setup_scheduler(config_cl):
    controller_kwargs = {
        "config": config_cl,
    }
    schedule_controller = ScheduleController(**controller_kwargs)

    callback_time_in_sec = get_scheduler_timeout(config_cl)
    app = tornado.ioloop.PeriodicCallback(
        schedule_controller.generate_tasks, callback_time_in_sec * 1000)

    config_cl.tell_everybody_that_i_am_ready()
    return app


def make_app(etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    return setup_scheduler(config_cl)


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()

    app = make_app(args.etcdhost, args.etcdport, wait=True)
    LOG.info("Starting periodic")
    app.start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
