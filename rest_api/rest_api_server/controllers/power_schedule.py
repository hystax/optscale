import logging
from datetime import datetime, timezone
from sqlalchemy.sql import and_, exists
from tools.optscale_exceptions.common_exc import (
    ConflictException, WrongArgumentsException, NotFoundException)
from rest_api.rest_api_server.controllers.base import (
    BaseController, OrganizationValidatorMixin, MongoMixin,
    ResourceFormatMixin)
from rest_api.rest_api_server.controllers.base_async import (
    BaseAsyncControllerWrapper)
from rest_api.rest_api_server.controllers.cloud_resource import (
    CloudResourceController
)
from rest_api.rest_api_server.models.models import PowerSchedule
from rest_api.rest_api_server.exceptions import Err

LOG = logging.getLogger(__name__)


class PowerScheduleController(BaseController, OrganizationValidatorMixin,
                              MongoMixin, ResourceFormatMixin):
    def _get_model_type(self):
        return PowerSchedule

    def _validate(self, item, is_new=True, **kwargs):
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        ps_exists = query.scalar()
        if ps_exists:
            raise ConflictException(Err.OE0149, [
                self.model_type.__name__, kwargs['name']])
        if (item.end_date and item.start_date and
                item.start_date >= item.end_date):
            raise WrongArgumentsException(
                Err.OE0541, ['start_date', 'end_date'])
        if item.power_on == item.power_off:
            raise WrongArgumentsException(
                Err.OE0552, ['power_on', 'power_off'])
        now = int(datetime.now(tz=timezone.utc).timestamp())
        end_date = kwargs.get('end_date')
        if isinstance(end_date, int) and end_date < now:
            raise WrongArgumentsException(Err.OE0461, ['end_date'])

    def _set_resources(self, power_schedule, show_resources=False):
        resources = list(self.resources_collection.find(
            {'power_schedule': power_schedule['id']}))
        power_schedule['resources_count'] = len(resources)
        if show_resources:
            power_schedule['resources'] = []
            res_ctrl = CloudResourceController(
                self.session, self._config, self.token)
            for resource in resources:
                resource = self.format_resource(resource)
                resource.update(
                    {'details': res_ctrl.get_resource_details(resource)})
                power_schedule['resources'].append(resource)

    def create(self, organization_id: str, **kwargs):
        self.check_organization(organization_id)
        start_date = kwargs.get('start_date')
        if start_date is None:
            kwargs['start_date'] = int(datetime.now(timezone.utc).timestamp())
        power_schedule = super().create(
            organization_id=organization_id, **kwargs).to_dict()
        power_schedule['resources_count'] = 0
        return power_schedule

    def list(self, organization_id: str, **kwargs):
        if organization_id:
            self.check_organization(organization_id)
        result = []
        ps_list = super().list(organization_id=organization_id)
        for ps in ps_list:
            ps = ps.to_dict()
            self._set_resources(ps, show_resources=False)
            result.append(ps)
        return result

    def get_item(self, item_id: str):
        item = super().get(item_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, item_id])
        item = item.to_dict()
        self._set_resources(item, show_resources=True)
        return item

    def edit(self, item_id: str, **kwargs):
        item = super().get(item_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, item_id])
        schedule = super().edit(item_id, **kwargs).to_dict()
        self._set_resources(schedule, show_resources=True)
        return schedule

    def bulk_action(self, power_schedule_id: str, data: dict):
        item = super().get(power_schedule_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, power_schedule_id])
        action = data['action']
        instance_ids = data['instance_id']
        resources = self.resources_collection.find(
            {'_id': {'$in': instance_ids}, 'resource_type': 'Instance',
             'active': True}, ['_id'])
        res_exist = [x['_id'] for x in resources]
        if res_exist and action == 'attach':
            self.resources_collection.update_many(
                {'_id': {'$in': res_exist}},
                {'$set': {'power_schedule': power_schedule_id}})
        elif res_exist and action == 'detach':
            self.resources_collection.update_many(
                {'_id': {'$in': res_exist}},
                {'$unset': {'power_schedule': 1}})
        failed = [x for x in instance_ids if x not in res_exist]
        return {
            'failed': failed,
            'succeeded': res_exist
        }

    def delete(self, power_schedule_id):
        item = super().get(power_schedule_id)
        if not item:
            raise NotFoundException(
                Err.OE0002, [self.model_type.__name__, power_schedule_id])
        self.resources_collection.update_many(
            {'power_schedule': power_schedule_id},
            {'$unset': {'power_schedule': 1}})
        super().delete(power_schedule_id)


class PowerScheduleAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self) -> type:
        return PowerScheduleController
