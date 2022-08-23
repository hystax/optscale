import uuid
from calendar import monthrange
from datetime import datetime
from katara_worker.reports_generators.base import Base


class OrganizationExpenses(Base):
    @staticmethod
    def get_nil_uuid():
        return str(uuid.UUID(int=0))

    def generate(self):
        today = datetime.utcnow()
        start_date = today.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        start = int(start_date.timestamp())
        end = int(today.timestamp())

        _, org = self.rest_cl.organization_get(self.organization_id)
        _, org_pool_details = self.rest_cl.pool_get(
            org['pool_id'], details=True, children=True)
        pool_details = [org_pool_details] + org_pool_details.pop(
            'children', [])

        pools = []
        _, cloud_accs = self.rest_cl.cloud_account_list(self.organization_id,
                                                        details=True)
        organization_total_cost = 0
        organization_forecast = 0
        for cloud_acc in cloud_accs['cloud_accounts']:
            details = cloud_acc['details']
            organization_total_cost += details['cost']
            organization_forecast += details['forecast']

        for pool in pool_details:
            pools.append({
                'id': pool['id'],
                'name': pool['name'],
                'limit': pool['limit'],
            })
        for pool in pools:
            _, expenses = self.rest_cl.clean_expenses_get(
                self.organization_id, start, end, {'pool_id': pool['id']})
            pool['cost'] = round(sum(
                map(lambda x: x['cost'], expenses['clean_expenses'])), 2)
            pool['tracked'] = len(expenses['clean_expenses'])
            pool['forecast'] = self.get_monthly_forecast(pool['cost'])
        pools = sorted(pools, key=lambda i: i['cost'], reverse=True)

        _, unassigned_expenses = self.rest_cl.clean_expenses_get(
            self.organization_id, start, end,
            {'pool_id': self.get_nil_uuid()})

        st_dt_string = '{day}/{month}/{year}'.format(
            day=start_date.day, month=start_date.month, year=start_date.year)
        e_dt_string = '{day}/{month}/{year}'.format(
            day=today.day, month=today.month, year=today.year)
        return {
            'email': [self.report_data['user_email']],
            'template_type': 'weekly_expense_report',
            'subject': 'OptScale weekly expense report',
            'template_params': {
                'texts': {
                    'user': self.report_data,
                    'title': 'Weekly expense report',
                    'pools': pools,
                    'start_date': st_dt_string,
                    'end_date': e_dt_string,
                    'unassigned': {
                        'total_cost': round(
                            unassigned_expenses['total_cost'], 2),
                        'resources_tracked': len(
                            unassigned_expenses['clean_expenses']),
                        'forecast': self.get_monthly_forecast(
                            unassigned_expenses['total_cost'])
                    },
                    'organization': {
                        'name': org['name'],
                        'limit': org_pool_details['limit'],
                        'total_cost': round(organization_total_cost, 2),
                        'forecast': round(organization_forecast, 2),
                        'id': self.organization_id,
                        'currency_code': self.get_currency_code(org['currency'])
                    }
                }
            }
        }

    @staticmethod
    def get_monthly_forecast(cost):
        today = datetime.utcnow()
        worked_days = today.day
        _, days_in_month = monthrange(today.year, today.month)
        forecast = cost * days_in_month / worked_days
        return round(forecast, 2)


def main(organization_id, report_data, config_client):
    return OrganizationExpenses(organization_id, report_data, config_client).generate()
