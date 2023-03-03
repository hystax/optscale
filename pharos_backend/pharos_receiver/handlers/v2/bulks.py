import json
import logging
from pharos_receiver.controllers.bulk import LogsBulkAsyncController
from pharos_receiver.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class LogsBulkHandler(BaseHandler):
    def _get_controller_class(self):
        return LogsBulkAsyncController

    async def post(self, **kwargs):
        """Collects events from agent"""
        self.check_secret()
        body = json.loads(self.request.body)
        LOG.info(body)
        await self.controller.save(body)
        self.set_status(200)
