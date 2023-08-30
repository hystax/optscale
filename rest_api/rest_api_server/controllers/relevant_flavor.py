import logging
import requests
import operator
from collections import defaultdict
from tools.optscale_exceptions.common_exc import (NotFoundException,
                                                  WrongArgumentsException)
from rest_api.rest_api_server.controllers.base import BaseController, MongoMixin
from rest_api.rest_api_server.controllers.base_async import BaseAsyncControllerWrapper
from concurrent.futures import ThreadPoolExecutor
from optscale_client.insider_client.client import Client as InsiderClient
from rest_api.rest_api_server.exceptions import Err
from rest_api.rest_api_server.models.models import Organization

LOG = logging.getLogger(__name__)


class RelevantFlavorController(BaseController):
    def check_organization(self, organization_id):
        org = self.session.query(Organization).filter(
            Organization.id == organization_id,
            Organization.deleted.is_(False)
        ).one_or_none()
        if org is None:
            raise NotFoundException(Err.OE0002, [Organization.__name__,
                                                 organization_id])
        return org

    def list(self, organization_id, **kwargs):
        organization = self.check_organization(organization_id)
        currency = kwargs.pop(
            'preferred_currency', None) or organization.currency
        kwargs['preferred_currency'] = currency
        resp, errors = self.get_relevant_flavors(**kwargs)
        res_set = defaultdict(lambda: defaultdict(list))
        for r in resp:
            for c_type, flavors in r.items():
                for flavor in flavors:
                    k = (flavor.pop('cpu', None), flavor.pop('memory', None))
                    res_set[k][c_type].append(flavor)
        sorted_keys = sorted(res_set.keys(), key=operator.itemgetter(0, 1))
        result = []
        for k in sorted_keys:
            value = res_set[k]
            value['cpu'], value['ram'] = k
            result.append(value)
        return result, errors

    def get_relevant_flavors(self, **kwargs):
        result = []
        cloud_types = kwargs.pop('cloud_types')
        insider_client = InsiderClient(
            url=self._config.insider_url(),
            secret=self._config.cluster_secret()
        )
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = []
            for t in cloud_types:
                futures.append(
                    executor.submit(insider_client.get_relevant_flavors,
                                    cloud_type=t, **kwargs))
            errors = {}
            for i, f in enumerate(futures):
                try:
                    _, res = f.result()
                    result.append(res)
                except requests.exceptions.HTTPError as ex:
                    errors[cloud_types[i]] = self._get_http_error_reason(ex)
        return result, errors

    def _get_http_error_reason(self, ex):
        try:
            return ex.response.reason
        except Exception:
            return str(ex)


class RelevantFlavorAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RelevantFlavorController
