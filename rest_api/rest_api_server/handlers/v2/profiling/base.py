import hashlib
from tools.optscale_exceptions.http_exc import OptHTTPError
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.utils import run_task
from rest_api.rest_api_server.handlers.v2.base import BaseHandler


class ProfilingHandler(BaseHandler):
    async def _get_profiling_token(self, organization_id):
        res = await run_task(
            self.controller.get_profiling_token, organization_id)
        return res

    async def check_md5_profiling_token(
            self, organization_id, token, raises=True):
        token_db = await self._get_profiling_token(organization_id)
        md5_token = hashlib.md5(token_db.encode('utf-8')).hexdigest()
        if token != md5_token:
            if raises:
                raise OptHTTPError(403, Err.OE0234, [])
            else:
                return None
        return token_db
