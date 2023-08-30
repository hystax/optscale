import logging
from datetime import datetime
from tools.optscale_exceptions.common_exc import (
    ConflictException, WrongArgumentsException)
from rest_api.rest_api_server.controllers.discovery_info import DiscoveryInfoController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import DiscoveryInfo
from rest_api.rest_api_server.utils import check_list_attribute

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_, exists

LOG = logging.getLogger(__name__)


class DiscoveryInfosBulkController(DiscoveryInfoController):

    def _validate(self, item, is_new=True, **kwargs):
        if is_new:
            self.check_cloud_acc_and_org(item.cloud_account_id)
            resource_type = kwargs.get('resource_type')
            query = self.session.query(exists().where(
                and_(DiscoveryInfo.cloud_account_id == item.cloud_account_id,
                     DiscoveryInfo.resource_type == resource_type,
                     DiscoveryInfo.deleted.is_(False))))
            di_exist = query.scalar()
            if di_exist:
                raise ConflictException(Err.OE0518,
                                        [kwargs.get('resource_type'),
                                         item.cloud_account_id])

    def create(self, cloud_account_id, **kwargs):
        result = []
        discovery_infos = kwargs['discovery_info']
        model_type = self._get_model_type()
        try:
            for di_params in discovery_infos:
                di_params['cloud_account_id'] = cloud_account_id
                self.check_create_restrictions(**di_params)
                item = model_type(**di_params)
                self._validate(item, True, **di_params)
                self.session.add(item)
                result.append(item)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            raise WrongArgumentsException(Err.OE0003, [str(ex)])
        return result

    def delete(self, cloud_account_id, **kwargs):
        self.check_cloud_acc_and_org(cloud_account_id)
        discovery_infos_ids = kwargs['discovery_info']
        now = int(datetime.utcnow().timestamp())
        self.session.query(DiscoveryInfo).filter(
            DiscoveryInfo.id.in_(discovery_infos_ids),
            DiscoveryInfo.deleted.is_(False)
        ).update({DiscoveryInfo.deleted_at: now},
                 synchronize_session=False)
        self.session.commit()


class DiscoveryInfosAsyncBulkController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return DiscoveryInfosBulkController
