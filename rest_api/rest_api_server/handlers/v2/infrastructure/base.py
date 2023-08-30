from rest_api.rest_api_server.utils import run_task
from rest_api.rest_api_server.handlers.v2.base import BaseHandler


class InfrastructureHandler(BaseHandler):
    async def _get_infrastructure_token(self, organization_id):
        res = await run_task(
            self.controller.get_infrastructure_token, organization_id)
        return res
