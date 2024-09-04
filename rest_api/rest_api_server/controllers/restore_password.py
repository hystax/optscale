import logging
import requests
from random import randrange
from rest_api.rest_api_server.controllers.base import BaseController
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from rest_api.rest_api_server.utils import query_url
from optscale_client.auth_client.client_v2 import Client as AuthClient
from optscale_client.herald_client.client_v2 import Client as HeraldClient

LOG = logging.getLogger(__name__)


class RestorePasswordController(BaseController):
    def restore_password(self, email):
        generated_code = self._generate_code()
        verification_code = self.create_verification_code(email, generated_code)
        if verification_code:
            self.send_verification_email(email, generated_code)

    @staticmethod
    def _generate_code():
        ints = []
        for _ in range(6):
            ints.append(str(randrange(10)))
        return ''.join(ints)

    def create_verification_code(self, email, code):
        auth_client = AuthClient(url=self._config.auth_url(),
                                 secret=self._config.cluster_secret())
        try:
            _, result = auth_client.verification_code_create(email, code)
            return result
        except requests.exceptions.HTTPError:
            return

    def _generate_link(self, email, code):
        host = self._config.public_ip()
        params = query_url(email=email, code=code)
        return f'https://{host}/password-recovery{params}'

    def send_verification_email(self, email, code):
        link = self._generate_link(email, code)
        HeraldClient(
            url=self._config.herald_url(),
            secret=self._config.cluster_secret()
        ).email_send(
            [email], 'Optscale password recovery',
            template_type="restore_password",
            template_params={
                'texts': {
                    'code': code,
                },
                'links': {
                    'restore_button': link
                }
            }
        )


class RestorePasswordAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RestorePasswordController
