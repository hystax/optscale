import logging
from collections import OrderedDict
from bumi_worker.modules.base import ServiceBase
from bumi_worker.modules.module import get_email_module_name

ROUTING_KEY = 'organization.recommendation.new_security_recommendation'

LOG = logging.getLogger(__name__)
MODULE_UNIQUE_FIELDS = {
            'inactive_users': ['cloud_account_id', 'user_id'],
            'inactive_console_users': ['cloud_account_id', 'user_id'],
            's3_public_buckets': ['resource_id'],
            'insecure_security_groups': ['resource_id']
}


class SecurityOptimizationNotification(ServiceBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'skip_security_notification': {'default': False}
        })

    def _get(self):
        result = []
        skip_notification_option_tuple = self.get_options_values()
        if not skip_notification_option_tuple[0]:
            for module, unique_fields in MODULE_UNIQUE_FIELDS.items():
                count = 0
                current_run_result = []
                previous_run_result = []
                pipeline = [{"$match": {
                                "module": module,
                                "organization_id": self.organization_id}},
                            {"$sort": {"created_at": -1}},
                            {"$limit": 2}]
                results = self.mongo_client.restapi['checklists'].aggregate(
                    pipeline)
                for r in results:
                    run_result = [tuple(item[f] for f in unique_fields)
                                  for item in r.get('data', [])
                                  if isinstance(item, dict) and
                                  not item.get('is_excluded')]
                    if r['created_at'] == self.created_at:
                        current_run_result = run_result
                    else:
                        previous_run_result = run_result
                for r_unique_values in current_run_result:
                    if r_unique_values not in previous_run_result:
                        count += 1
                if count > 0:
                    module_name = get_email_module_name(module)
                    result.append({'module': module_name, 'count': count})
        if result:
            LOG.info(f'Found new security recommendations for organization '
                     f'{self.organization_id}: {result}')
            task = {
                "organization_id": self.organization_id,
                "object_id": self.organization_id,
                "object_type": "organization",
                "action": "new_security_recommendation",
                "meta": result
            }
            self._publish_activities_tasks([task], ROUTING_KEY)


def main(organization_id, config_client, created_at, **kwargs):
    return SecurityOptimizationNotification(
        organization_id, config_client, created_at).get()
