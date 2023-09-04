import json
import logging

from pharos_backend.pharos_receiver.handlers.v2.base import BaseHandler

LOG = logging.getLogger(__name__)


class MetricsHandler(BaseHandler):
    async def post(self, **kwargs):
        self.check_secret()
        body = json.loads(self.request.body)
        LOG.info(body)
        self.set_status(200)
