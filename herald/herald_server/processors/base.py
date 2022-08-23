

class BaseProcessor:

    @staticmethod
    def validate_payload(payload):
        pass

    @staticmethod
    def create_tasks(event, payloads, config_client=None):
        raise NotImplementedError()

    @staticmethod
    def process_task(task, config_client=None):
        raise NotImplementedError()
