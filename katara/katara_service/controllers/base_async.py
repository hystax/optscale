import functools
import logging
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop


LOG = logging.getLogger(__name__)
tp_executor = ThreadPoolExecutor(30)


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return awaitable
    """
    def __init__(self, db_session, config=None, engine=None):
        self.session = db_session
        self._config = config
        self._db = None
        self._controller = None
        self._engine = engine
        self.executor = tp_executor
        self.io_loop = IOLoop.current()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(
                self.session, self._config, self.engine)
        return self._controller

    @property
    def engine(self):
        return self._engine

    @property
    def model_type(self):
        return self.controller._get_model_type()

    def _get_controller_class(self):
        raise NotImplementedError

    def get_awaitable(self, meth_name, *args, **kwargs):
        method = getattr(self.controller, meth_name)
        return self.io_loop.run_in_executor(self.executor, functools.partial(method, *args, **kwargs))

    def __getattr__(self, name):

        def _missing(*args, **kwargs):
            return self.get_awaitable(name, *args, **kwargs)
        return _missing
