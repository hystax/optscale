from tools.optscale_exceptions.common_exc import (
    NotFoundException, WrongArgumentsException)
from insider.insider_api.exceptions import Err
from insider.insider_api.utils import check_string, is_public_region
from insider.insider_api.controllers.base import (
    BaseController, BaseAsyncControllerWrapper)


class SimilarPricingsController(BaseController):

    @staticmethod
    def validate_parameters(**kwargs):
        for k in ['pricing_id', 'cloud_type']:
            v = kwargs.get(k)
            if v is None:
                raise WrongArgumentsException(Err.OI0011, [k])
        pricing_id = kwargs.get('pricing_id')
        cloud_type = kwargs.get('cloud_type')
        check_string('cloud_type', cloud_type)
        check_string('pricing_id', pricing_id)
        if cloud_type not in ['azure_cnr']:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        pricing_id = kwargs['pricing_id']
        cloud_type = kwargs['cloud_type']
        discoveries = self.discoveries_collection.find(
            {'cloud_type': cloud_type}
        ).sort(
            [('completed_at', -1)]).limit(1)
        try:
            last_discovery = next(discoveries)
        except StopIteration:
            raise NotFoundException(Err.OI0009, [cloud_type])
        result = []
        if cloud_type == 'azure_cnr':
            result = self.get_azure_similar_pricings(
                pricing_id, last_discovery['started_at'])
        return result

    def get_azure_similar_pricings(self, pricing_id, discovery_time):
        pricings = self.azure_prices_collection.aggregate([
            {
                '$match': {
                    '$and': [
                        {'meterId': pricing_id},
                        {'type': 'Consumption'},
                        {'serviceName': 'Virtual Machines'},
                        {'last_seen': {'$gte': discovery_time}}
                    ]
                }
            }
        ])
        try:
            price_info = next(pricings)
        except StopIteration:
            return []
        result = self.azure_prices_collection.aggregate([
            {
                '$match': {
                    '$and': [
                        {'meterName': price_info['meterName']},
                        {'type': price_info['type']},
                        {'productName': price_info['productName']},
                        {'last_seen': {'$gte': discovery_time}}
                    ]
                },
            }
        ])
        return [
            r for r in list(result) if is_public_region(
                r['armRegionName'], 'azure_cnr')
        ]


class SimilarPricingsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return SimilarPricingsController
