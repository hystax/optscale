from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import functools
from pymongo import MongoClient
from tornado.ioloop import IOLoop


tp_executor = ThreadPoolExecutor(30)
DEFAULT_CACHE_TIME = 60 * 60 * 12
MAX_PARALLEL_REQUESTS = 50


class CachedCloudCaller:
    def __init__(self, mongo_cl):
        self.mongo_cl = mongo_cl

    @property
    def cache_collection(self):
        return self.mongo_cl.insider.cache

    def cached_cloud_call(self, fn, *args, **kwargs):
        query_filter = {
            'func_name': fn.__name__,
            'args': args,
            'kwargs': kwargs,
        }
        cache_filter = deepcopy(query_filter)
        now = datetime.utcnow()
        cache_filter['updated_at'] = {
            '$gte': now - timedelta(seconds=DEFAULT_CACHE_TIME)
        }
        cache = list(self.cache_collection.find(cache_filter))
        if cache:
            return cache[0]['result']
        else:
            result = fn(*args, **kwargs)
            self.cache_collection.update_one(query_filter, {
                '$set': {'result': result, 'updated_at': now},
                '$setOnInsert': query_filter,
            }, upsert=True)
            return result


class CachedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, mongo_cl):
        super().__init__(max_workers=MAX_PARALLEL_REQUESTS)
        self.caller = CachedCloudCaller(mongo_cl)

    def submit(self, fn, *args, **kwargs):
        return super().submit(self.caller.cached_cloud_call,
                              fn, *args, **kwargs)


class BaseController(object):

    def __init__(self, config=None):
        super().__init__()
        self._config = config
        self._mongo_client = None

    @property
    def mongo_client(self):
        if not self._mongo_client:
            mongo_params = self._config.mongo_params()
            mongo_conn_string = "mongodb://%s:%s@%s:%s" % mongo_params[:-1]
            self._mongo_client = MongoClient(mongo_conn_string)
        return self._mongo_client

    @property
    def discoveries_collection(self):
        return self.mongo_client.insider.discoveries

    @property
    def azure_prices_collection(self):
        return self.mongo_client.insider.azure_prices


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
