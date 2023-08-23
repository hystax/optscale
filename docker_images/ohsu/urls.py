class Urls:
    url_prefix = '/ohsu'

    urls_map = {
        'links': r"%s/organizations/(?P<organization_id>[^/]+)/links",
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/ohsu/v2'


urls_v2 = UrlsV2()
