class Urls:
    url_prefix = '/metroculus'

    urls_map = {
        'activity_breakdown': r"%s/activity_breakdown",
        'agr_metrics': r"%s/agr_metrics",
        'metrics': r"%s/metrics",
        'k8s_metrics': r"%s/k8s_metrics",
        'swagger': r'%s/swagger/(.*)',
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/metroculus/v2'


urls_v2 = UrlsV2()
