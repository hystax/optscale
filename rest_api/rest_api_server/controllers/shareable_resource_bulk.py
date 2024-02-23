from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.controllers.shareable_resource import ShareableBookingController
from rest_api.rest_api_server.exceptions import Err


class ShareableResourceBulkController(ShareableBookingController):
    def _sharing_failed_response(self, not_shared_ids,
                                 invalid_ids=None,
                                 not_active_ids=None):
        failed = []
        for resource in not_shared_ids:
            failed.append({
                "id": resource[0],
                "message": Err.OE0478.value[0] % resource[1],
                "code": Err.OE0478.name})
        for resource in invalid_ids:
            failed.append({
                "id": resource[0],
                "message": Err.OE0412.value[0] % resource[1],
                "code": Err.OE0412.name})
        for resource in not_active_ids:
            failed.append({
                "id": resource[0],
                "message": Err.OE0443.value[0] % resource[1],
                "code": Err.OE0443.name})
        return failed

    def make_resources_shareable(self, resources_ids):
        if resources_ids:
            self.resources_collection.update_many(
                filter={'_id': {
                    '$in': resources_ids},
                },
                update={'$set': {'shareable': True}}
            )

    def bulk_share(self, organization_id, resource_ids):
        def extract_resource_id_list(r_list):
            return [(
                res['id'],
                res.get('cloud_resource_id') or res.get('cloud_resource_hash')
            ) for res in r_list]

        result = {}
        resources, invalid_res, not_active_res = self._check_resources(
            organization_id, resource_ids)
        to_share, not_to_share, shareable = self.split_resources_by_shareability(
            resources)
        share_ids = [res['id'] for res in to_share]
        contains_shareable_resources = self.contains_shareable_resource(
            organization_id)
        self.make_resources_shareable(share_ids)
        result['succeeded'] = share_ids
        for res in shareable:
            result['succeeded'].append(res['id'])

        not_to_share_ids = extract_resource_id_list(not_to_share)
        invalid_resources_ids = extract_resource_id_list(invalid_res)
        not_active_ids = extract_resource_id_list(not_active_res)
        result['failed'] = self._sharing_failed_response(
            not_to_share_ids, invalid_resources_ids, not_active_ids)
        if contains_shareable_resources is False and share_ids:
            self.send_first_shareable_email(organization_id, len(share_ids))
        return result


class ShareableResourceBulkAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return ShareableResourceBulkController
