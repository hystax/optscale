import json
import requests
from retrying import retry


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class Client:
    def __init__(self, verify=True):
        self._session = None
        self.verify = verify

    @property
    def session(self):
        if not self._session:
            self._session = requests.session()
            self._session.verify = self.verify
        return self._session

    @retry(retry_on_exception=retry_if_connection_error, wait_fixed=10000,
           stop_max_attempt_number=10)
    def request(self, url, method):
        response = self.session.request(method, url)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            if 'application/json' in response.headers['Content-Type']:
                response_body = json.loads(
                    response.content.decode('utf-8'))
            if 'text/plain' in response.headers['Content-Type']:
                response_body = response.content.decode()
        return response.status_code, response_body

    def get(self, url):
        return self.request(url, "GET")

    def __del__(self):
        self.session.close()
