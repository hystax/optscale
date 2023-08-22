import logging
from diworker.diworker.migrations.base import BaseMigration
from clickhouse_driver import Client as ClickHouseClient
from optscale_client.rest_api_client.client_v2 import Client as RestClient
from datetime import datetime

"""
Clickhouse traffic expenses table rework.
"""
LOG = logging.getLogger(__name__)


class Migration(BaseMigration):
    @property
    def rest_cl(self):
        if self._rest_cl is None:
            self._rest_cl = RestClient(
                url=self.config_cl.restapi_url(), verify=False)
            self._rest_cl.secret = self.config_cl.cluster_secret()
        return self._rest_cl

    def _get_clickhouse_client(self):
        user, password, host, db_name = self.config_cl.clickhouse_params()
        return ClickHouseClient(
            host=host, password=password, database=db_name, user=user)

    def upgrade(self):
        clickhouse_cl = self._get_clickhouse_client()
        LOG.info('Clearing clickhouse db...')
        clickhouse_cl.execute('ALTER TABLE traffic_expenses DELETE WHERE 1')
        clickhouse_cl.execute('OPTIMIZE TABLE traffic_expenses FINAL')
        LOG.info('Creating traffic processing tasks')
        _, orgs = self.rest_cl.organization_list()
        now_ts = int(datetime.utcnow().timestamp())
        cnt = 0
        for org in orgs['organizations']:
            _, accs = self.rest_cl.cloud_account_list(org['id'])
            for ca in accs['cloud_accounts']:
                if ca['type'] in ['aws_cnr', 'azure_cnr', 'alibaba_cnr']:
                    cnt += 1
                    self.rest_cl.traffic_processing_task_create(ca['id'], {
                        'start_date': 0,
                        'end_date': now_ts
                    })
        LOG.info('%s tasks created' % cnt)

    def downgrade(self):
        pass
