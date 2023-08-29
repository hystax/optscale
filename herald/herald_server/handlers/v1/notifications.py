import json

from herald.herald_server.controllers.notification import NotificationAsyncController
from herald.herald_server.handlers.v1.base_async import (
    BaseAsyncCollectionHandler,
    BaseAsyncItemHandler
)
from herald.herald_server.handlers.v1.base import BaseAuthHandler
from herald.herald_server.utils import ModelEncoder


class UserNotificationAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                             BaseAuthHandler):
    def _get_controller_class(self):
        return NotificationAsyncController

    async def post(self, user_id):
        self.check_self_auth(user_id)
        await super().post(user_id=user_id)

    async def get(self, user_id):
        self.check_self_auth(user_id)
        notification_list = await self.controller.list(user_id)
        notification_dict = {'notifications': [
            notification.to_dict()
            for notification in notification_list]}
        self.write(json.dumps(notification_dict, cls=ModelEncoder))


class NotificationAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return NotificationAsyncController

    async def _check_notification_permissions(self, notification_id):
        notification = await self._get_item(notification_id)
        self.check_self_auth(notification.user_id)

    async def get(self, id, **kwargs):
        await self._check_notification_permissions(id)
        await super().get(id, **kwargs)

    async def patch(self, id, **kwargs):
        await self._check_notification_permissions(id)
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        await self._check_notification_permissions(id)
        await super().delete(id, **kwargs)
