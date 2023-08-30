import json
import logging

from datetime import datetime
from retrying import retry
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import and_

from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import CloudTypes
from rest_api.rest_api_server.models.models import CloudAccount, K8sNode
from rest_api.rest_api_server.utils import RetriableException, should_retry

from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)


LOG = logging.getLogger(__name__)
RETRIES = dict(
    stop_max_attempt_number=6, wait_fixed=500,
    retry_on_exception=should_retry)


class NodeController(BaseController):
    def __init__(self, db_session, config=None, token=None, engine=None):
        super().__init__(db_session, config, token, engine)
        self._unique_fields = ['name', 'provider_id']  # in cloud acc scope

    def _get_model_type(self):
        return K8sNode

    def get_cloud_account(self, cloud_account_id):
        cloud_acc = self.session.query(CloudAccount).filter(and_(
            CloudAccount.id == cloud_account_id,
            CloudAccount.deleted.is_(False)
        )).one_or_none()

        if not cloud_acc:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])
        if cloud_acc.type != CloudTypes.KUBERNETES_CNR:
            raise WrongArgumentsException(Err.OE0436, [cloud_acc.type.value])

        return cloud_acc

    @staticmethod
    def _get_default_price(cost_model):
        return sum(cost_model.values())

    def _validate_payload(self, payload):
        required_fields = ['provider_id', 'flavor']
        all_fields_exists = all(
            field in payload.keys() and payload.get(field) is not None
            for field in required_fields
        )
        all_fields_not_exists = all(
            payload.get(field) is None for field in required_fields
        )
        if not (all_fields_exists or all_fields_not_exists):
            raise WrongArgumentsException(Err.OE0475, [])

    @retry(**RETRIES)
    def bulk_create(self, cloud_account_id, nodes_payload):
        cloud_acc = self.get_cloud_account(cloud_account_id)
        cost_model = json.loads(cloud_acc.cost_model.value)
        default_price = self._get_default_price(cost_model)

        existing_nodes = super().list(cloud_account_id=cloud_account_id)
        existing_map = {
            tuple(getattr(n, f, None) for f in self._unique_fields): n
            for n in existing_nodes}
        payload_map = {
            tuple(np.get(f, None) for f in self._unique_fields): np
            for np in nodes_payload
        }

        res = []
        now = int(datetime.utcnow().timestamp())
        try:
            for k, existing_node in existing_map.items():
                changes = payload_map.pop(k, None)
                if not changes:
                    existing_node.deleted_at = now
                    continue

                if changes.get('hourly_price') is None:
                    changes['hourly_price'] = default_price
                self.check_update_restrictions(**changes)
                self.session.expunge(existing_node)
                for key, value in changes.items():
                    setattr(existing_node, key, value)
                self.session.add(existing_node)
                res.append(existing_node)

            for payload in payload_map.values():
                self._validate_payload(payload)
                if payload.get('hourly_price') is None:
                    payload['hourly_price'] = default_price
                self.check_create_restrictions(**payload)
                new_node = self.model_type(
                    cloud_account_id=cloud_account_id, **payload)
                self.session.add(new_node)
                res.append(new_node)
            self.session.commit()
        except IntegrityError as ex:
            self.session.rollback()
            self.session.expunge_all()
            raise RetriableException(ex)

        return res

    def list(self, cloud_account_id):
        cloud_acc = self.get_cloud_account(cloud_account_id)
        return self.session.query(self.model_type).filter(and_(
            self.model_type.cloud_account_id == cloud_acc.id,
            self.model_type.last_seen >= cloud_acc.last_import_at,
            self.model_type.deleted_at.is_(False)
        )).all()


class NodesAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return NodeController
