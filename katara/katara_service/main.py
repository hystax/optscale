import argparse
import enum
import logging
import os
import tornado.ioloop
import tornado.web


import katara.katara_service.handlers.v2 as h_v2
from katara.katara_service.controllers.schedule import ScheduleController
from katara.katara_service.models.db_factory import DBFactory, DBType
from katara.katara_service.urls import urls_v2


import optscale_client.config_client.client


DEFAULT_PORT = 8935
DEFAULT_ETCD_HOST = 'etcd'
DEFAULT_ETCD_PORT = 80

BASEDIR_NAME = os.path.dirname(__file__)
BASEDIR_PATH = os.path.abspath(BASEDIR_NAME)
SWAGGER_PATH = os.path.join(BASEDIR_PATH, 'swagger')

LOG = logging.getLogger(__name__)


class Roles(enum.Enum):
    scheduler = 'scheduler'
    api = 'api'

    def __str__(self):
        return self.value


def get_handlers(handler_kwargs):
    return [
        (urls_v2.tasks,
         h_v2.tasks.TaskAsyncItemHandler, handler_kwargs),
        (urls_v2.tasks_collection,
         h_v2.tasks.TaskAsyncCollectionHandler, handler_kwargs),
        (urls_v2.recipients,
         h_v2.recipients.RecipientAsyncItemHandler, handler_kwargs),
        (urls_v2.recipients_collection,
         h_v2.recipients.RecipientAsyncCollectionHandler, handler_kwargs),
        (urls_v2.reports,
         h_v2.reports.ReportAsyncItemHandler, handler_kwargs),
        (urls_v2.reports_collection,
         h_v2.reports.ReportAsyncCollectionHandler, handler_kwargs),
        (urls_v2.schedules,
         h_v2.schedules.ScheduleAsyncItemHandler, handler_kwargs),
        (urls_v2.schedules_collection,
         h_v2.schedules.ScheduleAsyncCollectionHandler, handler_kwargs)
    ]


def setup_api(db, config_cl):
    db.create_schema()
    handler_kwargs = {
        "engine": db.engine,
        "config": config_cl,
    }
    app = tornado.web.Application(
        get_handlers(handler_kwargs) +
        [(urls_v2.swagger, h_v2.swagger.SwaggerStaticFileHandler,
          {'path': SWAGGER_PATH, 'default_filename': 'index.html'})],
        default_handler_class=h_v2.base.DefaultHandler
    )
    config_cl.tell_everybody_that_i_am_ready()
    return app


def setup_scheduler(db, config_cl):
    controller_kwargs = {
        "engine": db.engine,
        "config": config_cl,
    }
    # sync controller will be enough
    schedule_controller = ScheduleController(**controller_kwargs)
    callback_time_in_sec = config_cl.katara_scheduler_timeout()
    app = tornado.ioloop.PeriodicCallback(
        schedule_controller.generate_tasks, callback_time_in_sec * 1000)
    config_cl.tell_everybody_that_i_am_ready()
    return app


def make_app(db_type, role, etcd_host, etcd_port, wait=False):
    applications_map = {
        Roles.api: setup_api,
        Roles.scheduler: setup_scheduler,
    }
    setup_func = applications_map.get(role)
    config_cl = optscale_client.config_client.client.Client(host=etcd_host, port=etcd_port)
    if wait:
        config_cl.wait_configured()

    db = DBFactory(db_type, config_cl).db
    return setup_func(db, config_cl)


def main():
    logging.basicConfig(level=logging.INFO)

    etcd_host = os.environ.get('HX_ETCD_HOST', DEFAULT_ETCD_HOST)
    etcd_port = os.environ.get('HX_ETCD_PORT', DEFAULT_ETCD_PORT)
    role = os.environ.get('HX_KATARA_ROLE')

    parser = argparse.ArgumentParser()
    parser.add_argument('--etcdhost', type=str, default=etcd_host)
    parser.add_argument('--etcdport', type=int, default=etcd_port)
    parser.add_argument('--role', type=Roles, choices=list(Roles),
                        default=role)
    args = parser.parse_args()

    app = make_app(DBType.MySQL, args.role, args.etcdhost,
                   args.etcdport, wait=True)
    if isinstance(app, tornado.ioloop.PeriodicCallback):
        LOG.info("Starting periodic")
        app.start()
    elif isinstance(app, tornado.web.Application):
        LOG.info("Start listening on port %d", DEFAULT_PORT)
        app.listen(DEFAULT_PORT, decompress_request=True)
    else:
        return

    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
