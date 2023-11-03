import logging
from io import StringIO
from databricks.sdk import WorkspaceClient, AccountClient
from databricks.sdk.core import DatabricksError
from tools.cloud_adapter.exceptions import (CloudConnectionError,
                                            InvalidParameterException,
                                            CloudSettingNotSupported)
from tools.cloud_adapter.clouds.base import CloudBase
from tools.cloud_adapter.utils import CloudParameter

DEFAULT_CURRENCY = "USD"
DATABRICKS_HOST = 'https://accounts.cloud.databricks.com'
LOG = logging.getLogger(__name__)
DEFAULT_SKU_PRICES = {
    'AWS_ENHANCED_SECURITY_AND_COMPLIANCE': 0.00,
    'ENTERPRISE_ALL_PURPOSE_COMPUTE': 0.65,
    'ENTERPRISE_ALL_PURPOSE_COMPUTE_(PHOTON)': 0.65,
    'ENTERPRISE_DLT_CORE_COMPUTE': 0.20,
    'ENTERPRISE_DLT_CORE_COMPUTE_(PHOTON)': 0.20,
    'ENTERPRISE_DLT_PRO_COMPUTE': 0.25,
    'ENTERPRISE_DLT_PRO_COMPUTE_(PHOTON)': 0.25,
    'ENTERPRISE_DLT_ADVANCED_COMPUTE': 0.36,
    'ENTERPRISE_DLT_ADVANCED_COMPUTE_(PHOTON)': 0.36,
    'ENTERPRISE_JOBS_COMPUTE': 0.13,
    'ENTERPRISE_JOBS_COMPUTE_(PHOTON)': 0.20,
    'ENTERPRISE_JOBS_LIGHT_COMPUTE': 0.20,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_N_VIRGINIA': 0.070,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_OHIO': 0.070,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_US_WEST_OREGON': 0.070,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_CANADA': 0.078,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_EUROPE_IRELAND': 0.078,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_EUROPE_FRANKFURT': 0.084,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_AP_SINGAPORE': 0.088,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_AP_SYDNEY': 0.088,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_EAST_N_VIRGINIA': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_EAST_OHIO': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_WEST_OREGON': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_CANADA': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_EUROPE_IRELAND': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_EUROPE_FRANKFURT': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_AP_SINGAPORE': 0.00,
    'ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_AP_SYDNEY': 0.00,
    'ENTERPRISE_SERVERLESS_SQL_COMPUTE_US_EAST_N_VIRGINIA': 0.70,
    'ENTERPRISE_SERVERLESS_SQL_COMPUTE_US_WEST_OREGON': 0.70,
    'ENTERPRISE_SERVERLESS_SQL_COMPUTE_EUROPE_IRELAND': 0.91,
    'ENTERPRISE_SERVERLESS_SQL_COMPUTE_AP_SYDNEY': 0.95,
    'ENTERPRISE_SQL_COMPUTE': 0.22,
    'ENTERPRISE_SQL_PRO_COMPUTE_US_EAST_N_VIRGINIA': 0.55,
    'ENTERPRISE_SQL_PRO_COMPUTE_US_EAST_OHIO': 0.55,
    'ENTERPRISE_SQL_PRO_COMPUTE_US_WEST_OREGON': 0.55,
    'ENTERPRISE_SQL_PRO_COMPUTE_US_WEST_CALIFORNIA': 0.55,
    'ENTERPRISE_SQL_PRO_COMPUTE_CANADA': 0.62,
    'ENTERPRISE_SQL_PRO_COMPUTE_SA_BRAZIL': 0.85,
    'ENTERPRISE_SQL_PRO_COMPUTE_EUROPE_IRELAND': 0.72,
    'ENTERPRISE_SQL_PRO_COMPUTE_EUROPE_FRANKFURT': 0.72,
    'ENTERPRISE_SQL_PRO_COMPUTE_EUROPE_LONDON': 0.74,
    'ENTERPRISE_SQL_PRO_COMPUTE_EUROPE_FRANCE': 0.72,
    'ENTERPRISE_SQL_PRO_COMPUTE_AP_SYDNEY': 0.74,
    'ENTERPRISE_SQL_PRO_COMPUTE_AP_MUMBAI': 0.61,
    'ENTERPRISE_SQL_PRO_COMPUTE_AP_SINGAPORE': 0.69,
    'ENTERPRISE_SQL_PRO_COMPUTE_AP_TOKYO': 0.78,
    'ENTERPRISE_SQL_PRO_COMPUTE_AP_SEOUL': 0.74,
    'PREMIUM_ALL_PURPOSE_COMPUTE': 0.55,
    'PREMIUM_ALL_PURPOSE_COMPUTE_(PHOTON)': 0.55,
    'PREMIUM_DLT_CORE_COMPUTE': 0.20,
    'PREMIUM_DLT_CORE_COMPUTE_(PHOTON)': 0.20,
    'PREMIUM_DLT_PRO_COMPUTE': 0.25,
    'PREMIUM_DLT_PRO_COMPUTE_(PHOTON)': 0.25,
    'PREMIUM_DLT_ADVANCED_COMPUTE': 0.36,
    'PREMIUM_DLT_ADVANCED_COMPUTE_(PHOTON)': 0.36,
    'PREMIUM_JOBS_COMPUTE': 0.15,
    'PREMIUM_JOBS_COMPUTE_(PHOTON)': 0.15,
    'PREMIUM_JOBS_LIGHT_COMPUTE': 0.10,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_N_VIRGINIA': 0.070,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_US_EAST_OHIO': 0.070,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_US_WEST_OREGON': 0.070,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_CANADA': 0.078,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_EUROPE_IRELAND': 0.078,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_EUROPE_FRANKFURT': 0.084,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_AP_SINGAPORE': 0.088,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_AP_SYDNEY': 0.088,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_EAST_N_VIRGINIA': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_EAST_OHIO': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_US_WEST_OREGON': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_CANADA': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_EUROPE_IRELAND': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_EUROPE_FRANKFURT': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_AP_SINGAPORE': 0.00,
    'PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_LAUNCH_AP_SYDNEY': 0.00,
    'PREMIUM_SERVERLESS_SQL_COMPUTE_US_EAST_N_VIRGINIA': 0.70,
    'PREMIUM_SERVERLESS_SQL_COMPUTE_US_WEST_OREGON': 0.70,
    'PREMIUM_SERVERLESS_SQL_COMPUTE_EUROPE_FRANKFURT': 0.91,
    'PREMIUM_SERVERLESS_SQL_COMPUTE_EUROPE_IRELAND': 0.91,
    'PREMIUM_SERVERLESS_SQL_COMPUTE_AP_SYDNEY': 0.95,
    'PREMIUM_SQL_COMPUTE': 0.22,
    'PREMIUM_SQL_PRO_COMPUTE_US_EAST_N_VIRGINIA': 0.55,
    'PREMIUM_SQL_PRO_COMPUTE_US_EAST_OHIO': 0.55,
    'PREMIUM_SQL_PRO_COMPUTE_US_WEST_OREGON': 0.55,
    'PREMIUM_SQL_PRO_COMPUTE_US_WEST_CALIFORNIA': 0.55,
    'PREMIUM_SQL_PRO_COMPUTE_CANADA': 0.62,
    'PREMIUM_SQL_PRO_COMPUTE_SA_BRAZIL': 0.85,
    'PREMIUM_SQL_PRO_COMPUTE_EUROPE_IRELAND': 0.72,
    'PREMIUM_SQL_PRO_COMPUTE_EUROPE_FRANKFURT': 0.72,
    'PREMIUM_SQL_PRO_COMPUTE_EUROPE_LONDON': 0.74,
    'PREMIUM_SQL_PRO_COMPUTE_EUROPE_FRANCE': 0.72,
    'PREMIUM_SQL_PRO_COMPUTE_AP_SYDNEY': 0.74,
    'PREMIUM_SQL_PRO_COMPUTE_AP_MUMBAI': 0.61,
    'PREMIUM_SQL_PRO_COMPUTE_AP_SINGAPORE': 0.69,
    'PREMIUM_SQL_PRO_COMPUTE_AP_TOKYO': 0.78,
    'PREMIUM_SQL_PRO_COMPUTE_AP_SEOUL': 0.74,
    'STANDARD_ALL_PURPOSE_COMPUTE': 0.40,
    'STANDARD_ALL_PURPOSE_COMPUTE_(PHOTON)': 0.40,
    'STANDARD_DLT_CORE_COMPUTE': 0.20,
    'STANDARD_DLT_CORE_COMPUTE_(PHOTON)': 0.20,
    'STANDARD_DLT_PRO_COMPUTE': 0.25,
    'STANDARD_DLT_PRO_COMPUTE_(PHOTON)': 0.25,
    'STANDARD_DLT_ADVANCED_COMPUTE': 0.36,
    'STANDARD_DLT_ADVANCED_COMPUTE_(PHOTON)': 0.36,
    'STANDARD_JOBS_COMPUTE': 0.10,
    'STANDARD_JOBS_COMPUTE_(PHOTON)': 0.10,
    'STANDARD_JOBS_LIGHT_COMPUTE': 0.07
}


class Databricks(CloudBase):
    BILLING_CREDS = [
        CloudParameter(name='client_id', type=str, required=True),
        CloudParameter(name='client_secret', type=str, required=True,
                       protected=True),
        CloudParameter(name='account_id', type=str, required=True)
    ]

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._currency = DEFAULT_CURRENCY
        self._account_client = None
        self._workspace_client = None

    def _get_client_parameters(self):
        return dict(
            host=DATABRICKS_HOST, client_id=self.client_id,
            client_secret=self.client_secret, account_id=self.account_id
        )

    @property
    def account_client(self):
        if not self._account_client:
            self._account_client = AccountClient(
                **self._get_client_parameters())
        return self._account_client

    @property
    def workspace_client(self):
        if not self._workspace_client:
            self._workspace_client = WorkspaceClient(
                **self._get_client_parameters())
        return self._workspace_client

    @property
    def client_id(self):
        return self.config.get("client_id")

    @property
    def client_secret(self):
        return self.config.get("client_secret")

    @property
    def account_id(self):
        return self.config.get("account_id")

    def _raise_if_not_admin(self, exception):
        if any(filter(lambda x: x in str(exception), [
            'without account admin status', 'is not authorized'
        ])):
            raise CloudConnectionError(
                'Account admin status required for service principal')

    def validate_credentials(self, org_id=None):
        try:
            self.account_client.service_principals.list(
                filter=f'ApplicationId eq {self.client_id}')
        except DatabricksError as ex:
            self._raise_if_not_admin(ex)
            raise CloudConnectionError(str(ex))
        except ValueError as ex:
            raise InvalidParameterException(str(ex))
        return {'account_id': self.account_id, 'warnings': []}

    def download_usage(self, month_start, month_end):
        """Return billable usage logs.
        :param month_start: str
          Format: `YYYY-MM`. First month to return billable usage logs for.
        :param month_end: str
          Format: `YYYY-MM`. Last month to return billable usage logs for.
        """
        try:
            response = self.account_client.billable_usage.download(
                month_start, month_end, personal_data=True)
        except DatabricksError as ex:
            self._raise_if_not_admin(ex)
            response = StringIO(ex.args[0])
        return response

    def configure_report(self):
        if DEFAULT_CURRENCY != self._currency:
            raise CloudSettingNotSupported(
                "Account currency '%s' doesn’t match organization"
                " currency '%s'" % (DEFAULT_CURRENCY, self._currency))
        return {
            'config_updates': {},
            'warnings': []
        }

    def set_currency(self, currency):
        self._currency = currency

    def configure_last_import_modified_at(self):
        pass
