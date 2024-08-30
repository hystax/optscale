class Urls:
    url_prefix = '/insider'

    urls_map = {
        'similar_pricings': r"%s/cloud_types/(?P<cloud_type>[^/]+)/pricings/(?P<pricing_id>[^/]+)/similar",
        'flavors': r"%s/flavors",
        'flavors_generation': r"%s/flavors_generation",
        'flavor_prices': r"%s/cloud_types/(?P<cloud_type>[^/]+)/flavor_prices",
        'family_prices': r"%s/cloud_types/(?P<cloud_type>[^/]+)/family_prices",
        'reserved_instances_offerings': r"%s/reserved_instances_offerings",
        'relevant_flavors': r"%s/cloud_types/(?P<cloud_type>[^/]+)/relevant_flavors",
        'swagger': r'%s/swagger/(.*)',
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/insider/v2'


urls_v2 = UrlsV2()
