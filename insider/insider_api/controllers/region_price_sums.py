import logging
from optscale_exceptions.common_exc import NotFoundException, WrongArgumentsException
from insider_api.exceptions import Err
from insider_api.utils import check_string, is_public_region
from insider_api.controllers.base import (BaseController,
                                          BaseAsyncControllerWrapper)

LOG = logging.getLogger(__name__)

METER_ID_LIST = [
    '1b286734-7784-4f96-b497-d9ad9b935e99',  # D16 v3
    '3727475e-e0c1-460b-80b0-be4ad439ba8b',  # E16 v3
    '3a5eab69-1384-41f5-bc7f-f0ad8d241d66',  # B4ms
    '4d1bb254-aaf7-40e8-99d3-65a628cdd037',  # B2s
    '4f9f1112-491c-4d37-8e06-54a1b9cbc38c',  # F4
    '5b38b6dc-884b-49dd-8580-a4ff1a0abaef',  # D4 v3
    '6a756189-bcca-4675-b175-7a1e5ed1a951',  # A8 v2
    'c0b8a7eb-19b2-4f75-bd1e-59c471974021',  # E32 v3
    'd20bb405-d717-423c-b51c-bc629e54fd0c',  # B8ms
    'd75fb159-1a02-44b5-bb5c-fc204f93e846',  # F2
]


class RegionPriceSumsController(BaseController):
    @staticmethod
    def validate_parameters(**kwargs):
        for k in ['cloud_type']:
            v = kwargs.get(k)
            if v is None:
                raise WrongArgumentsException(Err.OI0011, [k])
        cloud_type = kwargs.get('cloud_type')
        check_string('cloud_type', cloud_type)
        if cloud_type not in ['azure_cnr']:
            raise WrongArgumentsException(Err.OI0010, [cloud_type])

    def get_last_discovery(self, cloud_type):
        discoveries = self.discoveries_collection.find(
            {'cloud_type': cloud_type}
        ).sort(
            [('completed_at', -1)]).limit(1)
        try:
            last_discovery = next(discoveries)
        except StopIteration:
            raise NotFoundException(Err.OI0009, [cloud_type])
        return last_discovery

    def get(self, **kwargs):
        self.validate_parameters(**kwargs)
        cloud_type = kwargs['cloud_type']
        last_discovery = self.get_last_discovery(cloud_type)
        discovery_time = last_discovery['started_at']
        all_regions = self.azure_prices_collection.distinct(
            'armRegionName', {
                'type': 'Consumption',
                'serviceName': 'Virtual Machines',
                'last_seen': {'$gte': discovery_time}
            }
        )
        all_public_regions = [
            r for r in all_regions if is_public_region(r, cloud_type)
        ]
        rr = self.azure_prices_collection.aggregate([
            {
                '$match': {
                    '$and': [
                        {'meterId': {'$in': METER_ID_LIST}},
                        {'type': 'Consumption'},
                        {'isPrimaryMeterRegion': True}
                    ]
                }
            }
        ])
        scores = dict()
        excluded_regions = set()
        for r in rr:
            pricings = self.azure_prices_collection.aggregate([
                {
                    '$match': {
                        '$and': [
                            {'meterName': r['meterName']},
                            {'type': r['type']},
                            {'productName': r['productName']},
                            {'last_seen': {'$gte': discovery_time}}
                        ]
                    }
                }
            ])
            exists_in_regions = set()
            for pr in pricings:
                region_name = pr['armRegionName']
                exists_in_regions.add(region_name)
                if not is_public_region(region_name, cloud_type):
                    continue
                if region_name not in scores:
                    scores[region_name] = 0
                scores[region_name] += pr.get('unitPrice', 0)
            sku_not_present_regions = set(all_public_regions) - set(
                exists_in_regions)
            excluded_regions.update(sku_not_present_regions)
        if excluded_regions:
            LOG.warning(
                'Regions {} are excluded from region price sums'.format(
                    ', '.join(excluded_regions)))
            for excluded_region in excluded_regions:
                scores.pop(excluded_region, None)
        return scores


class RegionPriceSumsAsyncController(BaseAsyncControllerWrapper):
    def _get_controller_class(self):
        return RegionPriceSumsController
