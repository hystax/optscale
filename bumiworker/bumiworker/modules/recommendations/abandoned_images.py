import logging
from collections import OrderedDict
from datetime import datetime, timedelta
from bumiworker.bumiworker.modules.abandoned_base import AbandonedBase

LOG = logging.getLogger(__name__)

DEFAULT_DAYS_THRESHOLD = 7
BULK_SIZE = 1000
SUPPORTED_CLOUD_TYPES = [
    'nebius'
]


class AbandonedImages(AbandonedBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []}
        })

    def get_last_used_map(self, cloud_account_id, image_ids):
        images = self.mongo_client.restapi.resources.aggregate([
            {
                '$match': {'$and': [
                    {'cloud_account_id': cloud_account_id},
                    {'resource_type': 'Volume'},
                    {'meta.image_id': {'$in': image_ids}}
                ]},
            },
            {
                '$group': {
                    '_id': '$meta.image_id',
                    'last_used': {'$max': '$last_seen'}
                }
            }
        ])
        return {i['_id']: i['last_used'] for i in images}

    def _get(self):
        (days_threshold, excluded_pools,
         skip_cloud_accounts) = self.get_options_values()
        cloud_account_map = self.get_cloud_accounts(
            SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        cloud_accounts = list(cloud_account_map.values())
        cloud_accounts_ids = list(cloud_account_map.keys())
        starting_point = datetime.utcnow() - timedelta(days=days_threshold)
        employees = self.get_employees()
        pools = self.get_pools()

        images_by_account = self.get_active_resources(
            cloud_accounts_ids, starting_point, 'Image')

        result = []
        for account in cloud_accounts:
            cloud_account_id = account['id']
            account_images = images_by_account[cloud_account_id]
            if account_images:
                cloud_resource_image_map = {
                    account_image['cloud_resource_id']: account_image
                    for account_image in account_images}
                last_used_map = self.get_last_used_map(
                    cloud_account_id, list(cloud_resource_image_map.keys()))
                matched_cloud_id_res_id_map = {}
                for image in account_images:
                    last_used = last_used_map.get(image['cloud_resource_id'], 0)
                    if last_used >= starting_point.timestamp():
                        continue
                    matched_cloud_id_res_id_map[
                        image['cloud_resource_id']] = image['_id']

                expenses = self.get_month_saving_by_daily_avg_expenses(
                    list(matched_cloud_id_res_id_map.values()), starting_point)

                for cloud_res_id in list(matched_cloud_id_res_id_map.keys()):
                    image = cloud_resource_image_map[cloud_res_id]
                    image_id = image['_id']
                    saving = expenses.get(image_id, 0)
                    if saving > 0:
                        result.append({
                            'cloud_resource_id': image['cloud_resource_id'],
                            'resource_name': image.get('name'),
                            'resource_id': image_id,
                            'cloud_account_id': image['cloud_account_id'],
                            'cloud_type': account['type'],
                            'folder_id': image['meta']['folder_id'],
                            'last_used': last_used_map.get(
                                image['cloud_resource_id'], 0),
                            'first_seen': image['first_seen'],
                            'saving': saving,
                            'owner': self._extract_owner(
                                image.get('employee_id'), employees),
                            'pool': self._extract_pool(
                                image.get('pool_id'), pools),
                            'is_excluded': image.get('pool_id') in excluded_pools,
                        })
        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AbandonedImages(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Abandoned Images'
