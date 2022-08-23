from slack_sdk.web.client import WebClient
import logging

LOG = logging.getLogger(__name__)


class SlackClient(WebClient):
    def __init__(self, installation_store, **kwargs):
        self._installation_store = installation_store
        super().__init__(**kwargs)

    def chat_post(self, *, channel_id=None, team_id=None, **kwargs):
        bot = self._installation_store.find_bot(
            team_id=team_id, enterprise_id=None)
        client = WebClient(token=bot.bot_token)
        return client.chat_postMessage(channel=channel_id, **kwargs)
