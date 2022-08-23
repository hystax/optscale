import logging
from tornado.ioloop import IOLoop
from tornado.concurrent import return_future, run_on_executor

from report_server.utils import tp_executor


LOG = logging.getLogger(__name__)


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """

    def __init__(self, mongo_client, config, rabbit_client):
        self.mongo_client = mongo_client
        self._config = config
        self.rabbit_client = rabbit_client
        self._controller = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.mongo_client, self._config,
                self.rabbit_client)
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    @run_on_executor
    @return_future
    def get_future(self, meth_name, *args, callback=None, **kwargs):
        method = getattr(self.controller, meth_name)
        callback(method(*args, **kwargs))

    def __getattr__(self, name):

        def _missing(*args, **kwargs):
            return self.get_future(name, *args, **kwargs)
        return _missing
