import logging
from herald_client.client import Client as ClientV1

LOG = logging.getLogger(__name__)


class Client(ClientV1):
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, token='', secret='',
                 verify=True):
        super().__init__(address, port, api_version, url, http_provider, token,
                         secret, verify)

    @staticmethod
    def email_herald_url():
        return "email"

    def email_send(self, email, subject, template_type="invite",
                   template_params=None, reply_to_email=None):
        body = {
            'email': email,
            'subject': subject,
            'template_type': template_type,
            'template_params': template_params,
            'reply_to_email': reply_to_email
        }
        return self.post(self.email_herald_url(), body)
