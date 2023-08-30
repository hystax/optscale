import logging
from sqlalchemy import exists, and_
from tools.optscale_exceptions.common_exc import NotFoundException, ConflictException
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.organization import OrganizationController
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.enums import WebhookObjectTypes, WebhookActionTypes
from rest_api.rest_api_server.models.models import Webhook, Organization
from rest_api.rest_api_server.utils import convert_to_safe_filename

LOG = logging.getLogger(__name__)


class WebhookController(BaseController, MongoMixin):
    def _get_model_type(self):
        return Webhook

    @property
    def webhook_logs_collection(self):
        return self.mongo_client.restapi.webhook_logs

    def _get_environment_object(self, item_id):
        return next(self.resources_collection.find({
            '_id': item_id,
            'deleted_at': 0,
            'shareable': True
        }), None)

    def _get_object(self, object_id, object_type):
        object_get_func_map = {
            WebhookObjectTypes.ENVIRONMENT: self._get_environment_object
        }
        return object_get_func_map[object_type](object_id)

    def validate_hook_object(self, webhook):
        obj = self._get_object(webhook.object_id, webhook.object_type)
        if not obj:
            raise NotFoundException(
                Err.OE0002, [webhook.object_type.value, webhook.object_id])

    def _validate(self, item, is_new=True, **kwargs):
        if not self._is_organization_exists(item.organization_id):
            raise NotFoundException(
                Err.OE0002, [Organization.__name__, item.organization_id])
        query = self.session.query(exists().where(
            and_(*(item.get_uniqueness_filter(is_new)))))
        webhook_exist = query.scalar()
        if webhook_exist:
            raise ConflictException(
                Err.OE0503, [item.action, item.object_id])
        self.validate_hook_object(item)

    def _is_organization_exists(self, organization_id):
        return self.session.query(
            exists().where(and_(
                Organization.id == organization_id,
                Organization.deleted.is_(False)
            ))
        ).scalar()

    def get_logs(self, webhook_id):
        webhook = self.get(webhook_id)
        action_map = {
            WebhookActionTypes.BOOKING_ACQUIRE: 'acquire',
            WebhookActionTypes.BOOKING_RELEASE: 'release'
        }
        obj = self._get_object(webhook.object_id, webhook.object_type)
        action_value = action_map.get(webhook.action)
        obj_name = obj.get('name')
        safe_name = convert_to_safe_filename(obj_name) or obj.get(
            'cloud_resource_id')
        filename = 'audit_log_%s_%s' % (action_value, safe_name)
        logs = list(self.webhook_logs_collection.find(
            {'webhook_id': webhook_id}
        ).sort('execution_time'))
        return filename, logs


class WebhookAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return WebhookController
