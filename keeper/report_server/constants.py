class Urls:
    url_prefix = '/report'

    urls_map = {}

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/report/v2'
    urls_map = {
        'events': r"%s/organizations/(?P<organization_id>[^/]+)/events",
        'events_count': r"%s/organizations/(?P<organization_id>[^/]+)/events/count",
        'feedbacks': r"%s/feedbacks",
        'ack_event': r"%s/events/(?P<id>[^/]+)",
    }


urls_v2 = UrlsV2()
