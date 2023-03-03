import aiohttp

from optscale_arcee.platform import CollectorFactory
from optscale_arcee.module_collector.collector import Collector as ImportsCollector
from optscale_arcee.hw_stat_collector.collector import Collector as HwCollector


class Sender:

    # default OptScale url
    base_url = "https://my.optscale.com:443/arcee/v2"

    def __init__(self, endpoint_url=None, ssl=True):
        if endpoint_url is None:
            endpoint_url = self.base_url
        self.endpoint_url = endpoint_url
        self.ssl = ssl

    @staticmethod
    async def m():
        platform = await CollectorFactory.get()
        return await platform().get_platform_meta()

    @staticmethod
    async def _proc_data():
        return await HwCollector.collect_stats()

    @staticmethod
    async def _imports_data():
        return await ImportsCollector.get_imports()

    async def send_get_request(self, url, headers=None, params=None) -> str:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                url, params=params, raise_for_status=True, ssl=self.ssl
            ) as response:
                return await response.json()

    async def send_post_request(self, url, headers=None, data=None) -> str:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(
                url, json=data, raise_for_status=True, ssl=self.ssl
            ) as response:
                return await response.json()

    async def send_patch_request(self, url, headers=None, data=None) -> str:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.patch(
                url, json=data, raise_for_status=True, ssl=self.ssl
            ) as response:
                return await response.json()

    async def get_run_id(self, application, token, run_name):
        uri = "%s/applications/%s/run" % (self.endpoint_url, application)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        data = {"imports": await self._imports_data(), "name": run_name}
        return await self.send_post_request(uri, headers, data)

    async def add_milestone(self, run_id, token, value):
        uri = "%s/run/%s/milestones" % (self.endpoint_url, run_id)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        return await self.send_post_request(uri, headers, {"milestone": value})

    async def add_tags(self, run_id, token, tags):
        uri = "%s/run/%s" % (self.endpoint_url, run_id)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        return await self.send_patch_request(uri, headers, {"tags": tags})

    async def change_state(self, run_id, token, state, finish=None):
        uri = "%s/run/%s" % (self.endpoint_url, run_id)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        return await self.send_patch_request(
            uri, headers, {"state": state, "finish": finish}
        )

    async def create_stage(self, run_id, token, name):
        uri = "%s/run/%s/stages" % (self.endpoint_url, run_id)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        return await self.send_post_request(uri, headers, {"stage": name})

    async def send_stats(self, token, data):
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        meta = await self.m()
        data.update({"platform": meta.to_dict()})
        await self.send_post_request(
            "%s/%s" % (self.endpoint_url, "collect"), headers, data
        )

    async def send_proc_data(self, run_id, token):
        uri = "%s/run/%s/proc" % (self.endpoint_url, run_id)
        headers = {"x-api-key": token, "Content-Type": "application/json"}
        data = dict()
        meta = await self.m()
        proc = await self._proc_data()
        data.update({"platform": meta.to_dict()})
        data.update({"proc_stats": proc})
        return await self.send_post_request(uri, headers, data)
