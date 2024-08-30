import json
import logging
from abc import ABCMeta
from urllib.parse import urlencode

import requests
from retrying import retry

LOG = logging.getLogger(__name__)


def retry_if_connection_error(exception):
    if isinstance(exception, requests.ConnectionError):
        return True
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code in (503,):
            return True
    return False


class AbstractHttpProvider(metaclass=ABCMeta):
    def __init__(self, secret=''):
        self._secret = secret

    @property
    def headers(self):
        return {
            'Secret': str(self._secret),
            'Content-type': 'application/json'
        }

    @property
    def secret(self):
        return self._secret

    @secret.setter
    def secret(self, value):
        self._secret = value


class RequestsHttpProvider(AbstractHttpProvider):
    def __init__(self, url, secret='', verify=True):
        self.url = url
        self.verify = verify
        self.session = requests.session()
        super().__init__(secret)

    @retry(stop_max_delay=10000, wait_fixed=1000,
           retry_on_exception=retry_if_connection_error)
    def request(self, path, method, data=None):
        full_url = self.url + path
        response = self.session.request(
            method, full_url, data=data,
            headers=self.headers, verify=self.verify)
        response.raise_for_status()
        response_body = None
        if response.status_code != requests.codes.no_content:
            response_body = json.loads(response.content.decode('utf-8'))
        return response.status_code, response_body

    def close(self):
        self.session.close()


class FetchMethodHttpProvider(AbstractHttpProvider):
    def __init__(self, fetch_method, rethrow=True, secret=''):
        self.fetch = fetch_method
        self._rethrow = rethrow
        super().__init__(secret)

    def request(self, url, method, body=None):
        response = self.fetch(
            url, method=method, body=body, allow_nonstandard_methods=True,
            headers=self.headers
        )
        if self._rethrow:
            response.rethrow()
        try:
            decoded_response = json.loads(response.body.decode('utf-8'))
        except Exception as e:
            LOG.error("Failed to decode response body %s", e)
            decoded_response = None
        return response.code, decoded_response

    def close(self):
        pass


class Client:
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, secret='',
                 verify=True):
        if http_provider is None:
            if url is None:
                url = "http://%s:%s" % (address, port)
            http_provider = RequestsHttpProvider(url, secret, verify)
        self._http_provider = http_provider
        self._api_version = api_version

    @property
    def secret(self):
        return self._http_provider.secret

    @secret.setter
    def secret(self, value):
        self._http_provider.secret = value

    def _url(self, sub_url):
        return "/insider/%s/%s" % (self._api_version, sub_url)

    def _request(self, url, method, body=None):
        data = None
        if body is not None:
            data = json.dumps(body)
        return self._http_provider.request(self._url(url), method, data)

    def get(self, url, body=None):
        return self._request(url, "GET", body)

    def post(self, url, body):
        return self._request(url, "POST", body)

    def put(self, url, body):
        return self._request(url, "PUT", body)

    def patch(self, url, body):
        return self._request(url, "PATCH", body)

    def delete(self, url):
        return self._request(url, "DELETE")

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    @staticmethod
    def cloud_type_url(cloud_type):
        return 'cloud_types/%s' % cloud_type

    @staticmethod
    def similar_pricings_url(cloud_type, pricing_id):
        return '%s/pricings/%s/similar' % (
            Client.cloud_type_url(cloud_type), pricing_id)

    def get_similar_pricings(self, cloud_type, pricing_id):
        return self.get(self.similar_pricings_url(cloud_type, pricing_id))

    @staticmethod
    def flavors_url():
        return 'flavors'

    def find_flavor(self, cloud_type, resource_type, region, family_specs,
                    mode, **kwargs):
        body = {
            'cloud_type': cloud_type,
            'resource_type': resource_type,
            'region': region,
            'family_specs': family_specs,
            'mode': mode
        }
        body.update(kwargs)
        return self.post(self.flavors_url(), body)

    @staticmethod
    def flavor_prices_url(cloud_type):
        return '%s/flavor_prices' % Client.cloud_type_url(cloud_type)

    def get_flavor_prices(
            self, cloud_type, flavor, region, os_type, preinstalled=None,
            quantity=None, billing_method=None, currency=None):
        params = {
            'flavor': flavor,
            'region': region,
            'os_type': os_type,
        }
        if preinstalled:
            params['preinstalled'] = preinstalled
        if quantity:
            params['quantity'] = quantity
        if billing_method:
            params['billing_method'] = billing_method
        if currency:
            params['currency'] = currency
        url = self.flavor_prices_url(cloud_type) + self.query_url(**params)
        return self.get(url)

    @staticmethod
    def reserved_instances_offerings_url():
        return 'reserved_instances_offerings'

    def find_reserved_instances_offerings(
            self, cloud_type, flavor, min_duration, max_duration, tenancy=None,
            include_marketplace=None, currency=None, product_description=None,
            cloud_account_id=None, **kwargs):
        body = {
            'cloud_type': cloud_type,
            'product_description': product_description,
            'tenancy': tenancy,
            'flavor': flavor,
            'min_duration': min_duration,
            'max_duration': max_duration,
            'include_marketplace': include_marketplace,
            'currency': currency,
            'cloud_account_id': cloud_account_id
        }
        body.update(kwargs)
        return self.post(self.reserved_instances_offerings_url(), body)

    @staticmethod
    def flavors_generation_url():
        return 'flavors_generation'

    def find_flavor_generation(self, cloud_type, region, current_flavor,
                               os_type=None, preinstalled=None, meter_id=None,
                               **kwargs):
        body = {
            'cloud_type': cloud_type,
            'region': region,
            'current_flavor': current_flavor,
            'os_type': os_type,
            'preinstalled': preinstalled,
            'meter_id': meter_id
        }
        body.update(kwargs)
        return self.post(self.flavors_generation_url(), body)

    @staticmethod
    def family_prices_url(cloud_type):
        return '%s/family_prices' % Client.cloud_type_url(cloud_type)

    def get_family_prices(self, cloud_type, instance_family, region,
                          os_type=None, currency=None):
        params = {
            'instance_family': instance_family,
            'region': region,
        }
        if os_type:
            params['os_type'] = os_type
        if currency:
            params['currency'] = currency
        url = self.family_prices_url(cloud_type) + self.query_url(**params)
        return self.get(url)

    @staticmethod
    def relevant_flavors_url(cloud_type):
        return '%s/relevant_flavors' % Client.cloud_type_url(cloud_type)

    def get_relevant_flavors(self, cloud_type, region, **kwargs):
        params = {
            'region': region
        }
        if kwargs:
            params.update(kwargs)
        url = self.relevant_flavors_url(cloud_type) + self.query_url(**params)
        return self.get(url)
