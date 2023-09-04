import json
import logging
from pharos_backend.pharos_receiver.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class AcksHandler(BaseHandler):
    def _get_controller_class(self):
        return NotImplemented

    async def post(self, **kwargs):
        """Only dmAppId is in body"""
        self.check_secret()
        body = json.loads(self.request.body)
        LOG.info(body)
        self.set_status(200)
