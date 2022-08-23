class Urls:
    url_prefix = '/report'

    urls_map = {
        'events': r"%s/events",
        'events_count': r"%s/events/count",
        'ack_event': r"%s/events/(?P<id>[^/]+)",
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/report/v2'
    urls_map = dict(Urls.urls_map, **{
        'events': r"%s/organizations/(?P<organization_id>[^/]+)/events",
        'events_count': r"%s/organizations/(?P<organization_id>[^/]+)/events/count",
        'feedbacks': r"%s/feedbacks",
    })


urls_v2 = UrlsV2()
