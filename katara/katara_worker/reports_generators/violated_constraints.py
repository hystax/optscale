from katara.katara_worker.reports_generators.base import Base


RESOURCE_TYPE_MAP = {
    'ttl': 'TTL',
    'total_expense_limit': 'Total expense limit',
    'daily_expense_limit': 'Daily expense limit'
}


class ViolatedConstraints(Base):
    def generate(self):
        user_id = self.report_data.get('user_id')
        constraints_keys = ['violated_constraints', 'differ_constraints']
        _, tasks = self.rest_cl.my_tasks_get(
            self.organization_id, user_id=user_id,
            types=constraints_keys)
        _, org = self.rest_cl.organization_get(self.organization_id)
        differ_constraints = tasks.get('differ_constraints', {})
        violated_constraints = tasks.get('violated_constraints', {})
        total_differ = differ_constraints.get('count', 0)
        total_violated = violated_constraints.get('count', 0)
        differ_resources = differ_constraints.get('tasks', [])
        violated_resources = violated_constraints.get('tasks', [])
        if not total_differ and not total_violated:
            return
        for res_constaints in [differ_resources, violated_resources]:
            if not res_constaints:
                continue
            for res_constaint in res_constaints:
                resource_type = res_constaint.get('type')
                type_value_for_replace = RESOURCE_TYPE_MAP.get(resource_type)
                if resource_type and type_value_for_replace:
                    res_constaint['type'] = type_value_for_replace
        return {
            'email': [self.report_data['user_email']],
            'template_type': 'resource_owner_violation_report',
            'subject':
                'Action required: Hystax OptScale Resource Constraints Report',
            'template_params': {
                'texts': {
                    'organization': {
                        'id': org['id'],
                        'name': org['name']
                    },
                    'total_differ': total_differ,
                    'total_violated': total_violated,
                    'differ_resources': differ_resources,
                    'violated_resources': violated_resources,
                }
            }
        }


def main(organization_id, report_data, config_client):
    return ViolatedConstraints(
        organization_id, report_data, config_client).generate()
