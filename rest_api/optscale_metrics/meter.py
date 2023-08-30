import functools
import inspect
import logging
import os
import threading
import time

from optscale_client.config_client.client import Client as ConfigClient
from etcd import EtcdEventIndexCleared
from influxdb import InfluxDBClient

LOG = logging.getLogger(__name__)


class Meter:
    def __init__(self):
        etcd_host = os.environ.get('HX_ETCD_HOST')
        etcd_port = os.environ.get('HX_ETCD_PORT')
        self.service = 'not-set'
        self.enabled = False
        self.watcher_running = False

        try:
            if etcd_port is not None or etcd_host is not None:
                self.config_cl = ConfigClient(
                    host=etcd_host, port=int(etcd_port))
            else:
                raise Exception('etcd env is not configured')
            self.config_cl.wait_configured()
            self.influx_cl = InfluxDBClient(
                *self.config_cl.metrics_influx_params(), timeout=10, retries=1)
            self.watcher_running = True
        except Exception as exc:
            LOG.exception('Failed to connect to influx, '
                          'metrics will not work: %s', exc)
            pass

        watcher = threading.Thread(target=self.watch)
        watcher.start()

    def stop(self):
        self.watcher_running = False

    def watch(self):
        tracking_index = None
        while self.watcher_running:
            try:
                enabled = self.config_cl.read('/optscale_meter_enabled')
                self.enabled = bool(int(enabled.value))

                if tracking_index is None:
                    tracking_index = int(enabled.modifiedIndex) + 1
                try:
                    self.config_cl.watch(enabled.key, index=tracking_index)
                except EtcdEventIndexCleared:
                    LOG.warning('Etcd index cleared, restarting watcher')
                    tracking_index = int(enabled.etcd_index) + 1
                    continue

                tracking_index = None
            except Exception as exc:
                LOG.warning('Restarting meter watcher due to failure: %s. ', exc)
                self.enabled = False
                time.sleep(5)

    def save_execution_time(self, measurement, execution_time):
        if not self.enabled:
            return
        body = [
            {
                "measurement": measurement,
                "tags": {
                    'service': self.service,
                },
                "fields": {
                    'execution_time': execution_time,
                }
            }
        ]
        try:
            self.influx_cl.write_points(body)
        except Exception as exc:
            LOG.exception('Unable to save execution time: %s', exc)


optscale_meter = Meter()


def get_class_that_defined_method(meth):
    if isinstance(meth, functools.partial):
        return get_class_that_defined_method(meth.func)
    if inspect.ismethod(meth) or (
            inspect.isbuiltin(meth)
            and getattr(meth, '__self__', None) is not None
            and getattr(meth.__self__, '__class__', None)
    ):
        for cls in inspect.getmro(meth.__self__.__class__):
            if meth.__name__ in cls.__dict__:
                return cls
        meth = getattr(meth, '__func__', meth)
    if inspect.isfunction(meth):
        cls = getattr(inspect.getmodule(meth),
                      meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0],
                      None)
        if isinstance(cls, type):
            return cls
    return getattr(meth, '__objclass__', None)


def save_stats(f):
    def wrapper(*args, **kwargs):
        if not optscale_meter.enabled:
            return f(*args, **kwargs)
        else:
            start_time = time.time()
            ret = f(*args, **kwargs)

            f_cls = get_class_that_defined_method(f)
            if f_cls is not None:
                measurement = '{}.{}'.format(f_cls.__name__, f.__name__)
            else:
                measurement = f.__name__

            optscale_meter.save_execution_time(
                measurement, time.time() - start_time)
            return ret

    return wrapper
