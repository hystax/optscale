from sqlalchemy import and_, exists

from tools.optscale_exceptions.common_exc import ConflictException

from katara.katara_service.controllers.base import BaseController
from katara.katara_service.controllers.base_async import (
    BaseAsyncControllerWrapper)
from katara.katara_service.exceptions import Err
from katara.katara_service.models.models import Report


class ReportController(BaseController):
    def _get_model_type(self):
        return Report

    def _validate(self, report, is_new=True, **kwargs):
        query = self.session.query(exists().where(
            and_(*(report.get_uniqueness_filter(is_new)))))
        report_exist = query.scalar()
        if report_exist:
            raise ConflictException(
                Err.OKA0003, [report.name, report.module_name])


class ReportAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ReportController
