from katara.katara_worker.reports_generators.base import Base


class PoolExceedResources(Base):
    def generate(self):
        user_id = self.report_data.get('user_id')
        _, organization = self.rest_cl.organization_get(self.organization_id)
        exceeded_pools_keys = [
            'exceeded_pools', 'exceeded_pool_forecasts']
        _, tasks = self.rest_cl.my_tasks_get(
            self.organization_id, user_id=user_id,
            types=exceeded_pools_keys)
        result = {}
        exceeded_pools_ids = []
        for exceeded_pools_key in exceeded_pools_keys:
            exceeded_pools = {
                x['pool_id']: x for x in tasks.get(
                    exceeded_pools_key, {}).get('tasks', [])
            }
            result[exceeded_pools_key] = exceeded_pools
            exceeded_pools_ids.extend(exceeded_pools.keys())
        _, employees = self.rest_cl.employee_list(self.organization_id)
        employee = next(x for x in list(employees['employees'])
                        if x['auth_user_id'] == user_id)
        for res_type in ['instance', 'volume', 'snapshot', 'bucket']:
            _, response = self.rest_cl.cloud_resources_discover(
                self.organization_id, res_type, {
                    'owner_id': [employee['id']],
                    'pool_id': exceeded_pools_ids
                })
            data = response.get('data', [])
            for resource in data:
                pool_id = resource['pool_id']
                for exceeded_pools_key in exceeded_pools_keys:
                    exceeded_pools = result[exceeded_pools_key]
                    exceeded_pool = exceeded_pools.get(pool_id)
                    if exceeded_pool:
                        if not exceeded_pool.get('resources'):
                            exceeded_pool['resources'] = []
                            exceeded_pool['total_expenses'] = round(
                                exceeded_pool['total_expenses'], 2)
                        resource['type'] = res_type
                        if not resource.get('name'):
                            resource.update({'name': ''})
                        exceeded_pool['resources'].append(resource)
        exceeded_pools = [pool for pool in result[
            'exceeded_pools'].values() if pool.get('resources')]
        exceeded_pool_forecasts = [pool for pool in result[
            'exceeded_pool_forecasts'].values() if pool.get('resources')]
        if not exceeded_pools and not exceeded_pool_forecasts:
            return
        return {
            'email': [self.report_data['user_email']],
            'template_type': 'pool_exceed_resources_report',
            'subject': 'Action Required: Hystax OptScale Pool Limit '
                       'Exceed Alert',
            'template_params': {
                'texts': {
                    'organization': {
                        'name': organization['name'],
                        'currency_code': self.get_currency_code(
                            organization['currency'])
                    },
                    'exceeded_pools': exceeded_pools,
                    'exceeded_pool_forecasts': exceeded_pool_forecasts,
                    "exceeded_pool_forecasts_count": len(
                        exceeded_pool_forecasts),
                    "exceeded_pools_count": len(exceeded_pools)
                }
            }
        }


def main(organization_id, report_data, config_client):
    return PoolExceedResources(
        organization_id, report_data, config_client).generate()
