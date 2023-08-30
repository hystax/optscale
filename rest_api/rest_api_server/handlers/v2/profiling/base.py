from rest_api.rest_api_server.utils import run_task
from rest_api.rest_api_server.handlers.v2.base import BaseHandler


class ProfilingHandler(BaseHandler):
    async def _get_profiling_token(self, organization_id):
        res = await run_task(
            self.controller.get_profiling_token, organization_id)
        return res
