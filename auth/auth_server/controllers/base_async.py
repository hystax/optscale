import logging
import functools
from tornado.ioloop import IOLoop
from auth_server.utils import tp_executor

LOG = logging.getLogger(__name__)


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """

    def __init__(self, db_session, config=None):
        self.session = db_session
        self._config = config
        self._db = None
        self._controller = None
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session, self._config)
        return self._controller

    @property
    def model_type(self):
        return self.controller._get_model_type()

    def _get_controller_class(self):
        raise NotImplementedError

    def check_token_valid(self, key):
        return self.io_loop.run_in_executor(None, self.controller.access_token_store.check_token_valid, key)

    def get_awaitable(self, meth_name, *args, **kwargs):
        method = getattr(self.controller, meth_name)
        return self.io_loop.run_in_executor(self.executor, functools.partial(method, *args, **kwargs))

    def __getattr__(self, name):

        def _missing(*args, **kwargs):
            return self.get_awaitable(name, *args, **kwargs)
        return _missing
