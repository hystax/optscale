import logging
from datetime import datetime
from tools.optscale_exceptions.common_exc import (ConflictException,
                                                  NotFoundException)
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.pool import PoolController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Pool, PoolExpensesExport
from rest_api.rest_api_server.utils import BASE_POOL_EXPENSES_EXPORT_LINK_FORMAT as BASE_LINK_FORMAT
from sqlalchemy import and_

LOG = logging.getLogger(__name__)


class PoolExpensesExportController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pool_ctrl = None

    def _get_model_type(self):
        return PoolExpensesExport

    @property
    def pool_ctrl(self):
        if self._pool_ctrl is None:
            self._pool_ctrl = PoolController(self.session, self._config)
        return self._pool_ctrl

    def _generate_export_link(self, export_id):
        return BASE_LINK_FORMAT.format(self._config.public_ip(), export_id)

    def get_pool(self, pool_id):
        pool = self.session.query(Pool).filter(
            and_(
                Pool.id == pool_id,
                Pool.deleted.is_(False)
            )
        ).one_or_none()
        if not pool:
            raise NotFoundException(
                Err.OE0002, [Pool.__name__, pool_id])
        return pool

    def get_export(self, export_id):
        export = self.session.query(PoolExpensesExport).filter(
            PoolExpensesExport.id == export_id,
            PoolExpensesExport.deleted.is_(False)
        ).one_or_none()
        if not export:
            raise NotFoundException(
                Err.OE0002, [PoolExpensesExport.__name__, export_id])
        return export

    def get_export_by_pool(self, pool_id):
        export = self.session.query(PoolExpensesExport).filter(
            PoolExpensesExport.pool_id == pool_id,
            PoolExpensesExport.deleted.is_(False)
        ).one_or_none()
        if not export:
            raise NotFoundException(
                Err.OE0002, [PoolExpensesExport.__name__, ''])
        return export

    def get_pool_id(self, export_id):
        export = self.get_export(export_id)
        return export.pool_id

    def create(self, pool_id):
        res = {}
        self.get_pool(pool_id)
        try:
            self.get_export_by_pool(pool_id)
            raise ConflictException(Err.OE0469, [pool_id])
        except NotFoundException:
            export = super().create(pool_id=pool_id).to_dict()
            res['expenses_export_link'] = self._generate_export_link(export['id'])
            return res

    def get_expenses_data(self, export_id, start_date=None, end_date=None):
        pool_id = self.get_pool_id(export_id)
        if start_date is None and end_date is None:
            start_date = 0
            end_date = int(datetime.utcnow().timestamp())
        elif end_date is None:
            end_date = start_date + 24 * 60 * 60 - 1
        pool = self.get_pool(pool_id)
        expenses = self.pool_ctrl.get_expenses(
            pool, start_date, end_date, filter_by='pool_expenses_export')
        return expenses

    def delete(self, item_id):
        self.get_export(item_id)
        return super().delete(item_id)


class PoolExpensesExportAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return PoolExpensesExportController
