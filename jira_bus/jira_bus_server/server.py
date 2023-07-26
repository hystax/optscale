import argparse
import logging
import os

import config_client.client
import pydevd_pycharm
import tornado.ioloop
import tornado.web
from etcd import Lock as EtcdLock

from jira_bus_server.constants import backend_urls
from jira_bus_server.handlers.v2.app_descriptor import AppDescriptorHandler
from jira_bus_server.handlers.v2.app_hook import (
    AppHookIssueUpdatedHandler, AppHookIssueDeletedHandler)
from jira_bus_server.handlers.v2.app_lifecycle import (
    AppLifecycleInstalledHandler)
from jira_bus_server.handlers.v2.base import DefaultHandler
from jira_bus_server.handlers.v2.issue_attachment import (
    IssueAttachmentCollectionHandler, IssueAttachmentItemHandler)
from jira_bus_server.handlers.v2.issue_info import IssueInfoHandler
from jira_bus_server.handlers.v2.organization_assignment import (
    OrganizationAssignmentHandler)
from jira_bus_server.handlers.v2.organization import (
    OrganizationCollectionHandler)
from jira_bus_server.handlers.v2.organization_status import (
    OrganizationStatusHandler)
from jira_bus_server.handlers.v2.shareable_book import (
    ShareableBookCollectionHandler, ShareableBookItemHandler)
from jira_bus_server.handlers.v2.shareable_resource import (
    ShareableResourceHandler)
from jira_bus_server.handlers.v2.swagger import SwaggerStaticFileHandler
from jira_bus_server.handlers.v2.user_assignment import UserAssignmentHandler
from jira_bus_server.models.db_factory import DBType, DBFactory

DEFAULT_PORT = 8977
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

LOG = logging.getLogger(__name__)

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')
UI_PATH = os.path.join(BASEDIR_PATH, 'ui')


def get_handlers(handler_kwargs):
    return [
        (backend_urls.app_descriptor,
         AppDescriptorHandler, handler_kwargs),
        (backend_urls.installed,
         AppLifecycleInstalledHandler, handler_kwargs),
        (backend_urls.issue_updated,
         AppHookIssueUpdatedHandler, handler_kwargs),
        (backend_urls.issue_deleted,
         AppHookIssueDeletedHandler, handler_kwargs),
        (backend_urls.user_assignment,
         UserAssignmentHandler, handler_kwargs),
        (backend_urls.organization_assignment,
         OrganizationAssignmentHandler, handler_kwargs),
        (backend_urls.organization_collection,
         OrganizationCollectionHandler, handler_kwargs),
        (backend_urls.issue_info,
         IssueInfoHandler, handler_kwargs),
        (backend_urls.shareable_resource,
         ShareableResourceHandler, handler_kwargs),
        (backend_urls.issue_attachment_collection,
         IssueAttachmentCollectionHandler, handler_kwargs),
        (backend_urls.issue_attachment_item,
         IssueAttachmentItemHandler, handler_kwargs),
        (backend_urls.shareable_book_collection,
         ShareableBookCollectionHandler, handler_kwargs),
        (backend_urls.shareable_book_item,
         ShareableBookItemHandler, handler_kwargs),
        (backend_urls.organization_status,
         OrganizationStatusHandler, handler_kwargs)
    ]


def get_swagger_handlers():
    return [
        (r'%s/swagger/(.*)' % backend_urls.url_prefix,
         SwaggerStaticFileHandler, {'path': SWAGGER_PATH}),
        (r'%s/?' % backend_urls.url_prefix, tornado.web.RedirectHandler,
         {'url': '%s/swagger/spec.html' % backend_urls.url_prefix}),
    ]


def make_app(db_type, etcd_host, etcd_port, wait=False):
    config_cl = config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    db = DBFactory(db_type, config_cl).db
    if wait:
        # Use lock to avoid migration problems with several jira buses
        # starting at the same time on cluster
        LOG.info('Waiting for migration lock')
        with EtcdLock(config_cl, 'jira_bus_migrations'):
            db.create_schema()
    else:
        db.create_schema()

    handler_kwargs = {
        'engine': db.engine,
        'config': config_cl,
    }
    config_cl.tell_everybody_that_i_am_ready()

    # noinspection PyTypeChecker
    handlers = get_handlers(handler_kwargs) + get_swagger_handlers()

    return tornado.web.Application(
        handlers, default_handler_class=DefaultHandler)


def main():
    if os.environ.get('PYCHARM_DEBUG_HOST'):
        pydevd_pycharm.settrace(
            host=os.environ['PYCHARM_DEBUG_HOST'],
            port=int(os.environ.get('PYCHARM_DEBUG_PORT', 3000)),
            stdoutToServer=True,
            stderrToServer=True,
            suspend=False,
        )

    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    args = parser.parse_args()

    app = make_app(DBType.MySQL, args.etcdhost, args.etcdport, wait=True)
    LOG.info('start listening on port %d', DEFAULT_PORT)
    app.listen(DEFAULT_PORT, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
