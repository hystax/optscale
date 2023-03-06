class Urls:
    url_prefix = '/pharos_receiver'

    urls_map = {
        'log_bulk': r"%s/collector/bulk",
        'metrics': r"%s/collector/metrics",
        'ack': r"%s/collector/ack",
        'heartbeats': r"%s/collector/heartbeat"
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


class UrlsV2(Urls):
    url_prefix = '/pharos_receiver/v2'


urls_v2 = UrlsV2()
