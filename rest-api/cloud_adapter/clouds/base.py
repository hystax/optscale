from cloud_adapter.exceptions import InvalidResourceTypeException
from cloud_adapter.model import RES_MODEL_MAP


class CloudBase:
    def discovery_calls_map(self):
        return {}

    def get_discovery_calls(self, resource_type):
        try:
            resource = RES_MODEL_MAP[resource_type]
        except KeyError:
            raise InvalidResourceTypeException(
                'Invalid resource type %s' % resource_type)
        func = self.discovery_calls_map().get(resource)
        if func:
            return func()
        else:
            return []

    @classmethod
    def configure_credentials(cls, config):
        return config
