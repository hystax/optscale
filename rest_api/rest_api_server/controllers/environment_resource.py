import hashlib
import logging
from datetime import datetime

from sqlalchemy import and_

from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.cloud_account import CloudAccountController
from rest_api.rest_api_server.controllers.cloud_resource import CloudResourceController
from rest_api.rest_api_server.controllers.cost_model import ResourceBasedCostModelController
from rest_api.rest_api_server.controllers.pool_alert import PoolAlertController
from rest_api.rest_api_server.controllers.shareable_resource import ShareableBookingController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import CloudTypes, ThresholdBasedTypes
from rest_api.rest_api_server.models.models import (Organization, CloudAccount)

from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)

LOG = logging.getLogger(__name__)


class EnvironmentResourceController(CloudResourceController,
                                    ShareableBookingController):
    @staticmethod
    def get_split_fields():
        return {'cloud_account_id', 'cloud_resource_id', 'pool_id',
                'employee_id', 'created_at', 'deleted_at', '_id',
                'applied_rules', 'cluster_id', 'cluster_type_id',
                'name', 'is_environment', 'shareable'}

    @staticmethod
    def get_validation_parameters(resource_type):
        required_fields = {
            'cloud_resource_id', 'resource_type', 'cloud_account_id', 'name'
        }
        immutable_params = {
            'created_at', 'deleted_at', 'id', '_id', 'is_environment',
            'shareable'
        }
        optional_params = {
            'employee_id', 'pool_id', 'tags', 'first_seen',
            'last_seen', 'active', 'env_properties', 'service_name', 'ssh_only'
        }
        return (required_fields, immutable_params,
                optional_params, set())

    def get_set_status_func(self, resource_type):
        pass

    def check_cloud_account_exists(self, value):
        if not isinstance(value, list):
            value = [value]
        ca_ids = self.session.query(CloudAccount.id).filter(and_(
            CloudAccount.id.in_(value),
            CloudAccount.deleted.is_(False),
            CloudAccount.type == CloudTypes.ENVIRONMENT
        )).all()
        diff = set(value) - {x[0] for x in ca_ids}
        if diff:
            raise NotFoundException(
                Err.OE0002, [CloudAccount.__name__, diff.pop()])

    def get(self, item_id, include_deleted=False, **kwargs):
        obj = super().get(item_id, include_deleted)
        if not obj.get('shareable'):
            raise NotFoundException(Err.OE0002, ['Resource', item_id])
        return obj

    def edit(self, item_id, **kwargs):
        item = self.get(item_id)
        edited_env = super().edit(item_id, **kwargs)
        if item['active'] != edited_env['active']:
            cloud_account_id = edited_env['cloud_account_id']
            organization_id = CloudAccountController(
                self.session, self._config, self.token).get(
                    cloud_account_id).organization_id
            state = {
                True: 'activated',
                False: 'deactivated'
            }
            meta = {
                'state': state[edited_env['active']],
                'object_name': edited_env.get('name')
            }
            self.publish_activities_task(
                organization_id, item_id, 'environment', 'env_power_mngmt',
                meta, 'environment.env_power_mngmt')
        return edited_env

    def get_environment_account(self, organization_id, no_create=False):
        return CloudAccountController(
            self.session, self._config, self.token
        ).get_or_create_environment_cloud_account(organization_id, no_create)

    def check_entity_exists(self, entity_id, model):
        try:
            super().check_entity_exists(entity_id, model)
        except WrongArgumentsException:
            raise NotFoundException(
                Err.OE0002, [model.__name__, entity_id])

    def list_org_environments(self, organization_id):
        self.check_entity_exists(organization_id, Organization)
        # env acc shouldn't be created
        cloud_account = self.get_environment_account(
            organization_id, no_create=True)
        if not cloud_account:
            return []
        return self.list(
            is_environment=True, cloud_account_id=cloud_account.id,
            include_deleted=False)

    def create(self, organization_id, **kwargs):
        self.check_entity_exists(organization_id, Organization)
        cloud_account = self.get_environment_account(organization_id)
        contains_shareable_resources = self.contains_shareable_resource(
            organization_id)
        result = self.save_bulk(
            cloud_account_id=cloud_account.id,
            behavior='error_existing',
            return_resources=True,
            resources=[kwargs],
            new_environment=True
        )
        resource = result.pop()
        ResourceBasedCostModelController(
            self.session, self._config
        ).create(resource['id'], organization_id)
        if resource.get('env_properties'):
            pool_alerts_map = PoolAlertController(
                self.session, self._config, self.token).get_pool_alerts_map(
                [resource['pool_id']], ThresholdBasedTypes.ENV_CHANGE)
            pool_id = resource['pool_id']
            if pool_alerts_map.get(resource['pool_id']):
                changed_properties_list = []
                for prop_key, prop_value in resource['env_properties'].items():
                    changed_properties_list.append({
                        'name': prop_key,
                        'previous_value': '-',
                        'new_value': prop_value
                    })
                for alert_id in pool_alerts_map[pool_id]:
                    meta = {
                        'alert_id': alert_id,
                        'env_properties': changed_properties_list
                    }
                    self.publish_activities_task(
                        organization_id, resource['id'], 'resource',
                        'env_property_updated', meta,
                        'alert.violation.env_change')

        if contains_shareable_resources is False:
            self.send_first_shareable_email(organization_id)
        return resource

    @staticmethod
    def gen_cloud_resource_ids(resources):
        def get_cloud_resource_id(r):
            tail = "%s%s" % (r.get('name'), r.get('resource_type'))
            return 'environment_%s' % hashlib.md5(
                tail.encode('utf-8')).hexdigest()

        for resource in resources:
            if resource.get('cloud_resource_id'):
                raise WrongArgumentsException(
                    Err.OE0211, ['cloud_resource_id'])
            resource['cloud_resource_id'] = get_cloud_resource_id(resource)
        return resources

    def extend_payload(self, resource, now):
        defaults = {
            'region': None,
            'is_environment': True,
            'active': resource.get('active', True),
            'shareable': True,
            'ssh_only': resource.get('ssh_only', False)
        }
        resource.update(defaults)
        if not resource.get('tags'):
            resource['tags'] = {}
        return super().extend_payload(resource, now)

    def delete(self, item_id):
        ResourceBasedCostModelController(
            self.session, self._config
        ).delete(item_id)
        # if environment was deleted then we delete all its bookings
        self.delete_bookings(item_id)
        self.resources_collection.update_one(
            filter={
                '_id': item_id,
                'is_environment': True
            },
            update={'$set': {'deleted_at': int(datetime.utcnow().timestamp())}}
        )


class EnvironmentResourceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return EnvironmentResourceController
