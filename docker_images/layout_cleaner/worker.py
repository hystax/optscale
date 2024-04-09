import os
import logging
from optscale_client.config_client.client import Client as ConfigClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient

LOG = logging.getLogger(__name__)


class LayoutCleaner(object):
    def __init__(self):
        super().__init__()
        self._config_cl = None
        self._rest_cl = None

    @property
    def config_cl(self):
        if not self._config_cl:
            etcd_host = os.environ.get('HX_ETCD_HOST')
            etcd_port = int(os.environ.get('HX_ETCD_PORT'))
            self._config_cl = ConfigClient(host=etcd_host, port=etcd_port)
        return self._config_cl

    @property
    def rest_cl(self):
        if not self._rest_cl:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(),
                secret=self.config_cl.cluster_secret())
        return self._rest_cl

    @staticmethod
    def is_outdated(layout, employees_ids, tasks_ids):
        if (layout['owner_id'] not in employees_ids or (
                layout['type'] == 'ml_run_charts_dashboard' and
                layout['entity_id'] not in tasks_ids)):
            return True
        return False

    def clean_layouts(self):
        LOG.info('Start processing layouts')
        _, organizations = self.rest_cl.organization_list()
        organizations_ids = [x['id'] for x in organizations['organizations']]
        for organization_id in organizations_ids:
            LOG.info('Start processing for organization %s', organization_id)
            _, tasks = self.rest_cl.task_list(organization_id)
            tasks_ids = [x['id'] for x in tasks['tasks']]
            _, employees = self.rest_cl.employee_list(organization_id)
            employees_ids = [x['id'] for x in employees['employees']]
            _, layouts = self.rest_cl.layouts_list(organization_id)
            for layout in layouts['layouts']:
                if self.is_outdated(layout, employees_ids, tasks_ids):
                    LOG.info('Deleting layout %s', layout['id'])
                    self.rest_cl.layout_delete(organization_id, layout['id'])
        LOG.info('Processing completed')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cleaner = LayoutCleaner()
    cleaner.clean_layouts()
