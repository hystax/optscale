import functools
from concurrent.futures import ThreadPoolExecutor
from tornado.ioloop import IOLoop
from clickhouse_driver import Client as ClickHouseClient

tp_executor = ThreadPoolExecutor(30)


class BaseController(object):
    def __init__(self, config=None):
        super().__init__()
        self.config_cl = config
        self._clickhouse_client = None

    @property
    def clickhouse_client(self):
        if not self._clickhouse_client:
            user, password, host, db_name = self.config_cl.clickhouse_params()
            self._clickhouse_client = ClickHouseClient(
                host=host, password=password, database=db_name, user=user)
        return self._clickhouse_client


class BaseAsyncControllerWrapper(object):
    """
    Used to wrap sync controller methods to return futures
    """
    def __init__(self, config_cl=None):
        self.config_cl = config_cl
        self.executor = tp_executor
        self._controller = None
        self.io_loop = IOLoop.current()

    @property
    def controller(self):
        if not self._controller:
            self._controller = self._get_controller_class()(self.config_cl)
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
