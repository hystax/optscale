import os
import logging
import argparse
import time
import tornado.ioloop
import tornado.web

import config_client.client
from herald_server.constants import urls_v1, urls_v2
from herald_server.handlers.v1.base import DefaultHandler
from herald_server.handlers.v1.notifications import (UserNotificationAsyncCollectionHandler,
                                                     NotificationAsyncItemHandler)
from herald_server.handlers.v2.emails import EmailAsyncHandler
from herald_server.models.db_factory import DBType, DBFactory
from herald_server.controllers.message_publisher import Publisher

DEFAULT_PORT = 8906
DEFAULT_ETCD_HOST = '127.0.0.1'
DEFAULT_ETCD_PORT = 2379

LOG = logging.getLogger(__name__)


def make_app(db_type, etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    db = DBFactory(db_type, config_cl).db
    db.create_schema()

    rabbit_user, rabbit_pass, rabbit_host, rabbit_port = \
        config_cl.rabbit_params()
    events_queue = config_cl.events_queue()

    rabbit_client = Publisher(events_queue, rabbit_host, rabbit_port,
                              rabbit_user, rabbit_pass)

    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + .1,
                                                 rabbit_client.connect)

    handler_kwargs = {
        "engine": db.engine,
        "config": config_cl,
        "rabbit_client": rabbit_client,
    }
    config_cl.tell_everybody_that_i_am_ready()
    return tornado.web.Application([
        (urls_v1.user_notification,
         UserNotificationAsyncCollectionHandler, handler_kwargs),
        (urls_v1.notifications,
         NotificationAsyncItemHandler, handler_kwargs),
        (urls_v2.email,
         EmailAsyncHandler, handler_kwargs)
    ], default_handler_class=DefaultHandler)


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()

    app = make_app(DBType.MySQL, args.etcdhost, args.etcdport, wait=True)
    LOG.info("start listening on port %d", DEFAULT_PORT)
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
