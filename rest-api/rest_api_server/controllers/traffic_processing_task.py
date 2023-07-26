import logging
from sqlalchemy import and_
from rest_api_server.controllers.base import BaseController
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.exceptions import Err
from rest_api_server.models.models import TrafficProcessingTask, CloudAccount
from optscale_exceptions.common_exc import (
    ConflictException, NotFoundException, WrongArgumentsException)

LOG = logging.getLogger(__name__)


class TrafficProcessingTaskController(BaseController):
    def _get_model_type(self):
        return TrafficProcessingTask

    @staticmethod
    def task_type():
        return 'Traffic'

    def check_existence(self, **kwargs):
        cloud_account_id = kwargs.get('cloud_account_id')
        query_set = self.session.query(
            CloudAccount.id, self.model_type.id
        ).outerjoin(
            self.model_type, and_(
                self.model_type.cloud_account_id == cloud_account_id,
                self.model_type.deleted.is_(False),
                self.model_type.start_date == kwargs.get('start_date'),
                self.model_type.end_date == kwargs.get('end_date')
            )
        ).filter(
            CloudAccount.id == cloud_account_id,
            CloudAccount.deleted.is_(False)
        ).all()
        ca_id, task_id = None, None
        for q in query_set:
            ca_id, task_id = q[0], q[1]
        if not ca_id:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])
        if task_id:
            raise ConflictException(
                Err.OE0519, [self.task_type(), kwargs.get('start_date'),
                             kwargs.get('end_date'), cloud_account_id])

    def _validate(self, item, is_new=True, **kwargs):
        if not is_new:
            return
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        if start_date > end_date:
            raise WrongArgumentsException(Err.OE0446,
                                          ['end_date', 'start_date'])

    def create(self, **kwargs):
        self.check_existence(**kwargs)
        return super().create(**kwargs)

    def list(self, cloud_account_id):
        self._check_cloud_account_exists(cloud_account_id)
        return super().list(cloud_account_id=cloud_account_id)


class TrafficProcessingTaskAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return TrafficProcessingTaskController
