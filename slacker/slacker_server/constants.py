
class Urls:
    url_prefix = '/slacker/v2'

    urls_map = {
        'events': r"%s/events",
        'oauth_redirect': r"%s/oauth_redirect",
        'install': r"%s/install",
        'connect_slack_user': r"%s/connect_slack_user",
        'send_message': r"%s/send_message",
        'install_path': r"%s/install_path",
    }

    def __init__(self):
        for k, v in self.urls_map.items():
            self.__setattr__(k, v % self.url_prefix)


urls = Urls()
