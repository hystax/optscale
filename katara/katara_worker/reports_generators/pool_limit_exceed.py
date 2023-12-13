from katara.katara_worker.reports_generators.base import Base


class PoolExceed(Base):
    def generate(self):
        user_id = self.report_data.get('user_id')
        _, organization = self.rest_cl.organization_get(self.organization_id)
        exceeded_pools_keys = [
            'exceeded_pools', 'exceeded_pool_forecasts']
        _, tasks = self.rest_cl.my_tasks_get(
            self.organization_id, user_id=user_id,
            types=exceeded_pools_keys)
        _, cloud_accs = self.rest_cl.cloud_account_list(self.organization_id,
                                                        details=True)
        organization_total_cost = 0
        organization_forecast = 0
        for cloud_acc in cloud_accs['cloud_accounts']:
            details = cloud_acc['details']
            organization_total_cost += details['cost']
            organization_forecast += details['forecast']
        exceeded = []
        for exceeded_pools_key in exceeded_pools_keys:
            exceeded_pools = [
                {
                    'id': x['pool_id'],
                    'limit': x['limit'],
                    'total_expenses': round(x['total_expenses'], 2),
                    'pool_name': x['pool_name'],
                    'forecast': x['forecast']
                } for x in tasks.get(exceeded_pools_key, {}).get('tasks', [])
            ]
            exceeded.extend(exceeded_pools)
        if not exceeded:
            return
        return {
            'email': [self.report_data['user_email']],
            'template_type': 'pool_exceed_report',
            'subject': 'Action Required: Hystax OptScale Pool Limit '
                       'Exceed Alert',
            'template_params': {
                'texts': {
                    'organization': {
                        'id': organization['id'],
                        'name': organization['name'],
                        'currency_code': self.get_currency_code(
                            organization['currency'])
                    },
                    'user': self.report_data,
                    'exceeded': exceeded,
                    'title': 'Pool Limit Exceed Alert',
                    'total_cost': round(organization_total_cost, 2),
                    'total_forecast': round(organization_forecast, 2)
                }
            }
        }


def main(organization_id, report_data, config_client):
    return PoolExceed(organization_id, report_data, config_client).generate()
