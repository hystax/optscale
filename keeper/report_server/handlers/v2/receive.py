import logging

from keeper.report_server.handlers.v2.auth import AuthHandler
from keeper.report_server.handlers.base import BaseReceiveHandler


LOG = logging.getLogger(__name__)


class ReceiveHandler(AuthHandler, BaseReceiveHandler):
    pass
