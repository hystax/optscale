import json
import logging
from sqlalchemy.sql import and_, exists
from typing import List

from optscale_exceptions.common_exc import (ConflictException, FailedDependency,
                                            WrongArgumentsException,
                                            NotFoundException)
from rest_api_server.controllers.base import (BaseController,
                                              OrganizationValidatorMixin)
from rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api_server.models.enums import BIOrganizationStatuses, BITypes
from rest_api_server.models.models import OrganizationBI
from rest_api_server.utils import encrypt_bi_meta
from rest_api_server.exceptions import Err
from rest_api_server.utils import (raise_not_provided_exception,
                                   check_dict_attribute, check_string_attribute)

LOG = logging.getLogger(__name__)


class BIController(BaseController):
    """
    Controller for /restapi/v2/bi/{id}
    """

    def _get_model_type(self):
        return OrganizationBI

    @staticmethod
    def _get_encrypted_meta(**kwargs) -> str:
        return encrypt_bi_meta(json.dumps(kwargs.get("meta", {})))

    @staticmethod
    def _get_storage_acc_from_conn_str(conn_string):
        try:
            return conn_string.split('AccountName=')[1].split(';')[0]
        except IndexError:
            raise WrongArgumentsException(Err.OE0217, ['connection_string'])

    @staticmethod
    def _validate_state_transition(item, new_status):
        transition_map = {
            BIOrganizationStatuses.ACTIVE.value: [
                BIOrganizationStatuses.ACTIVE.value,
                BIOrganizationStatuses.QUEUED.value
            ],
            BIOrganizationStatuses.QUEUED.value: [
                BIOrganizationStatuses.QUEUED.value,
                BIOrganizationStatuses.RUNNING.value
            ],
            BIOrganizationStatuses.RUNNING.value: [
                BIOrganizationStatuses.RUNNING.value,
                BIOrganizationStatuses.QUEUED.value,
                BIOrganizationStatuses.SUCCESS.value,
                BIOrganizationStatuses.FAILED.value
            ],
            BIOrganizationStatuses.SUCCESS.value: [
                BIOrganizationStatuses.SUCCESS.value,
                BIOrganizationStatuses.QUEUED.value
            ],
            BIOrganizationStatuses.FAILED.value: [
                BIOrganizationStatuses.FAILED.value,
                BIOrganizationStatuses.QUEUED.value
            ]
        }
        available_transitions = transition_map.get(item.status.value, [])
        if new_status not in available_transitions:
            raise FailedDependency(Err.OE0521, [item.status.value, new_status])

    def _validate(self, item, is_new=True, **kwargs):
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        bi_exists = query.scalar()
        if bi_exists:
            raise ConflictException(Err.OE0149, [
                self.model_type.__name__, kwargs['name']])
        if (
            item.status in [BIOrganizationStatuses.SUCCESS,
                            BIOrganizationStatuses.ACTIVE] and
                item.last_status_error
        ):
            raise FailedDependency(
                Err.OE0523,
                ["last_error_code", item.status.value],
            )
        elif (
            item.status == BIOrganizationStatuses.FAILED and
                not item.last_status_error
        ):
            raise FailedDependency(
                Err.OE0525,
                ["last_error_code", item.status.value],
            )

    def _handle_type_meta(self, type_, meta):
        check_dict_attribute('meta', meta)
        if type_ == BITypes.AWS_RAW_EXPORT.value:
            meta_required = ['access_key_id', 'secret_access_key', 'bucket']
            meta_optional = ['s3_prefix']
        elif type_ == BITypes.AZURE_RAW_EXPORT.value:
            meta_required = ['connection_string', 'container']
            meta_optional = ['storage_account']
        else:
            raise WrongArgumentsException(Err.OE0174, [type_])
        meta_unexpected = list(filter(
            lambda x: x not in meta_required + meta_optional, meta.keys()))
        if meta_unexpected:
            raise WrongArgumentsException(Err.OE0546, [meta_unexpected, type_])
        meta_missing = list(filter(
            lambda x: x not in meta.keys(), meta_required))
        if meta_missing:
            raise_not_provided_exception(meta_missing)
        for key, value in meta.items():
            check_string_attribute(key, value)
        if type_ == BITypes.AZURE_RAW_EXPORT.value:
            meta['storage_account'] = self._get_storage_acc_from_conn_str(
                meta['connection_string'])
        return meta

    def edit(self, item_id, **kwargs):
        status = kwargs.get("status")
        item = self.get(item_id)
        # setting last_status_error into None for SUCCESS
        if status:
            if status == BIOrganizationStatuses.SUCCESS.value:
                if "last_status_error" not in kwargs:
                    kwargs["last_status_error"] = None
            self._validate_state_transition(item, status)
        if 'meta' in kwargs:
            kwargs['meta'] = self._handle_type_meta(item.type, kwargs['meta'])
            kwargs['meta'] = self._get_encrypted_meta(**kwargs)
        return super().edit(item_id, **kwargs)


class BIAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return BIController


class OrganizationBIController(BIController, OrganizationValidatorMixin,
                               BaseController):
    """
    Controller for /restapi/v2/organizations/{id}/bi
    """

    def _get_model_type(self) -> type:
        return OrganizationBI

    def list(self, organization_id: str = None, **kwargs) -> List[OrganizationBI]:
        if organization_id:
            self.check_organization(organization_id)
            return super().list(organization_id=organization_id)
        else:
            return super().list()

    def create(self, organization_id: str, **kwargs) -> OrganizationBI:
        self.check_organization(organization_id)
        if not kwargs.get("name"):
            org = self.get_organization(organization_id)
            if not org:
                raise NotFoundException(
                    Err.OE0002, ['organization', organization_id])
            kwargs["name"] = org.name
        kwargs["meta"] = self._handle_type_meta(kwargs["type"], kwargs["meta"])
        kwargs["meta"] = self._get_encrypted_meta(**kwargs)
        return super().create(organization_id=organization_id, **kwargs)

    def delete_bis_for_org(self, organization_id) -> None:
        bis = self.list(organization_id)
        for bi in bis:
            self.delete(bi.id)


class OrganizationBIAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self) -> type:
        return OrganizationBIController
