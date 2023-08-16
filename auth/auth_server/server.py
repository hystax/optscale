import argparse
import logging
import os

import optscale_client.config_client.client
import tornado.ioloop
import tornado.web
from tornado.web import RedirectHandler

import auth.auth_server.handlers.v1 as h_v1
import auth.auth_server.handlers.v2 as h_v2
from auth.auth_server.constants import urls_v2

from auth.auth_server.handlers.v1.base import DefaultHandler
from auth.auth_server.handlers.v1.swagger import SwaggerStaticFileHandler
from auth.auth_server.models.db_factory import DBType, DBFactory

DEFAULT_PORT = 8905
DEFAULT_ETCD_HOST = '127.0.0.1'
DEFAULT_ETCD_PORT = 2379

LOG = logging.getLogger(__name__)

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')

URL_PREFIX = "/auth/v2"


def get_handlers(handler_kwargs):
    return [
        # urls for auth v2
        (urls_v2.tokens, get_handler_version(
            h_v2, "tokens").TokenAsyncCollectionHandler, handler_kwargs),
        (urls_v2.users_collection, get_handler_version(
            h_v2, "users").UserAsyncCollectionHandler, handler_kwargs),
        (urls_v2.users, get_handler_version(
            h_v2, "users").UserAsyncItemHandler, handler_kwargs),
        (urls_v2.roles_collection, get_handler_version(
            h_v2, "roles").RoleAsyncCollectionHandler, handler_kwargs),
        (urls_v2.roles, get_handler_version(
            h_v2, "roles").RoleAsyncItemHandler, handler_kwargs),
        (urls_v2.authorize, get_handler_version(
            h_v2, "authorization").AuthorizationAsyncHandler, handler_kwargs),
        (urls_v2.assignments_collection, get_handler_version(
            h_v2, "assignments").AssignmentAsyncCollectionHandler,
         handler_kwargs),
        (urls_v2.assignments, get_handler_version(
            h_v2, "assignments").AssignmentAsyncItemHandler, handler_kwargs),
        (urls_v2.types_collection, get_handler_version(
            h_v2, "types").TypeAsyncCollectionHandler, handler_kwargs),
        (urls_v2.types, get_handler_version(
            h_v2, "types").TypeAsyncItemHandler, handler_kwargs),
        (urls_v2.scopes, get_handler_version(
            h_v2, "scopes").ScopeAsyncHandler, handler_kwargs),
        (urls_v2.allowed_actions, get_handler_version(
            h_v2, "actions").ActionAsyncHandler, handler_kwargs),
        (urls_v2.digests, get_handler_version(
            h_v2, "digests").DigestAsyncHandler, handler_kwargs),
        (urls_v2.action_resources, get_handler_version(
            h_v2, "action_resources").ActionResourcesAsyncHandler,
         handler_kwargs),
        (urls_v2.authorize_userlist, get_handler_version(
            h_v2, "authorization_userlist").AuthorizationUserlistAsyncHandler,
         handler_kwargs),
        (urls_v2.my_assignments, get_handler_version(
            h_v2, "assignments").MyAssignmentCollectionHandler,
         handler_kwargs),
        (urls_v2.assignment_register, get_handler_version(
            h_v2, "assignments").RegisterAssignmentCollectionHandler,
         handler_kwargs),
        (urls_v2.purposed_roles, get_handler_version(
            h_v2, "roles").PurposedRoleCollectionHandler, handler_kwargs),
        (urls_v2.user_existence, get_handler_version(
            h_v2, "users").CheckUserExistenceHandler, handler_kwargs),
        (urls_v2.user_roles, h_v2.user_roles.UserRolesAsyncHandler,
         handler_kwargs),
        (urls_v2.user_action_resources, get_handler_version(
            h_v2, "action_resources").UserActionResourcesAsyncHandler,
         handler_kwargs),
        (urls_v2.bulk_action_resources, get_handler_version(
            h_v2, "action_resources").BulkActionResourcesAsyncHandler,
         handler_kwargs),
        (urls_v2.signin, get_handler_version(
            h_v2, "signin").SignInAsyncHandler, handler_kwargs),
    ]


def get_handler_version(h_v, handler, default_version=h_v1):
    return getattr(h_v, handler, None) or getattr(default_version, handler)


def make_app(db_type, etcd_host, etcd_port, wait=False):
    config_cl = optscale_client.config_client.client.Client(
        host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()
    db = DBFactory(db_type, config_cl).db
    db.create_schema()
    handler_kwargs = {
        "engine": db.engine,
        "config": config_cl,
    }
    config_cl.tell_everybody_that_i_am_ready()
    return tornado.web.Application(
        get_handlers(handler_kwargs) + [
            (r'%s/swagger/(.*)' % URL_PREFIX,
             SwaggerStaticFileHandler, {'path': SWAGGER_PATH}),
            (r"%s/?" % URL_PREFIX, RedirectHandler,
             {"url": "%s/swagger/spec.html" % URL_PREFIX}),
        ],
        default_handler_class=DefaultHandler
    )


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
