import logging
from collections import OrderedDict
from bumiworker.bumiworker.modules.base import ServiceBase
from bumiworker.bumiworker.modules.module import get_email_module_name

ROUTING_KEY = 'organization.recommendation.saving_spike'

LOG = logging.getLogger(__name__)


class SavingSpikeNotification(ServiceBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            "threshold": {'default': 10},
            "skip_notifications": {'default': False}
        })

    def _get(self):
        (threshold, skip_notifications) = self.get_options_values()
        if skip_notifications:
            LOG.info('Skip notifications for organization %s',
                     self.organization_id)
            return
        current_total = 0
        previous_total = 0
        modules_data = []
        created_at = self.mongo_client.restapi['checklists'].aggregate([
            {'$match': {"organization_id": self.organization_id}},
            {'$group': {'_id': '$created_at'}},
            {'$sort': {'_id': -1}},
            {'$limit': 2}
        ])
        pipeline = [
            {"$match": {"organization_id": self.organization_id,
                        "created_at": {"$in": [x['_id'] for x in created_at]}}},
            {"$unwind": "$data"},
            {"$match": {"data.is_excluded": {"$ne": True},
                        "data.is_dismissed": {"$ne": True},
                        "data.saving": {"$exists": True}}},
            {"$group": {"_id": {"created_at": "$created_at",
                                "module": "$module"},
                        "data": {"$addToSet": "$data"}}}
        ]
        results = self.mongo_client.restapi['checklists'].aggregate(
            pipeline)
        for r in results:
            opt = r.get('data', [])
            module = r['_id']['module']
            total = sum([item.get('saving', 0) for item in opt])
            if r['_id']['created_at'] == self.created_at:
                module_name = get_email_module_name(module)
                current_total += total
                modules_data.append({'module': module_name,
                                     'count': len(opt),
                                     'saving': total})
            else:
                previous_total += total
        if current_total > previous_total + previous_total * threshold / 100:
            LOG.info(
                'Found saving spike for organization %s. Previous total: %s, '
                'current total: %s', self.organization_id, previous_total,
                current_total)
            modules_data.sort(key=lambda x: x['saving'], reverse=True)
            task = {
                "object_id": self.organization_id,
                "object_type": "organization",
                "action": "saving_spike",
                "meta": {"previous_total": previous_total,
                         "current_total": current_total,
                         "top3": modules_data[:3]}
            }
            self._publish_activities_tasks([task], ROUTING_KEY)


def main(organization_id, config_client, created_at, **kwargs):
    return SavingSpikeNotification(
        organization_id, config_client, created_at).get()
