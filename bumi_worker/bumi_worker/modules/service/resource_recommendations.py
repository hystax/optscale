from pymongo import UpdateOne
from bumi_worker.modules.base import ServiceBase


class ResourceRecommendations(ServiceBase):
    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.modules_without_saving = {'insecure_security_groups',
                                       's3_public_buckets'}
        self.modules_with_possible_zero_saving = {'instance_generation_upgrade'}

    def _get_recommendation_template(self):
        return {
            'run_timestamp': self.created_at,
            'modules': []
        }

    def _get(self):
        checklists = self.mongo_client.restapi['checklists'].find({
            'created_at': self.created_at,
            'organization_id': self.organization_id
        })
        recommendations_map = {}
        for r in checklists:
            data = r.get('data', {})
            if not isinstance(data, list):
                continue
            module_name = r.get('module')
            for d in data:
                resource_id = d.get('resource_id')
                saving = d.get('saving')
                if not resource_id or (
                        saving is None and module_name not in
                        self.modules_without_saving) or (
                        saving == 0 and module_name not in
                        self.modules_with_possible_zero_saving):
                    continue
                if not recommendations_map.get(resource_id):
                    recommendations_map[resource_id] = {}

                if d.get('is_excluded', False):
                    recommendation_key = 'excluded_recommendations'
                elif d.get('is_dismissed', False):
                    recommendation_key = 'dismissed_recommendations'
                else:
                    recommendation_key = 'recommendations'

                if not recommendations_map[resource_id].get(
                        recommendation_key):
                    recommendations_map[resource_id][
                        recommendation_key] = self._get_recommendation_template()
                d.update({'name': module_name})
                recommendations_map[resource_id][
                    recommendation_key]['modules'].append(d)
        if recommendations_map:
            self.mongo_client.restapi['resources'].bulk_write([
                UpdateOne(
                    filter={'_id': res_id},
                    update={
                        '$set': {
                            **recommendations
                        }
                    }
                ) for res_id, recommendations in recommendations_map.items()
            ])


def main(organization_id, config_client, created_at, **kwargs):
    return ResourceRecommendations(
        organization_id, config_client, created_at).get()
