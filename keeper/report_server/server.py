import os
import logging
import argparse

import time
import tornado.ioloop
import tornado.web
from pymongo import MongoClient
from mongoengine import connect

import config_client.client
import report_server.handlers.v1 as h_v1
import report_server.handlers.v2 as h_v2

from report_server.handlers.v1.swagger import SwaggerStaticFileHandler
from report_server.constants import urls_v2
from report_server.controllers.message_publisher import Publisher
from report_server.handlers.v1.base import DefaultHandler


DEFAULT_PORT = 8973
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')


def get_handler_version(h_v, handler, default_version=h_v1):
    res = getattr(h_v, handler, None) or getattr(default_version, handler)
    return res


def get_handlers(handler_kwargs, version=None):
    result = []
    versions_map = {
        'v2': (urls_v2, h_v2)
    }
    if version:
        versions = [versions_map.get(version)]
    else:
        versions = [v for _, v in versions_map.items()]

    for urls, handlers in versions:
        result.extend([
            (urls.events, get_handler_version(
                handlers, "events"
            ).EventAsyncHandler, handler_kwargs),
            (urls.events_count, get_handler_version(
                handlers, "events"
            ).EventCountAsyncHandler, handler_kwargs),
            (urls.ack_event, get_handler_version(
                handlers, "events"
            ).EventAckAsyncHandler, handler_kwargs),
        ])

    # v2 only
    if not version or version == 'v2':
        result.extend([
            (urls_v2.feedbacks, h_v2.feedbacks.FeedbacksAsyncHandler,
             handler_kwargs)
        ])
    return result


def get_swagger_urls():
    return [
        (r'%s/swagger/(.*)' % urls_v2.url_prefix,
         SwaggerStaticFileHandler, {'path': SWAGGER_PATH}),
        (r"%s/?" % urls_v2.url_prefix, tornado.web.RedirectHandler,
         {"url": "%s/swagger/spec.html" % urls_v2.url_prefix}),
    ]


def make_app(etcd_host, etcd_port, wait=False, mongo_client_class=None):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()
    mongo_params = config_cl.mongo_params()
    mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
    mongo_client = MongoClient(mongo_conn_string)
    connection_params = {}
    if mongo_client_class:
        connection_params['mongo_client_class'] = mongo_client_class
    connect(
        host='%s/%s?authSource=admin' % (mongo_conn_string, mongo_params[-1]),
        **connection_params
    )

    rabbit_user, rabbit_pass, rabbit_host, rabbit_port = \
        config_cl.rabbit_params()
    events_queue = config_cl.events_queue()

    rabbit_client = Publisher(events_queue, rabbit_host, rabbit_port,
                              rabbit_user, rabbit_pass)

    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + .1,
                                                 rabbit_client.connect)

    config_cl.tell_everybody_that_i_am_ready()
    handler_kwargs = {
        "mongo_client": mongo_client,
        "config": config_cl,
        "rabbit_client": rabbit_client,
    }

    return tornado.web.Application(
        get_handlers(handler_kwargs) + get_swagger_urls(),
        default_handler_class=DefaultHandler)


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()

    app = make_app(args.etcdhost, args.etcdport, wait=True)
    LOG.info("start listening on port %d", DEFAULT_PORT)
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
