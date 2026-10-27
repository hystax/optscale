from functools import cached_property
from tools.cloud_adapter.clouds.gcp import Gcp, DEFAULT_KWARGS
from tools.cloud_adapter.enums import CloudTypes
from tools.cloud_adapter.utils import CloudParameter
from tools.cloud_adapter.exceptions import (
    InvalidParameterException, CloudConnectionError)
from google.cloud import bigquery
from google.api_core import exceptions as api_exceptions


class GcpTenant(Gcp):
    BILLING_CREDS = [
        CloudParameter(
            name="billing_data",
            type=dict,
            required=True,
            dependencies=[
                CloudParameter(name="project_id", type=str, required=False),
                CloudParameter(name="dataset_name", type=str, required=True),
                CloudParameter(name="table_name", type=str, required=True),
            ],
        ),
        CloudParameter(
            name="pricing_data",
            type=dict,
            required=False,
            dependencies=[
                CloudParameter(name="project_id", type=str, required=False),
                CloudParameter(name="dataset_name", type=str, required=True),
                CloudParameter(name="table_name", type=str, required=True),
            ],
        ),
        CloudParameter(name="credentials", type=dict, required=True, protected=True),

        # Service parameters
        CloudParameter(name='skipped_subscriptions', type=dict, required=False)
    ]

    @classmethod
    def configure_credentials(cls, config):
        project_id = config['credentials'].pop('project_id', None)
        if project_id:
            for k in ['billing_data', 'pricing_data']:
                dataset = config.get(k)
                if dataset and not dataset.get('project_id'):
                    config[k]['project_id'] = project_id
        return config

    @cached_property
    def bigquery_client(self):
        return bigquery.Client.from_service_account_info(
            self.credentials,
            project=self.billing_project_id,
        )

    def _test_bigquery_connection(self):
        self._list_projects()

    def discovery_calls_map(self):
        return {}

    def _validate_credentials(self):
        if "client_id" not in self.credentials:
            raise InvalidParameterException(
                "Credentials should contain 'client_id'"
            )

    def validate_credentials(self, org_id=None):
        try:
            self._validate_billing_config()
            self._validate_billing_type()
            self._validate_credentials()
            self._test_bigquery_connection()
        except api_exceptions.Forbidden as ex:
            # remove new-lines, otherwise tornado will fail to write response
            raise InvalidParameterException(str(ex).replace("\n", " "))
        except Exception as ex:
            raise CloudConnectionError(str(ex))
        return {"account_id": self.credentials['client_id'], "warnings": []}

    def _list_projects(self):
        dt = self._get_billing_threshold_date()
        date_filter = self._make_date_filter(dt, ">=")
        # find actual project name from latest dataset update
        query = f"""
            SELECT project.id, project.name, max(export_time)
            FROM `{self._billing_table_full_name()}`
            WHERE {date_filter}
            GROUP BY project.id, project.name
            """
        query_job = self.bigquery_client.query(query, **DEFAULT_KWARGS)
        names_map = {}
        for r in list(query_job.result()):
            project_id, name, dt = r
            if not project_id or (
                project_id in names_map and names_map[project_id][1] > dt
            ):
                continue
            names_map[project_id] = (name, dt)
        return {k: v[0] for k, v in names_map.items()}

    def get_children_configs(self):
        projects = self._list_projects()
        return [{
            'name': project_name,
            'config': {
                'project_id': project_id
            },
            'type': CloudTypes.GCP_CNR.value
        } for project_id, project_name in projects.items()]
