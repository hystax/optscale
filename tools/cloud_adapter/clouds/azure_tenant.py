from tools.cloud_adapter.clouds.azure import Azure
from tools.cloud_adapter.enums import CloudTypes
from tools.cloud_adapter.utils import CloudParameter


class AzureTenant(Azure):
    BILLING_CREDS = [
        CloudParameter(name='secret', type=str, required=True, protected=True),
        CloudParameter(name='client_id', type=str, required=True),
        CloudParameter(name='tenant', type=str, required=True),

        # Additional credentials for CSP partners
        CloudParameter(name='partner_tenant', type=str, required=False),
        CloudParameter(name='partner_client_id', type=str, required=False),
        CloudParameter(name='partner_secret', type=str, required=False,
                       protected=True),

        # Service parameters
        CloudParameter(name='skipped_subscriptions', type=dict, required=False)
    ]

    def discovery_calls_map(self):
        return {}

    def _validate_credentials(self, org_id=None, queue=None):
        try:
            self._list_subscriptions()
            result = {'account_id': self.config['tenant'],
                      'warnings': []}
            if queue:
                queue.put(result)
        except Exception as exc:
            if queue:
                queue.put(exc)
            raise
        return result

    def configure_report(self):
        return {
            'config_updates': {},
            'warnings': []
        }

    def _list_subscriptions(self):
        return self.subscription.subscriptions.list()

    def get_children_configs(self):
        return [{
            'name': s.display_name,
            'config': {
                'subscription_id': s.id.split('/')[-1]
            },
            'type': CloudTypes.AZURE_CNR.value
        } for s in self._list_subscriptions()]
