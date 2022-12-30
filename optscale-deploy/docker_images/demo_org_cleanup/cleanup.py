import logging
import os
from datetime import timedelta, datetime

from requests import HTTPError

from config_client.client import Client as ConfigClient
from rest_api_client.client_v2 import Client as RestClient

LOG = logging.getLogger(__name__)


def main(config_cl):
    rest_cl = RestClient(url=config_cl.restapi_url(), verify=False)
    rest_cl.secret = config_cl.cluster_secret()

    _, response = rest_cl.organization_list({'is_demo': True})
    old_org_ts = int((datetime.utcnow() - timedelta(days=7)).timestamp())
    for org in response['organizations']:
        if org['created_at'] > old_org_ts:
            continue
        try:
            rest_cl.organization_delete(org['id'])
            LOG.info('Demo organization %s deleted', org['id'])
        except HTTPError as exc:
            LOG.error('Failed to delete org %s: (%s): %s',
                      org['id'], exc, exc.response.text)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config_cl = ConfigClient(
        host=os.environ.get('HX_ETCD_HOST'),
        port=int(os.environ.get('HX_ETCD_PORT')),
    )
    config_cl.wait_configured()
    main(config_cl)
