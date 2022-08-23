import logging
import os
import re

import tornado.web
import tornado.ioloop

from etcd import Lock as EtcdLock
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.installation_store.sqlalchemy import (
    SQLAlchemyInstallationStore)
from slack_sdk.oauth.state_store.sqlalchemy import SQLAlchemyOAuthStateStore
from slacker_server.slack_client import SlackClient
from config_client.client import Client as ConfigClient

from slacker_server.constants import urls
from slacker_server.controllers.slack import MetaSlackController
from slacker_server.handlers.v2.base import DefaultHandler
from slacker_server.handlers.v2.connect import ConnectHandler
from slacker_server.handlers.v2.send_message import SendMessageHandler
from slacker_server.handlers.v2.slack import (SlackEventsHandler,
                                              SlackOAuthHandler,
                                              SlackInstallPathHandler)
from slacker_server.handlers.v2.swagger import SwaggerStaticFileHandler
from slacker_server.models.db_factory import DBType, DBFactory

LOG = logging.getLogger(__name__)
BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')


def make_slack_app(engine, config_cl):
    slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET",
                                          'signing_secret')
    slack_client_id = os.environ.get("SLACK_CLIENT_ID", 'client_id')
    slack_client_secret = os.environ.get("SLACK_CLIENT_SECRET", 'client_secret')

    installation_store = SQLAlchemyInstallationStore(
        client_id=slack_client_id,
        engine=engine,
        logger=LOG,
    )
    oauth_state_store = SQLAlchemyOAuthStateStore(
        expiration_seconds=120,
        engine=engine,
        logger=LOG,
    )

    app = App(
        logger=LOG,
        signing_secret=slack_signing_secret,
        installation_store=installation_store,
        oauth_settings=OAuthSettings(
            client_id=slack_client_id,
            client_secret=slack_client_secret,
            scopes=["chat:write", 'im:history', 'chat:write.public',
                    'groups:write', 'channels:read', 'groups:read'],
            state_store=oauth_state_store,
            redirect_uri_path=urls.oauth_redirect,
            install_path=urls.install,
        ),
        client=SlackClient(installation_store=installation_store)
    )

    def re_msg(msg):
        return re.compile(msg, re.IGNORECASE)

    slack_ctrl = MetaSlackController(engine, config_cl)
    app.event('app_home_opened')(slack_ctrl.app_home_opened)
    app.event('member_joined_channel')(slack_ctrl.member_joined_channel)
    app.message(re_msg('logout'))(slack_ctrl.message_logout)
    app.message(re_msg('org'))(slack_ctrl.message_org)
    app.message(re_msg('resources'))(slack_ctrl.message_resources)
    app.message(re_msg('alerts'))(slack_ctrl.message_alerts)
    app.message(re_msg('envs'))(slack_ctrl.message_envs)
    app.message('')(slack_ctrl.message)
    app.action('choose_organization')(slack_ctrl.switch_org)
    app.action('account_disconnect')(slack_ctrl.disconnect)
    app.action('resource_details')(slack_ctrl.resource_details)
    app.action('link_button_click')(slack_ctrl.ack_event)
    app.action('alert_delete')(slack_ctrl.delete_alert)
    app.action('alert_create')(slack_ctrl.create_alert_view)
    app.action('alert_view_next')(slack_ctrl.update_alert_view)
    app.view('add_alert_view')(slack_ctrl.create_alert_submit)
    app.action('update_ttl')(slack_ctrl.create_update_ttl_view)
    app.view('update_ttl_view')(slack_ctrl.update_ttl_submit)
    app.action('add_booking')(slack_ctrl.create_booking_view)
    app.view('add_booking_view')(slack_ctrl.create_booking_submit)
    app.action('booking_details')(slack_ctrl.booking_details)
    app.action('delete_booking')(slack_ctrl.delete_booking)
    app.action('release_booking')(slack_ctrl.release_booking)
    app.use(slack_ctrl.log_request)
    return app


def make_tornado_app(app, db, config_cl, wait=False):
    if wait:
        config_cl.wait_configured()

    if wait:
        # Use lock to avoid migration problems with several containers
        # starting at the same time on cluster
        LOG.info('Waiting for migration lock')
        with EtcdLock(config_cl, 'slacker_migrations'):
            db.create_schema()
    else:
        db.create_schema()

    handler_kwargs = {
        "engine": db.engine,
        "config_cl": config_cl,
        "app": app,
    }
    config_cl.tell_everybody_that_i_am_ready()
    return tornado.web.Application(
        get_slack_handlers(app) + get_handlers(
            handler_kwargs) + get_swagger_handlers(),
        default_handler_class=DefaultHandler
    )


def get_slack_handlers(app):
    return [
        (urls.events, SlackEventsHandler, dict(app=app)),
        (urls.install, SlackOAuthHandler, dict(app=app)),
        (urls.oauth_redirect, SlackOAuthHandler, dict(app=app)),
        (urls.install_path, SlackInstallPathHandler, dict(app=app)),
    ]


def get_handlers(handler_kwargs):
    return [
        (urls.connect_slack_user, ConnectHandler, handler_kwargs),
        (urls.send_message, SendMessageHandler, handler_kwargs),
        (urls.install_path, SlackInstallPathHandler, handler_kwargs),
    ]


def get_swagger_handlers():
    return [
        (r'%s/swagger/(.*)' % urls.url_prefix,
         SwaggerStaticFileHandler, {'path': SWAGGER_PATH}),
        (r"%s/?" % urls.url_prefix, tornado.web.RedirectHandler,
         {"url": "%s/swagger/spec.html" % urls.url_prefix}),
    ]


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', '127.0.0.1')
    etcd_port = int(os.environ.get('HX_ETCD_PORT', '2379'))
    config_cl = ConfigClient(host=etcd_host, port=etcd_port)

    db_type = DBType.MySQL
    db = DBFactory(db_type, config_cl).db

    slack_app = make_slack_app(db.engine, config_cl)
    tornado_app = make_tornado_app(slack_app, db, config_cl, wait=True)
    LOG.info("start listening on port %d", 80)
    tornado_app.listen(80, decompress_request=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
