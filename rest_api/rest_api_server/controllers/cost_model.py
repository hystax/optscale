import json
import logging

from sqlalchemy import and_, exists

from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.report_import import (
    ExpensesRecalculationScheduleController)
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import CostModelTypes, CloudTypes
from rest_api.rest_api_server.models.models import (
    CostModel, Organization, CloudAccount)

from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)

ENV_DEFAULT_HOURLY_COST = 0.05
K8S_DEFAULT_CPU_HOURLY_COST = 0.002
K8S_DEFAULT_MEMORY_HOURLY_COST = 0.001
LOG = logging.getLogger(__name__)


class CostModelController(BaseController):
    @property
    def cost_model_type(self):
        raise NotImplementedError()

    def _get_model_type(self):
        return CostModel

    def _get_default_cost_model(self):
        raise NotImplementedError()

    def _get_validation_map(self):
        raise NotImplementedError()

    def _is_organization_exists(self, organization_id):
        return self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()

    def get_cloud_account(self, cloud_account_id):
        return self.session.query(CloudAccount).filter(
            and_(
                CloudAccount.id == cloud_account_id,
                CloudAccount.deleted.is_(False)
            )
        ).one_or_none()

    @staticmethod
    def _validate_model(model_params, cost_model):
        if cost_model is None:
            raise WrongArgumentsException(Err.OE0216, ['value'])
        if not isinstance(cost_model, dict):
            raise WrongArgumentsException(Err.OE0344, ['value'])
        if len(model_params) != len(cost_model):
            unexpected = list(map(lambda x: 'value.%s' % x,
                                  filter(lambda x: x not in model_params.keys(),
                                         cost_model.keys())))
            raise WrongArgumentsException(Err.OE0212, [unexpected])
        for param, supported_types in model_params.items():
            if cost_model.get(param) is None:
                raise WrongArgumentsException(Err.OE0216, ['value.%s' % param])
            if not any(map(lambda x: isinstance(
                    cost_model.get(param), x), supported_types)):
                raise WrongArgumentsException(Err.OE0466, ['value.%s' % param])

    def _validate(self, item, is_new=True, **kwargs):
        if is_new:
            organization_id = kwargs.get('organization_id')
            if not self._is_organization_exists(organization_id):
                raise NotFoundException(
                    Err.OE0002, [Organization.__name__, organization_id])
            try:
                CostModelTypes(kwargs.get('type'))
            except ValueError:
                raise WrongArgumentsException(Err.OE0217, ['type'])

            self.get_cloud_account(item.id)

    def list(self, organization_id):
        if not self._is_organization_exists(organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, organization_id])
        return super().list(organization_id=organization_id)

    def create(self, id, organization_id, value, **kwargs):
        validation_params = self._get_validation_map()
        self._validate_model(validation_params, value)
        return super().create(id=id, organization_id=organization_id,
                              type=self.cost_model_type.value,
                              value=json.dumps(value))

    def edit(self, item_id, **kwargs):
        c_model = self.get(item_id)
        validation_params = self._get_validation_map()
        value = kwargs.pop('value', None)
        self._validate_model(validation_params, value)
        value_changed = False
        if value and c_model.loaded_value != value:
            value_changed = True
        cost_model = super().edit(item_id, value=json.dumps(value), **kwargs)
        if value_changed:
            self.schedule_recalculation(item_id)
        return cost_model

    def get(self, item_id, **kwargs):
        self.get_cloud_account(item_id)
        kwargs['type'] = self.cost_model_type
        return super().get(item_id, **kwargs)

    def delete(self, item_id):
        self.get_cloud_account(item_id)
        return super().delete(item_id)

    def get_cloud_account_id(self, item_id):
        raise NotImplementedError

    def schedule_recalculation(self, item_id):
        cloud_account_id = self.get_cloud_account_id(item_id)
        ExpensesRecalculationScheduleController(
            self.session, self._config).schedule(cloud_account_id)


class CloudBasedCostModelController(CostModelController):
    @property
    def cost_model_type(self):
        return CostModelTypes.CLOUD_ACCOUNT

    @property
    def related_cloud_type(self):
        return CloudTypes.KUBERNETES_CNR

    def _get_validation_map(self):
        return {
            'cpu_hourly_cost': [float, int],
            'memory_hourly_cost': [float, int],
        }

    def get_cloud_account_id(self, item_id):
        return item_id

    def _get_default_cost_model(self):
        return {
            'cpu_hourly_cost': K8S_DEFAULT_CPU_HOURLY_COST,
            'memory_hourly_cost': K8S_DEFAULT_MEMORY_HOURLY_COST
        }

    def get_cloud_account(self, cloud_account_id):
        cloud_acc = super().get_cloud_account(cloud_account_id)
        if not cloud_acc:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, cloud_account_id])
        if cloud_acc.type != self.related_cloud_type:
            raise WrongArgumentsException(Err.OE0436, [cloud_acc.type.value])
        return cloud_acc

    def create(self, id, organization_id, value, **kwargs):
        if not value:
            value = self._get_default_cost_model()
        if kwargs:
            message = ', '.join(kwargs)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OE0212, [kwargs])
        return super().create(id=id, organization_id=organization_id,
                              value=value)


class ResourceBasedCostModelController(CloudBasedCostModelController,
                                       MongoMixin):
    @property
    def cost_model_type(self):
        return CostModelTypes.RESOURCE

    @property
    def related_cloud_type(self):
        return CloudTypes.ENVIRONMENT

    def get_cloud_account_id(self, item_id):
        ca = self.get_cloud_account(item_id)
        return ca.id

    def _get_validation_map(self):
        return {
            'hourly_cost': [float, int]
        }

    def _get_default_cost_model(self):
        return {
            'hourly_cost': ENV_DEFAULT_HOURLY_COST
        }

    def _get_resource(self, resource_id):
        return next(self.resources_collection.find(
            {'_id': resource_id, 'deleted_at': 0}), None)

    def get_cloud_account(self, resource_id):
        resource = self._get_resource(resource_id)
        if not resource:
            raise NotFoundException(
                Err.OE0002, ['resource', resource_id])
        cloud_account_id = resource.get('cloud_account_id')
        if not cloud_account_id:
            raise WrongArgumentsException(Err.OE0474, [])
        cloud_acc = super().get_cloud_account(cloud_account_id)
        return cloud_acc

    def create(self, resource_id, organization_id, **kwargs):
        if kwargs:
            message = ', '.join(kwargs)
            LOG.warning('Unexpected parameters %s: %s' %
                        (self.model_type, message))
            raise WrongArgumentsException(Err.OE0212, [kwargs])
        return super().create(id=resource_id, organization_id=organization_id,
                              value=self._get_default_cost_model())


class CostModelAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CostModelController


class CloudBasedAsyncCostModelController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return CloudBasedCostModelController


class ResourceBasedAsyncCostModelController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ResourceBasedCostModelController
