import os
import logging
import argparse
import tornado.ioloop
import tornado.web
import config_client.client

from pharos_receiver.urls import urls_v2
import pharos_receiver.handlers.v2 as handlers


DEFAULT_PORT = 8946
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 2379

LOG = logging.getLogger(__name__)

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)


def get_handlers(handler_kwargs):
    # pylint: disable=E1101
    return [
        (urls_v2.log_bulk,
         handlers.bulks.LogsBulkHandler, handler_kwargs),
        (urls_v2.metrics,
         handlers.metrics.MetricsHandler, handler_kwargs),
        (urls_v2.ack,
         handlers.acks.AcksHandler, handler_kwargs),
        (urls_v2.heartbeats,
         handlers.heartbeats.HeartbeatsHandler, handler_kwargs),
    ]


def make_app(etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()
    config_cl.tell_everybody_that_i_am_ready()
    handler_kwargs = {
        "config": config_cl,
    }

    return tornado.web.Application(
        get_handlers(handler_kwargs),
        default_handler_class=handlers.base.DefaultHandler)


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
