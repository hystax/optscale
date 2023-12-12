import json
import logging
from sqlalchemy import and_, exists

from tools.optscale_exceptions.common_exc import (
    ConflictException,
    WrongArgumentsException,
)
from optscale_client.rest_api_client.client_v2 import Client as RestClient

from katara.katara_service.controllers.base import BaseController
from katara.katara_service.controllers.base_async import (
    BaseAsyncControllerWrapper)
from katara.katara_service.exceptions import Err
from katara.katara_service.models.models import Recipient, RolePurpose
from katara.katara_service.utils import (
    check_kwargs_empty, check_list_attribute)


LOG = logging.getLogger(__name__)


class RecipientController(BaseController):
    def __init__(self, db_session=None, config=None, engine=None):
        super().__init__(db_session, config, engine)
        self._rest_cl = None

    def _get_model_type(self):
        return Recipient

    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(url=self._config.restapi_url(),
                                       verify=False)
            self._rest_cl.secret = self._config.cluster_secret()
        return self._rest_cl

    def _validate(self, recipient, is_new=True, **kwargs):
        query = self.session.query(
            exists().where(and_(*(recipient.get_uniqueness_filter(is_new))))
        )
        recipient_exist = query.scalar()
        if recipient_exist:
            raise ConflictException(
                Err.OKA0002, [recipient.role_purpose, recipient.scope_id]
            )
        if kwargs.get("meta"):
            try:
                json.loads(recipient.meta)
            except (TypeError, ValueError, json.decoder.JSONDecodeError):
                raise WrongArgumentsException(Err.OKA0016, [])
        if not recipient.scope_id:
            raise WrongArgumentsException(Err.OKA0021, ["scope_id"])
        if not recipient.role_purpose and not recipient.user_id:
            raise WrongArgumentsException(Err.OKA0023, [])
        elif recipient.role_purpose and recipient.user_id:
            raise WrongArgumentsException(Err.OKA0024, [])
        elif recipient.role_purpose and not recipient.user_id:
            try:
                RolePurpose(recipient.role_purpose)
            except ValueError:
                raise WrongArgumentsException(Err.OKA0025, ["role_purpose"])

    def delete(self, **kwargs):
        payload_dict = kwargs.pop("payload")
        check_kwargs_empty(**kwargs)
        user_ids = payload_dict.get("user_ids")
        recipient_ids = payload_dict.get("recipient_ids")
        scope_ids = payload_dict.get("scope_ids")
        check_list_attribute("user_ids", user_ids, required=False)
        check_list_attribute("recipient_ids", recipient_ids, required=False)
        check_list_attribute("scope_ids", scope_ids, required=False)
        filtered = False
        query = self.session.query(Recipient)
        filter_list = [
            (user_ids, Recipient.user_id),
            (recipient_ids, Recipient.id),
            (scope_ids, Recipient.scope_id),
        ]
        for filter_data, filter_obj in filter_list:
            if filter_data:
                filtered = True
                query = query.filter(filter_obj.in_(filter_data))
        if filtered:
            query.delete(synchronize_session="fetch")
            self.session.commit()


class RecipientAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RecipientController
