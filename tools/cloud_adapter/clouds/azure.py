import datetime
import enum
import logging
import time
from requests.models import Request
from urllib.parse import urlencode
from multiprocessing import Process, Queue
from azure.mgmt.consumption import ConsumptionManagementClient
from azure.mgmt.consumption.models import (ModernUsageDetail, LegacyUsageDetail,
                                           UsageDetail, UsageDetailsListResult)
from retrying import retry
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.commerce import UsageManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import InstanceViewTypes
from azure.mgmt.commerce.models.error_response import ErrorResponseException
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.subscription import SubscriptionClient
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import AuthenticationError, ClientRequestError
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import (HttpResponseError, ClientAuthenticationError,
                                   ResourceNotFoundError)
from azure.identity import ClientSecretCredential
from msrest import Deserializer

from tools.cloud_adapter.lib.azure_partner.client import AzurePartnerClient
from tools.cloud_adapter.lib.azure_partner.exceptions import (
    AzurePartnerConnectionException, AzurePartnerHttpException)
from tools.cloud_adapter.clouds.base import CloudBase
from tools.cloud_adapter.model import (
    InstanceResource,
    SnapshotResource,
    VolumeResource,
    BucketResource,
    IpAddressResource,
)
from tools.cloud_adapter.exceptions import (
    ResourceNotFound,
    AuthorizationException,
    InvalidParameterException,
    CloudSettingNotSupported,
    CloudConnectionError,
    MetricsNotFoundException,
    MetricsServerTimeoutException
)
from tools.cloud_adapter.utils import CloudParameter, gbs_to_bytes

# Silence annoying logs from Azure SDK
logging.getLogger('azure.core.pipeline.policies.http_logging_policy').setLevel(
    logging.WARNING)
logging.getLogger('azure.identity').setLevel(logging.WARNING)

LOG = logging.getLogger(__name__)
SECONDS_IN_DAY = 60 * 60 * 24
CLOUD_VALIDATION_TIMEOUT = 90
CLOUD_LINK_PATTERN = '%s%s/overview'
DAYS_IN_MONTH = 30
# we use base_url without tenant_name, azure can resolve links and also add tenant_name by itself while using link
DEFAULT_BASE_URL = 'https://portal.azure.com/#resource'
DESERIALIZER = Deserializer(classes={
    'ModernUsageDetail': ModernUsageDetail,
    'LegacyUsageDetail': LegacyUsageDetail,
    'UsageDetail': UsageDetail,
    'UsageDetailsListResult': UsageDetailsListResult
})

# defining it to use outside CAd
AzureConsumptionException = HttpResponseError
AzureErrorResponseException = ErrorResponseException
AzureAuthenticationError = ClientAuthenticationError
AzureResourceNotFoundError = ResourceNotFoundError


def _retry_on_error(exc):
    if isinstance(exc, AzureConsumptionException):
        # retry if not Too Many Requests
        if int(exc.response.status_code) != 429:
            return True
        else:
            LOG.info('Too many requests. Will sleep for 60 seconds')
            time.sleep(60)
            return True
    if isinstance(exc, MetricsServerTimeoutException):
        return True
    return False


def call_with_time_limit(func, args, kwargs, timeout):
    q = Queue()
    p = Process(target=func, args=(args, q), kwargs=kwargs)
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        raise TimeoutError
    if not q.empty():
        return q.get_nowait()


class ExpenseImportScheme(enum.Enum):
    usage = 'usage'
    raw_usage = 'raw_usage'
    partner_raw_usage = 'partner_raw_usage'


class Azure(CloudBase):
    BILLING_CREDS = [
        CloudParameter(name='subscription_id', type=str, required=True),
        CloudParameter(name='secret', type=str, required=True, protected=True),
        CloudParameter(name='client_id', type=str, required=True),
        CloudParameter(name='tenant', type=str, required=True),
        CloudParameter(name='expense_import_scheme', type=str, required=False),

        # Additional credentials for CSP partners
        CloudParameter(name='partner_tenant', type=str, required=False),
        CloudParameter(name='partner_client_id', type=str, required=False),
        CloudParameter(name='partner_secret', type=str, required=False,
                       protected=True),
    ]
    SUPPORTS_REPORT_UPLOAD = False
    DEFAULT_CURRENCY = 'USD'
    DEFAULT_IMPORT_SCHEME = ExpenseImportScheme.usage.value

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._subscription_id = self.config.get('subscription_id')
        self._service_principal_credentials = None
        self._client_secret_credentials = None
        self._compute = None
        self._resource = None
        self._network = None
        self._storage = None
        self._subscription = None
        self._consumption = None
        self._location_map = None
        self._billing = None
        self._partner = None
        self._usage = None
        self._monitor = None
        self._currency = self.DEFAULT_CURRENCY

    @staticmethod
    def get_currency_iso(currency):
        return {
            'USD': 'US',
            'EUR': 'DE',
            'AUD': 'AU',
            'BRL': 'BR',
            'CAD': 'CA',
            'DKK': 'DK',
            'INR': 'IN',
            'JPY': 'JP',
            'KRW': 'KR',
            'NZD': 'NZ',
            'NOK': 'NO',
            'RUB': 'RU',
            'SEK': 'SE',
            'CHF': 'CH',
            'TWD': 'TW',
            'GBP': 'GB'
        }.get(currency) or 'US'

    def discovery_calls_map(self):
        return {
            VolumeResource: self.volume_discovery_calls,
            InstanceResource: self.instance_discovery_calls,
            SnapshotResource: self.snapshot_discovery_calls,
            IpAddressResource: self.ip_address_discovery_calls,
            BucketResource: self.bucket_discovery_calls
        }

    @property
    def location_map(self):
        if self._location_map is None:
            self._location_map = {
                x.name: x.display_name
                for x in self.subscription.subscriptions.list_locations(
                    self._subscription_id)
            }
        return self._location_map

    @property
    def cloud_account_id(self):
        return self.config.get('cloud_account_id')

    @property
    def organization_id(self):
        return self.config.get('organization_id')

    @property
    def cloud_account_name(self):
        return self.config.get('cloud_account_name')

    @property
    def expense_import_scheme(self):
        return self.config.get(
            'expense_import_scheme', self.DEFAULT_IMPORT_SCHEME)

    @property
    def service_principal_credentials(self):
        if self._service_principal_credentials:
            return self._service_principal_credentials
        self._service_principal_credentials = (
            self._get_service_principal_credentials())
        return self._service_principal_credentials

    @property
    def client_secret_credentials(self):
        if self._client_secret_credentials:
            return self._client_secret_credentials
        self._client_secret_credentials = self._get_client_secret_credentials()
        return self._client_secret_credentials

    @property
    def compute(self):
        if self._compute:
            return self._compute
        self._compute = ComputeManagementClient(
            self.service_principal_credentials, self._subscription_id)
        return self._compute

    @property
    def resource(self):
        if self._resource:
            return self._resource
        self._resource = ResourceManagementClient(
            self.service_principal_credentials, self._subscription_id)
        return self._resource

    @property
    def network(self):
        if self._network:
            return self._network
        self._network = NetworkManagementClient(
            self.service_principal_credentials, self._subscription_id)
        return self._network

    @property
    def storage(self):
        if self._storage:
            return self._storage
        self._storage = StorageManagementClient(
            self.service_principal_credentials, self._subscription_id)
        return self._storage

    @property
    def consumption(self):
        if self._consumption:
            return self._consumption
        self._consumption = ConsumptionManagementClient(
            self.client_secret_credentials, self._subscription_id)
        return self._consumption

    @property
    def subscription(self):
        if self._subscription:
            return self._subscription
        self._subscription = SubscriptionClient(
            self.service_principal_credentials)
        return self._subscription

    @property
    def monitor(self):
        if self._monitor:
            return self._monitor
        self._monitor = MonitorManagementClient(
            self.service_principal_credentials, self._subscription_id)
        return self._monitor

    @property
    def partner(self):
        if not self._partner:
            if self._is_partner_account:
                self._partner = AzurePartnerClient(
                    tenant_id=self.config['partner_tenant'],
                    client_id=self.config['partner_client_id'],
                    client_secret=self.config['partner_secret'])
            else:
                raise CloudSettingNotSupported(
                    'Can\'t access partner API for non-partner cloud account')
        return self._partner

    @property
    def usage(self):
        if not self._usage:
            self._usage = UsageManagementClient(
                self.service_principal_credentials, self._subscription_id)
        return self._usage

    @property
    def raw_client(self):
        return self.subscription._client

    def _get_service_principal_credentials(self):
        """
        Obtain service principal credential object for older Azure SDK
        components. Will raise AuthorizationException if credentials are
        incorrect.
        :return: service principal credential object
        """
        try:
            credentials = ServicePrincipalCredentials(
                client_id=self.config['client_id'],
                secret=self.config['secret'],
                tenant=self.config['tenant'],
            )
        except AuthenticationError as ex:
            description = self._get_error_description(ex)
            raise AuthorizationException(description)
        return credentials

    def _get_client_secret_credentials(self):
        """
        Obtain client secret credential object for newer Azure SDK components.
        If credentials are wrong, credential object will be constructed without
        errors. An exception will be raised later during an attempt to make an
        API call.
        :return: client secret credential object
        """
        return ClientSecretCredential(
            client_id=self.config['client_id'],
            client_secret=self.config['secret'],
            tenant_id=self.config['tenant'],
        )

    @property
    def _is_partner_account(self):
        return ('partner_tenant' in self.config and
                'partner_client_id' in self.config and
                'partner_secret' in self.config)

    @staticmethod
    def _get_error_description(exc: AuthenticationError):
        try:
            description = exc.inner_exception.error_response.get(
                'error_description').split('\r\n')[0]
        except Exception:
            description = str(exc)
        return description

    @retry(retry_on_exception=_retry_on_error, wait_fixed=2000,
           stop_max_attempt_number=10)
    def _retry(self, method, *args, **kwargs):
        return method(*args, **kwargs)

    def _extract_server_status(self, instance_view):
        if len(instance_view.statuses) > 0:
            status_dict = dict(
                status_test.code.rsplit('/', 1) for status_test in
                instance_view.statuses)
            return status_dict.get('PowerState')

    def _get_vm_status(self, server_id):
        try:
            server_info = self._parse_azure_id(server_id)
            server = self.compute.virtual_machines.get(
                server_info['group_name'], server_info['name'],
                expand=InstanceViewTypes.instance_view)
        except ResourceNotFound:
            return None
        return self._extract_server_status(server.instance_view)

    def _extract_public_ip_ids(self, nic_object):
        public_ip_ids = [conf.public_ip_address.id
                         for conf in nic_object.ip_configurations
                         if conf.public_ip_address]
        return public_ip_ids

    def _extract_server_ips(self, server_object):
        public_ip_ids = []
        for nic in server_object.network_profile.network_interfaces:
            nic_info = self._parse_azure_id(nic.id)
            nic = self.network.network_interfaces.get(
                nic_info['group_name'], nic_info['name'],
                expand='ipConfigurations/publicIPAddress')
            public_ip_ids.extend(self._extract_public_ip_ids(nic))
        return public_ip_ids

    def _parse_azure_id(self, azure_id):
        azure_id_parts = azure_id.split('/')
        return {
            'azure_id': azure_id,
            'name': azure_id_parts[-1],
            'group_name': azure_id_parts[
                azure_id_parts.index('resourceGroups') + 1],
        }

    def _check_subscription(self, subscription_id):
        try:
            self.subscription.subscriptions.get(subscription_id)
        except CloudError as ex:
            raise ResourceNotFound(ex.inner_exception.message)

    def _get_cpu_ram(self, flavor):
        caps = flavor.capabilities
        vcpu = [c.value for c in caps if c.name == 'vCPUs'][0]
        ram = float(
            [c.value for c in caps if c.name == 'MemoryGB'][0]) * 1024
        return int(vcpu), int(ram)

    def get_flavors_info(self, flavors=None):
        all_sku = self.compute.resource_skus.list()
        flavor_map = {s.name: s for s in all_sku
                      if s.resource_type == 'virtualMachines'}
        result_flavors = list(flavor_map.keys())
        if flavors:
            not_found = [f for f in flavors if f not in flavor_map]
            if not_found:
                raise ResourceNotFound(
                    'Flavors {0} not found.'.format(not_found))
            result_flavors = list(filter(lambda x: x in flavors,
                                         flavor_map.keys()))
        result = {}
        for name in result_flavors:
            flavor = flavor_map[name]
            vcpu, ram = self._get_cpu_ram(flavor)
            result[name] = {
                'vcpus': vcpu,
                'name': name,
                'ram': ram,
                'family': flavor.family
            }
        return result

    def _guess_subscription_type(self, subscription_id):
        """
        Azure does not provide a public API that can be used to obtain Offer ID
        of Subscription, so it's hard to know what subscription type does user
        have. But it turns out that there is a `quota_id` field, which contains
        subscription type as a part of ID.
        :param subscription_id: Subscription ID
        :return: a string, here are some of the possible results: "PayAsYouGo",
            "CSP", "Sponsored".
        """
        subscription = self.subscription.subscriptions.get(subscription_id)
        quota_id = subscription.subscription_policies.quota_id
        return quota_id.rsplit('_', 1)[0]

    def _get_billing_info(self):
        consumption_api_supported = True
        currency = self._currency
        subscription_type = self._guess_subscription_type(
            self._subscription_id)
        warnings = []
        try:
            range_end = datetime.datetime.utcnow()
            range_start = range_end - datetime.timedelta(days=DAYS_IN_MONTH)
            usage = self.get_usage(range_start, range_end, 1)
            if usage is None:
                raise StopIteration
            usage_detail = next(usage)
            currency = (getattr(usage_detail, 'billing_currency', None) or
                        getattr(usage_detail, 'billing_currency_code', None))
        except (AzureConsumptionException, StopIteration, ClientRequestError,
                TypeError) as exc:
            # according to logs in this issue we get TypeError deep inside
            # python lib in case of timeout error
            is_timeout_error = isinstance(exc, (ClientRequestError, TypeError))
            is_empty = isinstance(exc, StopIteration)
            is_unsupported = (isinstance(exc, AzureConsumptionException) and
                              int(exc.response.status_code) in [400, 404, 422])

            # Sponsored subscriptions are known to be unsupported by
            # Consumption API, but it returns an empty result for them
            # instead of an error, so there is a check for that as well
            if is_unsupported or (is_empty and
                                  subscription_type == 'Sponsored'):
                consumption_api_supported = False
            elif is_empty:
                warnings.append(
                    'Subscription %s (%s) doesn\'t have usage data yet or is'
                    'not supported' % (
                        self._subscription_id, subscription_type))
            elif is_timeout_error:
                raise CloudConnectionError(
                    'Could not connect to cloud by subscription %s: '
                    'connection time out.' % self._subscription_id)
            else:
                raise

        if subscription_type == 'EnterpriseAgreement':
            consumption_api_supported = False

        return {
            'consumption_api_supported': consumption_api_supported,
            'currency': currency,
            'subscription_type': subscription_type,
            'warnings': warnings,
        }

    def _check_expense_import_scheme(self, scheme_name=None):
        if scheme_name is not None:
            try:
                scheme = ExpenseImportScheme(scheme_name).value
            except ValueError:
                raise InvalidParameterException(
                    'Invalid expense import scheme provided, '
                    'please use one of the following: {}'.format(
                        ', '.join(x.value for x in ExpenseImportScheme)))
            if (scheme == ExpenseImportScheme.partner_raw_usage.value and
                    not self._is_partner_account):
                raise InvalidParameterException(
                    'Please, provide partner credentials to use partner '
                    'expense import scheme')

    def _check_partner_account(self):
        try:
            subscription_info = self.partner.customers(
                self.config['tenant']).subscriptions(
                self.config['subscription_id']).get()
            LOG.info('Connecting CSP customer with subscription: %s',
                     subscription_info)
        except AzurePartnerConnectionException as exc:
            raise CloudConnectionError(
                'Azure Partner Center connection error: {}'.format(str(exc)))
        except AzurePartnerHttpException as exc:
            raise InvalidParameterException(
                'Error from Azure Partner Center: {}'.format(str(exc)))

    def validate_credentials(self, org_id=None):
        try:
            result = call_with_time_limit(
                self._validate_credentials, args=org_id, kwargs={},
                timeout=CLOUD_VALIDATION_TIMEOUT)
            if isinstance(result, Exception):
                raise result
            else:
                return result
        except TimeoutError:
            raise CloudConnectionError('Cloud validation timed out')

    def _validate_credentials(self, org_id=None, queue=None):
        try:
            self._check_expense_import_scheme(
                self.config.get('expense_import_scheme'))
            if self._is_partner_account:
                self._check_partner_account()
            # empty string or string with whitespaces only should be handled
            # separately. Details in OSB-566
            if not self.config['subscription_id'].strip():
                raise InvalidParameterException(
                    "The subscription '%s' could not be found." %
                    self.config['subscription_id'])
            try:
                self._check_subscription(self.config['subscription_id'])
            except ResourceNotFound as ex:
                raise InvalidParameterException(str(ex))
            result = {'account_id': self.config['subscription_id'],
                      'warnings': []}
            if queue:
                queue.put(result)
        except Exception as exc:
            if queue:
                queue.put(exc)
            raise
        return result

    def configure_report(self):
        billing_info = self._retry(self._get_billing_info)
        LOG.info('Billing info for subscription %s: %s',
                 self._subscription_id, billing_info)

        if billing_info['currency'] != self._currency:
            raise CloudSettingNotSupported(
                "Account currency '%s' doesn’t match organization"
                " currency '%s'" % (billing_info['currency'], self._currency))

        scheme = self.config.get('expense_import_scheme')
        if scheme is None:
            if self._is_partner_account:
                scheme = ExpenseImportScheme.partner_raw_usage.value
            elif billing_info['consumption_api_supported']:
                scheme = ExpenseImportScheme.usage.value
            else:
                scheme = ExpenseImportScheme.raw_usage.value

        return {
            'config_updates': {
                'expense_import_scheme': scheme,
            },
            'warnings': billing_info['warnings']
        }

    def configure_last_import_modified_at(self):
        pass

    @staticmethod
    def _generate_cloud_link(resource_id):
        return CLOUD_LINK_PATTERN % (DEFAULT_BASE_URL, resource_id)

    def _discover_vnets(self):
        vnets = self.network.virtual_networks.list_all()
        return {vnet.id: vnet.name for vnet in vnets}

    def _get_nics_by_instance(self, vm, return_all=True):
        nics = []
        if not vm.network_profile or not vm.network_profile.network_interfaces:
            return nics
        for network_interface in vm.network_profile.network_interfaces:
            nw_intf_id_components = network_interface.id.split('/')
            nic_name = nw_intf_id_components[-1]
            nic_group = nw_intf_id_components[-5]
            nics.append(self.network.network_interfaces.get(
                nic_group, nic_name))
            if not return_all:
                return nics
        return nics

    def _get_sgs_by_instance(self, vm):
        nics = self._get_nics_by_instance(vm, return_all=True)
        sgs_ids = set(nic.network_security_group.id for nic in nics)
        return list(sgs_ids)

    def _get_vnet_id_by_instance(self, vm):
        nics = self._get_nics_by_instance(vm, return_all=False)
        if not nics:
            return None
        return '/'.join(nics[0].ip_configurations[0].subnet.id.split('/')[:-2])

    def discover_instance_resources(self):
        """
        Discovers instance cloud resources
        :return: list(model.InstanceResource)
        """
        vnet_id_to_name = self._discover_vnets()
        virtual_machines = self.compute.virtual_machines.list_all()
        for vm in virtual_machines:
            os_type = vm.storage_profile.os_disk.os_type.value
            tags = vm.tags or {}
            spotted = vm.priority == 'Spot'
            status = self._get_vm_status(vm.id)
            # if we got invalid value from azure (status = None), then set stopped_allocated to None,
            # to detect this issue in future and get the latest value of stopped_allocated from db resource meta
            stopped_allocated = status if status is None else status == 'stopped'
            cloud_console_link = self._generate_cloud_link(vm.id)
            vnet_id = self._get_vnet_id_by_instance(vm)
            sgs_ids = self._get_sgs_by_instance(vm)
            instance_resource = InstanceResource(
                cloud_resource_id=vm.id.lower(),
                cloud_account_id=self.cloud_account_id,
                region=self.location_map.get(vm.location),
                name=vm.name,
                flavor=vm.hardware_profile.vm_size,
                stopped_allocated=stopped_allocated,
                organization_id=self.organization_id,
                tags=tags,
                spotted=spotted,
                cloud_console_link=cloud_console_link,
                os=os_type,
                vpc_id=vnet_id,
                vpc_name=vnet_id_to_name.get(vnet_id),
                security_groups=sgs_ids
            )
            yield instance_resource

    def instance_discovery_calls(self):
        return [(self.discover_instance_resources, ())]

    def discover_volume_resources(self):
        """
        Discovers volume cloud resources
        :return: list(model.VolumeResource)
        """
        volumes = self.compute.disks.list()
        for volume in volumes:
            tags = volume.tags or {}
            cloud_console_link = self._generate_cloud_link(volume.id)
            res = VolumeResource(
                cloud_resource_id=volume.id.lower(),
                cloud_account_id=self.cloud_account_id,
                region=self.location_map.get(volume.location),
                name=volume.name,
                size=gbs_to_bytes(volume.disk_size_gb),
                volume_type=volume.type,
                organization_id=self.organization_id,
                tags=tags,
                attached=volume.disk_state in ['Attached', 'Reserved'],
                cloud_console_link=cloud_console_link
            )
            yield res

    def volume_discovery_calls(self):
        return [(self.discover_volume_resources, ())]

    def discover_snapshot_resources(self):
        """
        Discovers Snapshot cloud resources
        :return: list(model.SnapshotResource)
        """
        snapshots = self.compute.snapshots.list()
        for snapshot in snapshots:
            tags = snapshot.tags or {}
            cloud_console_link = self._generate_cloud_link(snapshot.id)
            res = SnapshotResource(
                cloud_resource_id=snapshot.id.lower(),
                cloud_account_id=self.cloud_account_id,
                region=self.location_map.get(snapshot.location),
                organization_id=self.organization_id,
                name=snapshot.name,
                size=gbs_to_bytes(snapshot.disk_size_gb),
                description=None,
                state=snapshot.provisioning_state,
                tags=tags,
                cloud_console_link=cloud_console_link
            )
            yield res

    def snapshot_discovery_calls(self):
        return [(self.discover_snapshot_resources, ())]

    def discover_bucket_resources(self):
        """
        Discovers Bucket cloud resources

        We call them buckets to have common name for both cloud types.
        In Azure user is charged per cloud account, so we discover them here.
        Buckets in Azure are containers created inside cloud account.
        All of this may be confusing, it will be resolved in
        https://datatrendstech.atlassian.net/browse/OSB-646 and related epic

        :return: list(model.BucketResource)
        """
        accounts = self.storage.storage_accounts.list()
        for account in accounts:
            tags = account.tags or {}
            cloud_console_link = self._generate_cloud_link(account.id)
            res = BucketResource(
                cloud_resource_id=account.id.lower(),
                cloud_account_id=self.cloud_account_id,
                region=self.location_map.get(account.location),
                organization_id=self.organization_id,
                name=account.name,
                tags=tags,
                cloud_console_link=cloud_console_link)
            yield res

    def bucket_discovery_calls(self):
        return [(self.discover_bucket_resources, ())]

    def discover_ip_address_resources(self):
        vms = {}
        vm_ids = [vm.id for vm in
                  list(self.compute.virtual_machines.list_all())]
        for vm_id in vm_ids:
            try:
                vm_parsed_id = self._parse_azure_id(vm_id)
                vm = self.compute.virtual_machines.get(
                    vm_parsed_id['group_name'], vm_parsed_id['name'],
                    expand=InstanceViewTypes.instance_view)
                ip_address_ids = self._extract_server_ips(vm)
                for ip_address_id in ip_address_ids:
                    vms[ip_address_id] = {}
                    vms[ip_address_id]['status'] = self._extract_server_status(
                        vm.instance_view)
                    vms[ip_address_id]['vm_id'] = vm_id
            except ResourceNotFound:
                continue
        lbs = {}
        load_balancers = self.network.load_balancers.list_all()
        for lb in load_balancers:
            for ip_cfg in lb.frontend_ip_configurations:
                if not ip_cfg.public_ip_address:
                    continue
                lbs[ip_cfg.public_ip_address.id] = lb.id
        gateways = {}
        app_gateways = self.network.application_gateways.list_all()
        for app_gateway in app_gateways:
            for ip_cfg in app_gateway.frontend_ip_configurations:
                if not ip_cfg.public_ip_address:
                    continue
                gateways[ip_cfg.public_ip_address.id] = app_gateway.id
        all_ip_addresses = list(self.network.public_ip_addresses.list_all())
        for public_ip_address in all_ip_addresses:
            tags = public_ip_address.tags or {}
            public_ip_id = public_ip_address.id
            cloud_console_link = self._generate_cloud_link(public_ip_id)
            vm = vms.get(public_ip_id, {})
            lb = lbs.get(public_ip_id)
            gateway = gateways.get(public_ip_id)
            vm_id = vm.get('vm_id') or lb or gateway
            available = (vm.get('status') is None and lb is None and
                         gateway is None)
            resource = IpAddressResource(
                cloud_account_id=self.cloud_account_id,
                organization_id=self.organization_id,
                cloud_console_link=cloud_console_link,
                cloud_resource_id=public_ip_id.lower(),
                region=self.location_map.get(public_ip_address.location),
                name=public_ip_address.name,
                instance_id=vm_id,
                available=available,
                tags=tags
            )
            yield resource

    def pod_discovery_calls(self):
        return []

    def snapshot_chain_discovery_calls(self):
        return []

    def rds_instance_discovery_calls(self):
        return []

    def ip_address_discovery_calls(self):
        return [(self.discover_ip_address_resources, ())]

    def get_usage(self, start_date, range_end=None, limit=None):
        """
        Get priced usage for current subscription. This API does not work for
        all subscription types. Some of them (for example, CSP, Azure
        Sponsorship, Enterprise Agreement) are not supported.
        :param start_date: start datetime
        :param range_end: end datetime
        :param limit: result limit
        :return: an iterator with usage objects or None
        """
        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        filter_fmt = "properties/usageStart ge '{}' and properties/usageEnd lt '{}'"
        if range_end is None:
            range_end = datetime.datetime.utcnow()
        start_str = start_date.strftime(date_format)
        end_str = range_end.strftime(date_format)
        # test request to check subscription type
        result = self.consumption.usage_details.list(
            scope='/subscriptions/{}/'.format(self._subscription_id),
            filter=filter_fmt.format(start_str, end_str),
            expand='properties/meterDetails,properties/additionalProperties',
            top=1)
        for res in result:
            if isinstance(res, ModernUsageDetail):
                LOG.info('Modern subscription type usage data detected')
                return self.get_modern_usage(start_date, range_end, limit)
            else:
                return self.consumption.usage_details.list(
                    scope='/subscriptions/{}/'.format(self._subscription_id),
                    filter=filter_fmt.format(start_str, end_str),
                    expand='properties/meterDetails,properties/additionalProperties',
                    top=limit)
        return None

    def get_modern_usage(self, start_date, range_end=None, limit=None):
        """Get priced usage for current 'modern' subscription.
        UsageDetails API doesn't filter data for daterange in python SDK
        for 'modern' subscriptions.
        :param start_date: start datetime
        :param range_end: end datetime
        :param limit: result limit
        :return: an iterator with usage objects
        """
        def get_values(_req):
            result = self.raw_client.send(_req)
            deserialized = DESERIALIZER.deserialize_data(
                result.json(), "UsageDetailsListResult")
            return deserialized.value or [], deserialized.next_link
        date_format = '%Y-%m-%d'
        start_str = start_date.strftime(date_format)
        end_str = range_end.strftime(date_format)
        scope = 'subscriptions/{}'.format(self._subscription_id)
        base_url = 'https://management.azure.com'
        usage_url = self.consumption.usage_details.list.metadata[
            'url'].format(scope=scope)
        url = f'{base_url}{usage_url}?$extend=properties/meterDetails,' \
              f'properties/additionalProperties&startDate={start_str}' \
              f'&endDate={end_str}&api-version=2021-10-01'
        if limit:
            url += f'&top={limit}'
        token = self.raw_client.config.credentials.token['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        request = Request(method='GET', url=url, headers=headers)
        values, next_link = get_values(request)
        for v in values:
            yield v
        while next_link:
            request.url = next_link
            values, next_link = get_values(request)
            for v in values:
                yield v

    def get_raw_usage(self, start_date, range_end, granularity='Daily'):
        """
        Get unpriced usage for current subscription. This API should work for
        any subscription type, but expenses have to be calculated manually
        based on usage.

        Note that this API is weird and has several bugs:

        For daily granularity
        - It returns an error if ranges are not aligned by day
        - It returns an error is you try to get usage for today
        - It receives dates when resource usage was recorded, but outputs dates
            when resource usage was billed (in my tests there was a -2h shift)
        - It frequently splits results in two parts: 2h and 22h
        - It lies in usage dates and says that both parts depict 24h of usage
        - Usage for some day may be incomplete (e.g. 23 hours instead of 24),
            but the missing usage for that day will appear when you query data
            for some later day. And usage dates in both cases will say that
            they are for 24h.

        For hourly granularity
        - It returns an error if ranges are not aligned by hour
        - It returns an error is you try to get usage newer than 2-3h ago
        - It receives dates when resource usage was recorded, but outputs dates
            when resource usage was billed (in my tests there was a -2h shift)
        - Usage for some day may be incomplete (e.g. 23 hours instead of 24),
            but the missing usage for that day will appear when you query data
            for some later day.

        :param start_date: start datetime
        :param range_end: end datetime
        :param granularity: result granularity, can be Daily or Hourly
        :return: a generator with usage objects
        """
        return self.usage.usage_aggregates.list(
            reported_start_time=start_date,
            reported_end_time=range_end,
            show_details=True,
            aggregation_granularity=granularity,
        )

    def get_public_prices(self, currency=None, region=None,
                          offer_id='MS-AZR-0003P', locale='en-US'):
        """
        Get public Azure prices
        :param currency: result currency
        :param region: billing region (not usage region, resources themselves
            can be anywhere)
        :param offer_id: offer ID. Here are some examples:
            * MS-AZR-0003P (Pay-As-You-Go) - works fine.
            * MS-AZR-0036P (Microsoft Azure Sponsored Offer) - works fine.
            * MS-AZR-0017G (Azure Plan) - works fine.
            * MS-AZR-0017P (Enterprise Agreement) - works fine.
            * MS-AZR-0145P (Azure in CSP) - doesn't work, invalid request.
        :param locale: result locale
        :return: dict, with meter IDs as keys and following stuff as values:
            * rates - usage rates in format (usage_rate, price). Usage above
                some usage rate is priced by the corresponding price.
            * included - free stuff! How much usage is not priced at all.
            There are more fields, but at the moment they are not returned to
            reduce RAM overhead.
            TODO: include more fields once we start caching prices in database
        """
        if not currency:
            currency = self._currency
        if not region:
            region = self.get_currency_iso(currency)
        prices = self.usage.rate_card.get(
             filter=f"OfferDurableId eq '{offer_id}' "
                    f"and Currency eq '{currency}' "
                    f"and Locale eq '{locale}' "
                    f"and RegionInfo eq '{region}'",
        )
        return {
            p.meter_id: {
                'rates': list(sorted((float(k), v) for k, v
                                     in p.meter_rates.items())),
                'included': p.included_quantity
            }
            for p in prices.meters
        }

    def get_partner_prices(self, currency=None, region=None):
        """
        Get CSP Azure prices from Partner Center
        :param currency: result currency
        :param region: billing region (not usage region, resources themselves
            can be anywhere)
        :return: dict, with meter IDs as keys and following stuff as values:
            * rates - usage rates in format (usage_rate, price). Usage above
                some usage rate is priced by the corresponding price.
            * included - free stuff! How much usage is not priced at all.
            There are more fields, but at the moment they are not returned to
            reduce RAM overhead.
            TODO: include more fields once we start caching prices in database
        """
        if not currency:
            currency = self._currency
        if not region:
            region = self.get_currency_iso(currency)
        prices = self.partner.ratecards().azure().get(
            currency=currency, region=region)
        return {
            p['id']: {
                'rates': list(sorted((float(k), v) for k, v
                                     in p['rates'].items())),
                'included': p['includedQuantity']
            }
            for p in prices['meters']
        }

    def _get_coordinates_map(self):
        return {
            'usgovarizona': {
                'name': 'US Gov Arizona', 'alias': 'US Gov AZ',
                'longitude': -111.7046, 'latitude': 34.42527},
            'germanycentral': {
                'name': 'Germany Central', 'alias': 'DE West Central',
                'longitude': 8.6833, 'latitude': 50.1166},
            'japaneast': {
                'name': 'Japan East', 'alias': 'JA East',
                'longitude': 139.77, 'latitude': 35.68},
            'chinaeast2': {
                'name': 'China East 2', 'alias': 'China',
                'longitude': 121.474, 'latitude': 31.228},
            'westcentralus': {
                'name': 'West Central US', 'alias': 'US West Central',
                'longitude': -110.234, 'latitude': 40.89},
            'usgovvirginia': {
                'name': 'US Gov Virginia',
                'longitude': -78.39411, 'latitude': 37.623159},
            'australiacentral2': {
                'name': 'Australia Central 2', 'alias': 'AU Central 2',
                'longitude': 149.1244, 'latitude': -35.3075},
            'chinanorth2': {
                'name': 'China North 2', 'alias': 'CH North',
                'longitude': 116.383, 'latitude': 39.916},
            'uaecentral': {
                'name': 'UAE Central', 'alias': 'AE Central',
                'longitude': 54.366669, 'latitude': 24.466667},
            'koreacentral': {
                'name': 'Korea Central', 'alias': 'KR Central',
                'longitude': 126.978, 'latitude': 37.5665},
            'southcentralus': {
                'name': 'South Central US', 'alias': 'US South Central',
                'longitude': -98.5, 'latitude': 29.4167},
            'switzerlandwest': {
                'name': 'Switzerland West', 'alias': 'CH West',
                'longitude': 6.143158, 'latitude': 46.204391},
            'germanynortheast': {
                'name': 'Germany Northeast', 'alias': 'DE North',
                'longitude': 11.616, 'latitude': 52.133},
            'westindia': {
                'name': 'West India', 'alias': 'IN West',
                'longitude': 72.868, 'latitude': 19.088},
            'southafricanorth': {
                'name': 'South Africa North', 'alias': 'ZA North',
                'longitude': 28.21837, 'latitude': -25.73134},
            'australiasoutheast': {
                'name': 'Australia Southeast', 'alias': 'AU Southeast',
                'longitude': 144.9631, 'latitude': -37.8136},
            'francecentral': {
                'name': 'France Central', 'alias': 'FR Central',
                'longitude': 2.373, 'latitude': 46.3772},
            'germanynorth': {
                'name': 'Germany North', 'alias': 'DE North',
                'longitude': 8.806422, 'latitude': 53.073635},
            'switzerlandnorth': {
                'name': 'Switzerland North', 'alias': 'CH North',
                'longitude': 8.564572, 'latitude': 47.451542},
            'southafricawest': {
                'name': 'South Africa West', 'alias': 'ZA West',
                'longitude': 18.843266, 'latitude': -34.075691},
            'usseceast': {
                'name': 'US Sec East',
                'longitude': -78.536422, 'latitude': 37.274279},
            'westeurope': {
                'name': 'West Europe', 'alias': 'EU West',
                'longitude': 4.9, 'latitude': 52.3667},
            'norwaywest': {
                'name': 'Norway West', 'alias': 'NO West',
                'longitude': 5.733107, 'latitude': 58.969975},
            'canadacentral': {
                'name': 'Canada Central', 'alias': 'CA Central',
                'longitude': -79.383, 'latitude': 43.653},
            'ukwest': {
                'name': 'UK West', 'longitude': -3.084, 'latitude': 53.427},
            'usdodeast': {
                'name': 'US DoD East',
                'longitude': -77.84588, 'latitude': 37.70926},
            'usgovtexas': {
                'name': 'US Gov Texas', 'alias': 'US Gov TX',
                'longitude': -99.208076, 'latitude': 31.56443},
            'northcentralus': {
                'name': 'North Central US', 'alias': 'US North Central',
                'longitude': -87.6278, 'latitude': 41.8819},
            'australiaeast': {
                'name': 'Australia East', 'alias': 'AU East',
                'longitude': 151.2094, 'latitude': -33.86},
            'canadaeast': {
                'name': 'Canada East', 'alias': 'CA East',
                'longitude': -71.217, 'latitude': 46.817},
            'norwayeast': {
                'name': 'Norway East', 'alias': 'NO East',
                'longitude': 10.752245, 'latitude': 59.913868},
            'germanywestcentral': {
                'name': 'Germany West Central', 'alias': 'DE West Central',
                'longitude': 8.682127, 'latitude': 50.110924},
            'chinaeast': {
                'name': 'China East', 'alias': 'China',
                'longitude': 121.474, 'latitude': 31.228},
            'westus': {
                'name': 'West US', 'alias': 'US West',
                'longitude': -122.417, 'latitude': 37.783},
            'chinanorth': {
                'name': 'China North',
                'longitude': 116.383, 'latitude': 39.916},
            'francesouth': {
                'name': 'France South', 'alias': 'FR South',
                'longitude': 2.1972, 'latitude': 43.8345},
            'eastasia': {
                'name': 'East Asia', 'longitude': 114.188, 'latitude': 22.267},
            'uaenorth': {
                'name': 'UAE North', 'alias': 'uaen',
                'longitude': 55.316666, 'latitude': 25.266666},
            'southeastasia': {
                'name': 'Southeast Asia', 'alias': 'Asia',
                'longitude': 103.833, 'latitude': 1.283},
            'ussecwest': {
                'name': 'US Sec West',
                'longitude': -122.481734, 'latitude': 38.316024},
            'koreasouth': {
                'name': 'Korea South', 'alias': 'KR South',
                'longitude': 129.0756, 'latitude': 35.1796},
            'eastus2': {
                'name': 'East US 2', 'alias': 'useast2',
                'longitude': -78.3889, 'latitude': 36.6681},
            'westus2': {
                'name': 'West US 2', 'alias': 'US West 2',
                'longitude': -119.852, 'latitude': 47.233},
            'japanwest': {
                'name': 'Japan West', 'alias': 'JA West',
                'longitude': 135.5022, 'latitude': 34.6939},
            'southindia': {
                'name': 'South India', 'alias': 'IN South',
                'longitude': 80.1636, 'latitude': 12.9822},
            'centralus': {
                'name': 'Central US', 'alias': 'US Central',
                'longitude': -93.6208, 'latitude': 41.5908},
            'centralindia': {
                'name': 'Central India', 'alias': 'India',
                'longitude': 73.9197, 'latitude': 18.5822},
            'usdodcentral': {
                'name': 'US DoD Central',
                'longitude': -92.561731, 'latitude': 42.41475},
            'australiacentral': {
                'name': 'Australia Central', 'alias': 'AU Central',
                'longitude': 149.1244, 'latitude': -35.3075},
            'northeurope': {
                'name': 'North Europe', 'alias': 'Europe',
                'longitude': -6.2597, 'latitude': 53.3478},
            'uksouth': {
                'name': 'UK South', 'longitude': -0.799, 'latitude': 50.941},
            'eastus': {
                'name': 'East US', 'alias': 'US East',
                'longitude': -79.8164, 'latitude': 37.3719},
            'brazilsouth': {
                'name': 'Brazil South', 'alias': 'BR South',
                'longitude': -46.633, 'latitude': -23.55},
            'brazilsoutheast': {
                'name': 'Brazil Southeast', 'alias': 'South America',
                'longitude': -43.2075, 'latitude': -22.90278},
            'westus3': {
                'name': 'West US 3', 'alias': 'US West 3',
                'longitude': -112.074036, 'latitude': 33.448376},
        }

    def get_regions_coordinates(self):
        def to_coord(coordinate):
            if isinstance(coordinate, str):
                try:
                    coordinate = float(coordinate)
                except ValueError:
                    coordinate = None
            return coordinate

        coordinates_map = self._get_coordinates_map()
        try:
            for region in self.subscription.subscriptions.list_locations(
                    self._subscription_id):
                exist_region = coordinates_map.get(region.name, {})
                coordinates_map[region.name] = {
                    'longitude': to_coord(region.longitude),
                    'latitude': to_coord(region.latitude),
                    'name': region.display_name,
                    'alias': exist_region.get('alias')
                }
        except Exception:
            LOG.info('Cannot retrieve the list of regions for %s cloud account'
                     % self.cloud_account_id)
            pass
        return coordinates_map

    def _batch_request(self, request_specs):
        """
        Send multiple raw request as one request
        :param request_specs: a list with request spec dicts, each spec should
            contain at least 'httpMethod' and 'relativeUrl'. Maximum batch size
            seems to be 20: if the list is bigger, the API will ask for 'name'
            parameter in specs, and if name is provided it will just return
            nothing.
        :return: a dict with grouped response data
        """
        batch_request = self.raw_client.post(
            url='/batch',
            params={'api-version': '2015-11-01'},
            headers={'Content-Type': 'application/json'},
            content={'requests': request_specs},
        )
        response = self.raw_client.send(batch_request, stream=False)
        return response.json()

    @retry(stop_max_attempt_number=5, wait_fixed=5000,
           retry_on_exception=_retry_on_error)
    def get_metric(self, namespace, metric_names, instance_ids, interval,
                   start_date, end_date):
        """
        Get metrics for instances
        :param namespace: metric namespace
        :param metric_names: metric names list
        :param instance_ids: instance ids
        :param interval: time interval in seconds
        :param start_date: metric start datetime date
        :param end_date: metric end datetime date
        :return: dict
        """
        result = {}
        max_batch_size = 20
        url = '{instance_id}/providers/Microsoft.Insights/metrics?{params}'
        params = {
            'api-version': '2018-01-01',
            'aggregation': 'average',
            'timespan': '{start}/{end}'.format(
                start=start_date.isoformat(), end=end_date.isoformat()),
            'interval': 'PT{interval}S'.format(interval=interval),
            'metricnames': ','.join(
                x.replace(',', '%2') for x in metric_names),
            'metricNamespace': namespace,
        }
        for i in range(0, len(instance_ids), max_batch_size):
            request_specs = []
            for instance_id in instance_ids[i:i + max_batch_size]:
                request_specs.append({
                    'httpMethod': 'GET',
                    'relativeUrl': url.format(
                        instance_id=instance_id, params=urlencode(params))
                })
            responses = self._batch_request(request_specs)['responses']
            for j, response in enumerate(responses):
                instance_id = instance_ids[i + j]
                if 'error' in response['content']:
                    error = response['content']['error']
                    code = error.get('code', '')
                    if code == 'ServerTimeout':
                        raise MetricsServerTimeoutException(error)
                    elif code == 'ResourceNotFound':
                        continue
                    else:
                        raise MetricsNotFoundException(error)
                elif ('value' not in response['content'] and
                      response['content']['code'] == 'BadRequest'):
                    raise MetricsNotFoundException(response['content']['message'])

                for metric in response['content']['value']:
                    metric_name = metric['name']['value']
                    try:
                        points = metric['timeseries'][0]['data']
                    except (KeyError, IndexError):
                        points = []
                    result.setdefault(instance_id, {})[metric_name] = points
        return result

    def set_currency(self, currency):
        self._currency = currency

    def start_instance(self, instance_name, group_name):
        try:
            return self.compute.virtual_machines.start(
                group_name, instance_name)
        except CloudError as exc:
            if exc.error.error == 'ResourceNotFound':
                raise ResourceNotFound(str(exc))
            else:
                raise

    def stop_instance(self, instance_name, group_name):
        try:
            return self.compute.virtual_machines.deallocate(
                group_name, instance_name)
        except CloudError as exc:
            if exc.error.error == 'ResourceNotFound':
                raise ResourceNotFound(str(exc))
            else:
                raise
