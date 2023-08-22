import logging
from urllib.parse import urlencode
from optscale_client.report_client.client import Client as ClientV1

LOG = logging.getLogger(__name__)


class Client(ClientV1):
    def __init__(self, address="127.0.0.1", port="80", api_version="v2",
                 url=None, http_provider=None, token='', secret='', verify=True):
        super().__init__(address, port, api_version, url, http_provider, token,
                         secret, verify)

    @staticmethod
    def query_url(**query):
        query = {
            key: value for key, value in query.items() if value is not None
        }
        encoded_query = urlencode(query, doseq=True)
        return "?" + encoded_query

    @staticmethod
    def feedback_url():
        return 'feedbacks'

    @staticmethod
    def event_url(id=None, organization_id=None):
        url = 'events'
        if id is not None:
            url = '%s/%s' % (url, id)
        elif organization_id is not None:
            url = 'organizations/%s/%s' % (organization_id, url)
        return url

    @staticmethod
    def event_count_url(organization_id):
        url = '%s/%s' % (Client.event_url(organization_id=organization_id),
                         'count')
        return url

    def event_list(self, org_id, limit=None, ack_only=False, time_start=None,
                   time_end=None, levels=None, object_types=None,
                   evt_classes=None, last_id=None, include_read=False,
                   read_on_get=False):
        """
        Gets event list based on filters ordered by time ascending
        Doesn't marks Events as read, requires cluster secret
        :param org_id: (string) org id to filter events
        :param limit: (int)
        :param ack_only: (bool) only ACK events?
        :param time_start: (int) utc timestamp seconds, e.g 1544597079
        :param time_end: (int) utc timestamp seconds, e.g 1544597080
        :param levels: list(string) - levels e.g ['SUCCESS']
        :param object_types: list(string) - types e.g ['device', 'customer']
        :param evt_classes: list(string) - classes e.g
        :param last_id: (string) - last loaded event id
        :param include_read: (bool) - show read events
        :param read_on_get: (bool) - show read events
         ['INITIAL_REPLICATION_COMPLETED']
        :return: list(dict(Event))
        """
        url = self.event_url(organization_id=org_id) + self.query_url(
            limit=limit,
            ack_only=ack_only,
            time_start=time_start,
            time_end=time_end,
            level=levels,
            object_type=object_types,
            evt_class=evt_classes,
            last_id=last_id,
            include_read=include_read,
            read_on_get=read_on_get
        )
        return self.get(url)

    def event_count(self, org_id, ack_only=False, levels=None):
        url = self.event_count_url(org_id) + self.query_url(
            ack_only=ack_only,
            level=levels,
        )
        return self.get(url)

    def feedback_submit(self, email, url, text, metadata=None):
        body = {
            'email': email,
            'url': url,
            'text': text,
            'metadata': metadata
        }
        return self.post(self.feedback_url(), body)

    def feedbacks_list(self, time_start=None, time_end=None, user_id=None,
                       email=None, url=None, limit=None):
        url = self.feedback_url() + self.query_url(
            time_start=time_start,
            time_end=time_end,
            user_id=user_id,
            email=email,
            url=url,
            limit=limit,
        )
        return self.get(url)

    def event_submit(self, level, evt_class, object_id, object_type,
                     object_name, organization_id, description,
                     localized, ack=False,
                     initiator_id=None, initiator_name=None):
        body = {
            'level': level,
            'evt_class': evt_class,
            'object_id': object_id,
            'object_type': object_type,
            'object_name': object_name,
            'organization_id': organization_id,
            'description': description,
            'localized': localized,
            'ack': ack,
            'initiator_id': initiator_id,
            'initiator_name': initiator_name,
        }
        return self.post(self.event_url(organization_id=organization_id), body)

    def event_ack_all(self, org_id, timestamp=None, resolution=None):
        body = {
            'timestamp': timestamp,
            'resolution': resolution
        }
        return self.patch(self.event_url(organization_id=org_id), body)
