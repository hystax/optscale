from rest_api_server.controllers.organization import OrganizationAsyncController
from rest_api_server.handlers.v1.base_async import (BaseAsyncCollectionHandler,
                                                    BaseAsyncItemHandler)
from rest_api_server.handlers.v1.base import BaseAuthHandler


class OrganizationAsyncCollectionHandler(BaseAsyncCollectionHandler,
                                         BaseAuthHandler):
    def _get_controller_class(self):
        return OrganizationAsyncController


class OrganizationAsyncItemHandler(BaseAsyncItemHandler, BaseAuthHandler):
    def _get_controller_class(self):
        return OrganizationAsyncController

    async def patch(self, id, **kwargs):
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('EDIT_PARTNER', 'organization', id)
        await super().patch(id, **kwargs)

    async def delete(self, id, **kwargs):
        if not self.check_cluster_secret(raises=False):
            await self.check_permissions('DELETE_PARTNER', 'organization', id)
        await super().delete(id, **kwargs)
