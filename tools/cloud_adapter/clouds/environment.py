from tools.cloud_adapter.clouds.base import CloudBase


class Environment(CloudBase):
    BILLING_CREDS = []

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config

    def validate_credentials(self, org_id=None):
        return {'account_id': org_id, 'warnings': []}

    def configure_report(self):
        pass

    def configure_last_import_modified_at(self):
        pass

    def volume_discovery_calls(self):
        raise NotImplementedError

    def instance_discovery_calls(self):
        raise NotImplementedError

    def snapshot_discovery_calls(self):
        raise NotImplementedError

    def bucket_discovery_calls(self):
        raise NotImplementedError

    def pod_discovery_calls(self):
        raise NotImplementedError

    def snapshot_chain_discovery_calls(self):
        raise NotImplementedError

    def rds_instance_discovery_calls(self):
        raise NotImplementedError

    def ip_address_discovery_calls(self):
        raise NotImplementedError

    def get_regions_coordinates(self):
        return {}

    def set_currency(self, currency):
        pass
