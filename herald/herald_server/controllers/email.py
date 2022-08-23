import json

from herald_server.controllers.base import BaseController
from herald_server.controllers.base_async import BaseAsyncControllerWrapper
from herald_server.utils import is_hystax_email


class EmailAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return EmailController


class EmailController(BaseController):
    def skip_email_send(self, data):
        template_type = data.get('template_type')
        if template_type in ['new_employee', 'new_cloud_account',
                             'cloud_account_deleted']:
            auth_user_email = data.get('template_params', {}).get(
                'texts', {}).get('user_email')
            return auth_user_email is not None and is_hystax_email(
                auth_user_email)
        return False

    def publish_message(self, data):
        self.rabbit_client.publish_message(data)

    def create(self, **kwargs):
        need_skip = self.skip_email_send(kwargs)
        if not need_skip:
            self.publish_message(kwargs)
        return json.dumps(kwargs)
