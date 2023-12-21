import os
import time
import asyncio
import datetime
from functools import (
    lru_cache,
    partial,
)
import concurrent.futures

from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.insider_client.client import Client as InsiderClient


SECS_IN_HR = 3600  # seconds in hour


class CostCalc:

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    def __init__(self):
        self._config_cl = None
        self._insider_cl = None

    @staticmethod
    def get_cost(hourly_price, duration):
        return round(hourly_price * duration / SECS_IN_HR, 5)

    @property
    def config_cl(self):
        if self._config_cl is None:
            config_cl = ConfigClient(
                host=os.environ.get('HX_ETCD_HOST'),
                port=int(os.environ.get('HX_ETCD_PORT')),
            )
            self._config_cl = config_cl
        return self._config_cl

    @property
    def insider_cl(self):
        if self._insider_cl is None:
            self._insider_cl = InsiderClient(
                url=self.config_cl.insider_url())
            self._insider_cl.secret = self.config_cl.cluster_secret()
        return self._insider_cl

    @staticmethod
    def get_ttl_hash(seconds=3600):
        return time.time() // seconds

    def calc_runner_cost(
            self,
            runner,
    ):
        cost = 0.0
        cloud_type = runner.get("cloud_type", "aws")
        region_id = runner["region_id"]
        instance_type_id = runner["instance_type"]

        hourly_price = self.get_flavor_price(
            cloud_type,
            region_id,
            instance_type_id,
            self.get_ttl_hash()
        )
        if hourly_price:
            started_at = runner.get('started_at')
            now = int(datetime.datetime.utcnow().timestamp())
            if started_at:
                destroyed_at = runner.get('destroyed_at') or now
                cost = self.get_cost(hourly_price, destroyed_at - started_at)
        return cost

    def calc_runset_cost(
            self,
            runners,
    ):
        total_cost = 0.0
        for runner in runners:
            total_cost += self.calc_runner_cost(
                runner,
            )
        return total_cost

    @lru_cache(maxsize=64)
    def get_flavor_price(self, cloud_type, region, flavor, _ttl_hash,
                         os_type='linux'):
        """
        Gets price from Insider
        :param cloud_type:
        :param region:
        :param flavor:
        :param _ttl_hash:
        :param os_type:
        :return:
        """
        _, c = self.insider_cl.get_flavor_prices(
            cloud_type=cloud_type,
            region=region,
            flavor=flavor,
            os_type=os_type)
        prices = c.get("prices")
        if prices and len(prices):
            return prices[0].get("price", 0.0)

    @classmethod
    async def run_async(cls, func, *args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        if executor is None:
            executor = cls.executor
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)
