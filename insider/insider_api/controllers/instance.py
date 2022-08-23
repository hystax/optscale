import logging
from insider_api.exceptions import Err
from cloud_adapter.clouds.aws import Aws
from insider_api.controllers.base import (BaseController,
                                          BaseAsyncControllerWrapper,
                                          CachedThreadPoolExecutor,
                                          CachedCloudCaller)
from optscale_exceptions.common_exc import WrongArgumentsException
from cloud_adapter.exceptions import InvalidParameterException

LOG = logging.getLogger(__name__)


class InstanceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.caller = CachedCloudCaller(self.mongo_client)
        self._aws = None

    @property
    def aws(self):
        if self._aws is None:
            config = self._config.read_branch('/service_credentials/aws')
            self._aws = Aws(config)
        return self._aws

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

    def find_reserved_instances(self, **params):
        cloud_type = params.pop('cloud_type', None)
        if cloud_type not in ['aws_cnr']:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])
        return self.find_aws_reserved_instances(**params)


class InstanceAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return InstanceController
