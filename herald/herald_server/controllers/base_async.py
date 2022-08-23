import functools
import logging
from tornado.ioloop import IOLoop

from herald_server.utils import tp_executor


LOG = logging.getLogger(__name__)


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """

    def __init__(self, db_session, config=None, rabbit_client=None):
        self.session = db_session
        self._config = config
        self.rabbit_client = rabbit_client
        self._controller = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session, self._config, self.rabbit_client)
        return self._controller

    def _get_controller_class(self):
        raise NotImplementedError

    def get_awaitable(self, meth_name, *args, **kwargs):
        method = getattr(self.controller, meth_name)
        return self.io_loop.run_in_executor(self.executor, functools.partial(method, *args, **kwargs))

    def __getattr__(self, name):

        def _missing(*args, **kwargs):
            return self.get_awaitable(name, *args, **kwargs)
        return _missing
