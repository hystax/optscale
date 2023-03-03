import logging
import os
import tornado
from config_client.client import Client as ConfigClient
import ohsu.handlers.v2 as handlers
from ohsu.urls import urls_v2


DEFAULT_PORT = 9377
LOG = logging.getLogger(__name__)
SPARK_CONF_PATH = '/opt/spark/conf/spark-defaults.conf'


def get_handlers(handler_kwargs):
    # pylint: disable=E1101
    return [
        (urls_v2.links,
         handlers.links.SHSLinkAsyncHandler, handler_kwargs),
    ]


def make_app(config_cl):
    config_cl.tell_everybody_that_i_am_ready()
    handler_kwargs = {
        "config": config_cl,
    }
    return tornado.web.Application(
        get_handlers(handler_kwargs),
        default_handler_class=handlers.base.DefaultHandler)


def main():
    logging.basicConfig(level=logging.INFO)
    etcdhost = os.environ.get('HX_ETCD_HOST')
    etcdport = int(os.environ.get('HX_ETCD_PORT'))
    config_cl = ConfigClient(
        host=etcdhost,
        port=etcdport,
    )
    config_cl.wait_configured()
    minio = config_cl.read_branch('/minio')
    with open(SPARK_CONF_PATH, 'r') as f:
        data = f.read()
    LOG.info(data)
    with open(SPARK_CONF_PATH, 'a+') as f:
        if 'spark.hadoop.fs.s3a.access.key' not in data:
            f.write('\nspark.hadoop.fs.s3a.access.key   {}'.format(
                minio['access']))
        if 'spark.hadoop.fs.s3a.secret.key' not in data:
            f.write('\nspark.hadoop.fs.s3a.secret.key   {}'.format(
                minio['secret']))
        if 'spark.hadoop.fs.s3a.endpoint' not in data:
            f.write('\nspark.hadoop.fs.s3a.endpoint    {}\n'.format(
                'http://%s:%s' % (minio['host'], minio['port'])))
    app = make_app(config_cl)
    LOG.info("start listening on port %d", DEFAULT_PORT)
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
