import logging

from keeper.report_server.handlers.v2.auth import AuthHandler
from keeper.report_server.handlers.base import BaseReportHandler


LOG = logging.getLogger(__name__)


class ReportHandler(AuthHandler, BaseReportHandler):
    def get_params(self):
        return {
            "time_start": self.get_arg("time_start", int),
            "time_end": self.get_arg("time_end", int),
        }
