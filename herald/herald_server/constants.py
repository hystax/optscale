class Urls:
    url_prefix = '/herald'

    urls_map = {
        'user_notification': r"%s/users/(?P<user_id>[^/]+)/notifications",
        'notifications': r"%s/notifications/(?P<id>[^/]+)"
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV1(Urls):
    url_prefix = '/herald/v1'


class UrlsV2(Urls):
    url_prefix = '/herald/v2'
    urls_map = dict(Urls.urls_map, **{
        'email': r"%s/email"
    })


urls_v1 = UrlsV1()
urls_v2 = UrlsV2()
