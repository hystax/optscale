import logging
import re
from tools.cloud_adapter.clouds.aws import Aws
from tools.cloud_adapter.clouds.nebius import Nebius
from tools.cloud_adapter.exceptions import InvalidParameterException
from tools.optscale_exceptions.common_exc import WrongArgumentsException
from insider.insider_api.exceptions import Err
from insider.insider_api.controllers.base import (BaseController,
                                                  BaseAsyncControllerWrapper,
                                                  CachedThreadPoolExecutor,
                                                  CachedCloudCaller)

LOG = logging.getLogger(__name__)
YEAR_IN_SEC = 365 * 24 * 60 * 60


class InstanceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.caller = CachedCloudCaller(self.mongo_client)
        self._aws = None
        self._nebius = None
        self.cloud_account_id = None

    @property
    def aws(self):
        if self._aws is None:
            config = self.get_service_credentials('aws')
            if self.cloud_account_id:
                cloud_acc = self.get_cloud_account(self.cloud_account_id)
                config = cloud_acc['config']
            self._aws = Aws(config)
        return self._aws

    @property
    def nebius(self):
        if self.cloud_account_id:
            cloud_acc = self.get_cloud_account(self.cloud_account_id)
            config = cloud_acc['config']
        else:
            raise ValueError(
                'Cloud account %s is not found' % self.cloud_account_id)
        return Nebius(config)

    def find_aws_reserved_instances(self, **params):
        product_description = params.get('product_description')
        tenancy = params.get('tenancy')
        flavor = params.get('flavor')
        min_duration = params.get('min_duration')
        max_duration = params.get('max_duration')
        include_marketplace = params.get('include_marketplace')

        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            try:
                all_reserved_instances_offerings = executor.submit(
                    self.aws.get_reserved_instances_offerings,
                    product_description, tenancy, flavor, min_duration,
                    max_duration, include_marketplace).result()
            except InvalidParameterException as exc:
                raise WrongArgumentsException(Err.OI0018, [str(exc)])
            except ValueError as exc:
                raise WrongArgumentsException(Err.OI0017, [str(exc)])
        suitable_offerings = [
            offering for offering in all_reserved_instances_offerings[
                'ReservedInstancesOfferings']]
        result = []
        for suitable_offer in suitable_offerings:
            result.append({
                'scope': suitable_offer['Scope'],
                'offering_class': suitable_offer['OfferingClass'],
                'offering_type': suitable_offer['OfferingType'],
                'fixed_price': suitable_offer['FixedPrice'],
                'recurring_charges': suitable_offer['RecurringCharges']
            })
        return result

    def find_nebius_reserved_instances(self, **params):
        flavor = params.get('flavor')
        min_duration = params.get('min_duration')
        max_duration = params.get('max_duration')
        currency = params.get('currency', 'USD')
        sku_regex = '%s, committed usage for (.*)' % flavor
        with CachedThreadPoolExecutor(self.mongo_client) as executor:
            # add cloud_account_id to not use cached prices for
            # other nebius cloud accounts
            skus = executor.submit(
                self.nebius.get_prices, currency=currency,
                cloud_account_id=self.cloud_account_id).result()
            offerings = [x for x in skus if re.match(sku_regex, x['name'])]

        result = []
        for offer in offerings:
            if '1 year' in offer['name']:
                duration = YEAR_IN_SEC
                offering_type = '1 year'
            elif '6 months' in offer['name']:
                duration = YEAR_IN_SEC // 2
                offering_type = '6 months'
            else:
                continue
            if duration > max_duration or duration < min_duration:
                continue
            price = offer['pricingVersions'][-1]['pricingExpressions'][0][
                'rates'][0]['unitPrice']
            result.append({
                      "offering_class": offer['name'],
                      "offering_type": offering_type,
                      "recurring_charges": [{
                        "Amount": price,
                        "Frequency": "Hourly"
                      }]
            })
        return result

    def find_reserved_instances(self, **params):
        cloud_type = params.pop('cloud_type', None)
        self.cloud_account_id = params.pop('cloud_account_id', None)
        if cloud_type == 'aws_cnr':
            result = self.find_aws_reserved_instances(**params)
        elif cloud_type == 'nebius':
            result = self.find_nebius_reserved_instances(**params)
        else:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])
        return result


class InstanceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return InstanceController
