from collections import defaultdict
from functools import cached_property
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Tuple
from datetime import datetime, timezone, timedelta
from typing import Dict
import hashlib
import logging

import requests
import requests.exceptions as requests_exceptions
from google.api_core import retry, exceptions as api_exceptions
from google.api_core.exceptions import Forbidden
from google.auth import exceptions as auth_exceptions
from google.cloud import bigquery
from google.cloud import compute
from google.cloud import storage
from google.cloud import monitoring_v3
from google.cloud.iam_admin_v1 import IAMClient, types

import tools.cloud_adapter.exceptions
import tools.cloud_adapter.model
from tools.cloud_adapter.clouds.base import CloudBase
from tools.cloud_adapter.exceptions import (
    RegionNotFoundException, ResourceNotFound, ForbiddenException
)
from tools.cloud_adapter.utils import CloudParameter, gbs_to_bytes


# can be from 0 to 500 for gcp API
MAX_RESULTS = 500
BILLING_THRESHOLD = 3

_AUTH_TYPES = (
    api_exceptions.PermissionDenied,   # 403
    api_exceptions.Unauthenticated,    # 401
    api_exceptions.Forbidden,          # same semantic as 403
)

# Retries logic composed of code from
# google/cloud/bigquery/retry.py and
# google/cloud/storage/retry.py
# should NOT include auth errors
_RETRYABLE_TYPES = (
    api_exceptions.TooManyRequests,     # 429
    api_exceptions.InternalServerError, # 500
    api_exceptions.BadGateway,          # 502
    api_exceptions.ServiceUnavailable,  # 503
    api_exceptions.GatewayTimeout,      # 504
    api_exceptions.DeadlineExceeded,    # 504 / RPC deadline
    ConnectionError,
    requests.ConnectionError,
    requests_exceptions.ChunkedEncodingError,
    requests_exceptions.Timeout,
)


# Some retriable errors don't have their own custom exception in api_core.
_ADDITIONAL_RETRYABLE_STATUS_CODES = (408, 500, 502, 503, 504)

_RETRYABLE_REASONS = frozenset({
    "rateLimitExceeded",
    "userRateLimitExceeded",
    "backendError",
    "internalError",
    "badGateway",
    "serviceUnavailable",
    "deadlineExceeded",
})

# some resources like buckets do not always belong to a specific region.
# if they span multiple regions, their locations can have different values
# in resource dicovery and in report import. here we try to unify those names
# by replacing discovered values with those that we expet to get from
# report import.
REGION_REPLACEMENTS = {
    "eu": "europe"
}



def _is_auth_error(exc: BaseException) -> bool:

    if isinstance(exc, _AUTH_TYPES):
        return True

    if isinstance(exc, auth_exceptions.TransportError):
        try:
            return _is_auth_error(exc.args[0])
        except Exception:
            return False

    if isinstance(exc, api_exceptions.GoogleAPICallError):
        code = getattr(exc, "code", None)
        if code in (401, 403):
            return True

        msg = (str(exc) or "").lower()
        if any(s in msg for s in ("permissiondenied", "unauthenticated", "forbidden")):
            return True
    return False


def _should_retry(exc: BaseException) -> bool:
    """
    Predicate for google.api_core.retry.Retry: True => retry.
    """

    # do not retry auth errors
    if _is_auth_error(exc):
        return False

    if isinstance(exc, _RETRYABLE_TYPES):
        return True

    # Google API call error: inspect status code + 'reason'
    if isinstance(exc, api_exceptions.GoogleAPICallError):
        if getattr(exc, "code", None) in _ADDITIONAL_RETRYABLE_STATUS_CODES:
            return True
        # Some exceptions expose .errors (BigQuery/JSON) like [{'reason': 'rateLimitExceeded', ...}]
        try:
            errors = getattr(exc, "errors", None) or []
            if errors:
                reason = (errors[0] or {}).get("reason")
                if reason in _RETRYABLE_REASONS:
                    return True
        except Exception:
            pass

    if isinstance(exc, auth_exceptions.TransportError):
        try:
            return _should_retry(exc.args[0])
        except Exception:
            return False

    return False


# Exponential retries starting with 10 seconds delay
# and doubling the delay every time. Maximum total
# wait time is 120 seconds.
DEFAULT_RETRY = retry.Retry(
    predicate=_should_retry, deadline=120, initial=10, maximum=120
)
DEFAULT_TIMEOUT_SECONDS = 60
# Default arguments that need to be passed to every cloud API call.
# Some SDK libraries like BigQuery define their own timeout and retries,
# but it is ok to override them. Compute does not define any and
# if there is a network outage, the API call will just hang indefinitely.
DEFAULT_KWARGS = {
    "retry": DEFAULT_RETRY,
    "timeout": DEFAULT_TIMEOUT_SECONDS,
}

BASE_CONSOLE_LINK = "https://console.cloud.google.com"
DEFAULT_CURRENCY = "USD"
OPTSCALE_TRACKING_TAG = "optscale_tracking_id"
STANDARD_BILLING_PREFIX = "gcp_billing_export_v1"

COMPUTE_SERVICE_ID = "6F81-5844-456A"

LOG = logging.getLogger(__name__)


class InstanceType:
    # E2 shared-core custom machine types have fractional vCPUs,
    # but the instance types API says they all have 2 vCPUs.
    SHARED_CPU_VALUES = {
        "micro": 0.25,
        "small": 0.5,
        "medium": 1,
    }
    FAMILIES = {
        'c4a': 'General purpose',
        'c4': 'General purpose',
        'c3': 'General purpose',
        'c3d': 'General purpose',
        'n4': 'General purpose',
        'n2': 'General purpose',
        'n2d': 'General purpose',
        'n1': 'General purpose',
        't2d': 'General purpose',
        't2a': 'General purpose',
        'f1': 'General purpose',
        'g1': 'General purpose',
        'e2': 'Cost optimized',
        'z3': 'Storage optimized',
        'h3': 'Compute optimized',
        'c2': 'Compute optimized',
        'c2d': 'Compute optimized',
        'x4': 'Memory optimized',
        'm3': 'Memory optimized',
        'm2': 'Memory optimized',
        'm1': 'Memory optimized',
        'a3': 'Accelerator optimized',
        'a2': 'Accelerator optimized',
        'g2': 'Accelerator optimized',
    }

    def __init__(self, type_name=None, cpu_cores=None, ram_gb=None,
                 family=None, price=None, custom=False, region=None):
        self.type_name = type_name
        self.cpu_cores = cpu_cores
        self.ram_gb = ram_gb
        self.family = family
        self.family_description = None
        self.custom = custom
        self.price = price
        self.region = region
        self.parse_family_description()

    def parse_family_description(self):
        self.family_description = self.FAMILIES.get(self.family)

    def parse_machine_family(self):
        # turn e.g. "e2-standard-4" into "e2"
        self.family = self.type_name.split("-")[0]
        # N1 family flavors haven't flavor family prefix, example:
        # "custom-2-24576-ext"
        if self.family == "custom":
            self.family = "n1"
        self.parse_family_description()

    def parse_custom(self):
        if "custom" in self.type_name:
            self.custom = True

    def _cpu_value_from_flavor(self, flavor: str=None):
        if not flavor:
            flavor = self.type_name
        elements = flavor.split("-")
        try:
            if len(elements) > 2 and "mem" not in flavor and "cpu" not in flavor:
                cpu_value = flavor.split("-")[-2]
            else:
                cpu_value = flavor.split("-")[-1]
        except ValueError:
            return
        return cpu_value

    def parse_cpu_cores(self, machine_type: compute.MachineType):
        self.cpu_cores = machine_type.guest_cpus
        if machine_type.is_shared_cpu:
            # if machine type has shared CPU, compute API sometimes returns
            # incorrect CPU values
            cpu_value = self._cpu_value_from_flavor()
            fractional_cpu = self.SHARED_CPU_VALUES.get(cpu_value)
            if fractional_cpu is not None:
                self.cpu_cores = fractional_cpu

    def parse_compute_machine_type(self, machine_type: compute.MachineType):
        self.type_name = machine_type.name
        self.parse_machine_family()
        self.parse_custom()
        self.ram_gb = machine_type.memory_mb / 1024
        self.parse_cpu_cores(machine_type)

    def parse_ram_cpu_from_flavor_name(self):
        elements = self.type_name.split("-")
        ram = None
        cpu_value = None
        try:
            if len(elements) > 2:
                ram = int(elements[-1])
            cpu_value = self._cpu_value_from_flavor()
        except ValueError:
            # handle flavors ends with string, examples:
            # custom-2-26624-ext, c4a-highmem-4-lssd
            ram = int(elements[-2])
            cpu_value = self._cpu_value_from_flavor(
                flavor="-".join(elements[:-1]))
        if cpu_value:
            try:
                self.cpu_cores = self.SHARED_CPU_VALUES.get(
                    cpu_value) or float(cpu_value)
            except ValueError:
                pass
        if ram and "mem" not in self.type_name and "cpu" not in self.type_name:
            self.ram_gb = ram / 1024


    def __str__(self) -> str:
        return f"{self.family} {self.cpu_cores} {self.ram_gb} " \
               f"{round(self.price, 4) if self.price else None} {self.region}"

    def to_dict(self) -> dict:
        return {
            "name": self.type_name,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "family": self.family,
            "family_description": self.family_description,
            "custom": self.custom,
            "price": self.price,
            "region": self.region
        }


class MachineFamilyResourcePrice:
    def __init__(self):
        self.vcpu_price = None
        self.ram_gb_price = None

    def set_price(self, sku_text: str, price: float):
        if "Core" in sku_text:
            self.vcpu_price = price
        elif "Ram" in sku_text:
            self.ram_gb_price = price
        else:
            LOG.warning("unknown resource type for sku text %s", sku_text)

    def __str__(self) -> str:
        return f"cpu: {self.vcpu_price} ram: {self.ram_gb_price}"


class GcpResource:
    """
    Base class that contains common methods for transforming GCP SKD resources into our model resources.
    Subsequent classes contain resoruce specific methods.
    """

    def __init__(self, cloud_object, cloud_adapter: "Gcp") -> None:
        self._cloud_object = cloud_object
        self._cloud_adapter = cloud_adapter
        self._common_fields = self._get_common_fields()
        self.cloud_resource_hash = self._cloud_resource_hash()

    def _extract_tags(self):
        # turn a protobuf mapping into a python dict.
        if not hasattr(self._cloud_object, "labels"):
            return {}
        return {key: value for key, value in self._cloud_object.labels.items()}

    @staticmethod
    def _gcp_date_to_timestamp(date):
        return int(
            datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp()
        )

    @staticmethod
    def _last_path_element(url: str) -> str:
        """
        Many properties in GCP are reported in form of URL,
        but we are only interested in the last part.
        For example instance type is:
        'https://www.googleapis.com/compute/v1/projects/hystaxcom/zones/us-central1-a/machineTypes/e2-micro'
        and we want to store it as just 'e2-micro'.
        """
        return url.split("/")[-1]

    def _extract_region(self):
        region = None
        if hasattr(self._cloud_object, "zone"):
            zone = self._last_path_element(self._cloud_object.zone)
            region = self._cloud_adapter.zone_region(zone)
        elif hasattr(self._cloud_object, "region"):
            region = self._last_path_element(self._cloud_object.region)
        return region

    def _get_console_link(self):
        raise NotImplemented()

    def _get_common_fields(self):
        tags = self._extract_tags()
        region = self._extract_region()
        region = Gcp.fix_region(region)
        return dict(
            cloud_resource_id=str(self._cloud_object.id),
            cloud_account_id=self._cloud_adapter.cloud_account_id,
            region=region,
            name=self._cloud_object.name,
            organization_id=self._cloud_adapter.organization_id,
            tags=tags,
            cloud_console_link=self._get_console_link(),
        )

    def _cloud_resource_hash(self):
        return hashlib.sha1(self._cloud_object.self_link.encode()).hexdigest()

    def _need_to_update_tags(self):
        optscale_tag_value = self.tags.get(OPTSCALE_TRACKING_TAG)
        return optscale_tag_value != self.cloud_resource_hash

    def _set_tag(self, key, value):
        raise NotImplemented()

    def post_discover(self):
        if not self._need_to_update_tags():
            return
        self._set_tag(OPTSCALE_TRACKING_TAG, self.cloud_resource_hash)

    def _get_project_id(self):
        return self._cloud_adapter.project_id


class GcpInstance(tools.cloud_adapter.model.InstanceResource, GcpResource):
    def _get_console_link(self):
        zone = self._last_path_element(self._cloud_object.zone)
        name = self._cloud_object.name
        project_id = self._get_project_id()
        return (
            f"{BASE_CONSOLE_LINK}/compute/instancesDetail"
            f"/zones/{zone}/instances/{name}?project_id={project_id}"
        )

    def _extract_instance_disk_image(self):
        # try to determine instance image based on the license of the boot disk
        for disk in self._cloud_object.disks:
            if disk.boot and disk.licenses:
                return disk.licenses[0]
        return None

    def _extract_image_id(self):
        # TODO: need to investigate better when source_machine_image is empty.
        # fallback to reading image info from instance boot disk.
        return (
            self._cloud_object.source_machine_image or self._extract_instance_disk_image()
        )

    def _extract_flavor(self):
        # turn 'https://www.googleapis.com/compute/v1/projects/hystaxcom/zones/us-central1-a/machineTypes/e2-micro'
        # into e2-micro.
        return self._last_path_element(self._cloud_object.machine_type)

    def _extract_network(self):
        network_link = self._cloud_object.network_interfaces[0].network
        network_name = self._last_path_element(network_link)
        network_id = self._cloud_adapter.network_name_to_id.get(network_name)
        return network_id, network_name, network_link

    @staticmethod
    def _get_architecture(flavor: str) -> str:
        flavor = flavor.lower()
        if flavor.startswith("t2a-"):
            return "arm64"
        return "x86_64"

    def __init__(self, cloud_instance: compute.Instance, cloud_adapter: "Gcp"):
        GcpResource.__init__(self, cloud_instance, cloud_adapter)

        flavor = self._extract_flavor()
        image_id = self._extract_image_id()
        cloud_created_at = self._gcp_date_to_timestamp(
            cloud_instance.creation_timestamp
        )
        spotted = cloud_instance.scheduling.provisioning_model == "SPOT"
        stopped_allocated = cloud_instance.status == 'SUSPENDED'
        network_id, network_name, network_link = self._extract_network()
        security_groups = list(cloud_instance.tags.items)
        zone_id = self._last_path_element(self._cloud_object.zone)
        architecture = self._get_architecture(flavor)
        super().__init__(
            **self._common_fields,
            flavor=flavor,
            security_groups=security_groups,
            spotted=spotted,
            stopped_allocated=stopped_allocated,
            image_id=image_id,
            cloud_created_at=cloud_created_at,
            vpc_id=network_id,
            vpc_name=network_name,
            zone_id=zone_id,
            architecture=architecture
        )

    def _new_labels_request(self, key, value):
        labels = self._cloud_object.labels
        labels[key] = value
        labels_request = compute.InstancesSetLabelsRequest(
            label_fingerprint=self._cloud_object.label_fingerprint,
            labels=labels,
        )
        return labels_request

    def _set_tag(self, key, value):
        labels_request = self._new_labels_request(key, value)
        zone = self._last_path_element(self._cloud_object.zone)
        self._cloud_adapter.compute_instances_client.set_labels(
            project=self._cloud_adapter.project_id,
            zone=zone,
            instance=self._cloud_object.name,
            instances_set_labels_request_resource=labels_request,
            **DEFAULT_KWARGS,
        )

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class GcpVolume(tools.cloud_adapter.model.VolumeResource, GcpResource):
    def _get_console_link(self):
        zone = self._last_path_element(self._cloud_object.zone)
        name = self._cloud_object.name
        project_id = self._get_project_id()
        return (
            f"{BASE_CONSOLE_LINK}/compute/disksDetail"
            f"/zones/{zone}/disks/{name}?project_id={project_id}"
        )

    def _extract_zone_id(self):
        return self._last_path_element(self._cloud_object.zone)

    def _extract_disk_attached(self):
        last_attach = self._cloud_object.last_attach_timestamp
        last_detach = self._cloud_object.last_detach_timestamp
        return last_attach > last_detach

    def _extract_disk_type(self):
        # turn 'projects/project/zones/zone/diskTypes/pd-ssd'
        # into pd-ssd.
        return GcpResource._last_path_element(self._cloud_object.type_)

    def __init__(self, cloud_volume: compute.Disk, cloud_adapter):
        GcpResource.__init__(self, cloud_volume, cloud_adapter)
        attached = self._extract_disk_attached()
        type_ = self._extract_disk_type()
        zone_id = self._extract_zone_id()
        super().__init__(
            **self._common_fields,
            size=gbs_to_bytes(cloud_volume.size_gb),
            volume_type=type_,
            attached=attached,
            zone_id=zone_id,
            image_id=cloud_volume.source_image_id,
            snapshot_id=cloud_volume.source_snapshot_id
        )

    def _new_labels_request(self, key, value):
        labels = self._cloud_object.labels
        labels[key] = value
        labesl_request = compute.ZoneSetLabelsRequest(
            label_fingerprint=self._cloud_object.label_fingerprint,
            labels=labels,
        )
        return labesl_request

    def _set_tag(self, key, value):
        labesl_request = self._new_labels_request(key, value)
        zone = self._last_path_element(self._cloud_object.zone)
        self._cloud_adapter.compute_disks_client.set_labels(
            project=self._cloud_adapter.project_id,
            zone=zone,
            resource=self._cloud_object.name,
            zone_set_labels_request_resource=labesl_request,
            **DEFAULT_KWARGS,
        )

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class GcpImage(tools.cloud_adapter.model.ImageResource, GcpResource):
    def _get_console_link(self):
        name = self._cloud_object.name
        project_id = self._get_project_id()
        return (
            f"{BASE_CONSOLE_LINK}/compute/imagesDetail/"
            f"projects/{project_id}/global/images/{name}"
        )

    def __init__(self, cloud_image: compute.Image, cloud_adapter):
        GcpResource.__init__(self, cloud_image, cloud_adapter)
        super().__init__(
            **self._common_fields,
            disk_size=cloud_image.disk_size_gb,
            cloud_created_at=self._gcp_date_to_timestamp(
                cloud_image.creation_timestamp),
            snapshot_id=(cloud_image.source_snapshot_id
                         if cloud_image.source_snapshot_id else None)
        )

    def _new_labels_request(self, key, value):
        labels = self._cloud_object.labels
        labels[key] = value
        labels_request = compute.GlobalSetLabelsRequest(
            label_fingerprint=self._cloud_object.label_fingerprint,
            labels=labels,
        )
        return labels_request

    def _set_tag(self, key, value):
        labels_request = self._new_labels_request(key, value)
        self._cloud_adapter.compute_images_client.set_labels(
            project=self._cloud_adapter.project_id,
            resource=self._cloud_object.name,
            global_set_labels_request_resource=labels_request,
            **DEFAULT_KWARGS,
        )

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class GcpSnapshot(tools.cloud_adapter.model.SnapshotResource, GcpResource):
    def _get_console_link(self):
        name = self._cloud_object.name
        project_id = self._get_project_id()
        return (
            f"{BASE_CONSOLE_LINK}/compute/snapshotsDetail"
            f"/projects/{project_id}/global/snapshots/{name}"
            f"?project_id={project_id}"
        )

    def _extract_region(self):
        if self._cloud_object.storage_locations:
            return self._cloud_object.storage_locations[0]

    def __init__(self, cloud_snapshot: compute.Snapshot, cloud_adapter):
        GcpResource.__init__(self, cloud_snapshot, cloud_adapter)
        super().__init__(
            **self._common_fields,
            size=gbs_to_bytes(cloud_snapshot.disk_size_gb),
            description=cloud_snapshot.description,
            state=cloud_snapshot.status,
            volume_id=cloud_snapshot.source_disk_id,
        )

    def _new_labels_request(self, key, value):
        labels = self._cloud_object.labels
        labels[key] = value
        labesl_request = compute.GlobalSetLabelsRequest(
            label_fingerprint=self._cloud_object.label_fingerprint,
            labels=labels,
        )
        return labesl_request

    def _set_tag(self, key, value):
        labels_request = self._new_labels_request(key, value)
        self._cloud_adapter.compute_snapshots_client.set_labels(
            project=self._cloud_adapter.project_id,
            resource=self._cloud_object.name,
            global_set_labels_request_resource=labels_request,
            **DEFAULT_KWARGS,
        )

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class GcpBucket(tools.cloud_adapter.model.BucketResource, GcpResource):

    def __init__(self, cloud_bucket: storage.Bucket, cloud_adapter):
        GcpResource.__init__(self, cloud_bucket, cloud_adapter)
        is_public_acls = False
        is_public_policy = False
        iam_policy = cloud_bucket.get_iam_policy()
        iam = cloud_bucket.iam_configuration
        if iam.public_access_prevention != 'enforced':
            for binding in iam_policy.bindings:
                if "allUsers" in binding["members"]:
                    is_public_policy = True
                    break
            if not iam.uniform_bucket_level_access_enabled:
                acls = list(cloud_bucket.acl)
                for acl in acls:
                    if acl["entity"] == "allUsers":
                        is_public_acls = True
                        break
        super().__init__(
            **self._common_fields,
            is_public_policy=is_public_policy,
            is_public_acls=is_public_acls,
        )

    def _get_console_link(self):
        name = self._cloud_object.name
        return f"{BASE_CONSOLE_LINK}/storage/browser/{name}"

    def _extract_region(self):
        location = self._cloud_object.location.lower()
        if self._cloud_object.location_type == "dual-region":
            # it is possible to configure a bucket to belong to 2 different regions
            # in the same large zone, e.g. europe-west1+europe-west2
            if "nam" in location:
                location = "us"
            elif "europe" in location:
                location = "europe"
            elif "asia" in location:
                location = "asia"
        return location

    def _set_tag(self, key, value):
        labels = self._cloud_object.labels
        labels[key] = value
        self._cloud_object.labels = labels
        self._cloud_object.patch(**DEFAULT_KWARGS)

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class GcpAddress(tools.cloud_adapter.model.IpAddressResource, GcpResource):
    def __init__(self, cloud_address: compute.Address, cloud_adapter):
        GcpResource.__init__(self, cloud_address, cloud_adapter)
        available = cloud_address.status == "RESERVED"
        instance_id = None
        if not available:
            instance_id = cloud_adapter.get_instance_id_for_address(
                cloud_address)
            if not instance_id and cloud_address.users:
                instance_id = cloud_address.users[0]
        super().__init__(
            **self._common_fields,
            available=available,
            instance_id=instance_id,
        )

    def _get_console_link(self):
        return "https://console.cloud.google.com/networking/addresses/list"

    def _new_labels_request(self, key, value, region=True):
        labels = self._cloud_object.labels
        labels[key] = value
        request_map = {
            True: compute.RegionSetLabelsRequest,
            False: compute.GlobalSetLabelsRequest
        }
        labels_request = request_map[region](
            label_fingerprint=self._cloud_object.label_fingerprint,
            labels=labels,
        )
        return labels_request


    def _set_tag(self, key, value):
        region = self._last_path_element(self._cloud_object.region)
        labels_request = self._new_labels_request(key, value,
                                                  region=bool(region))
        if region:
            self._cloud_adapter.compute_addresses_client.set_labels(
                project=self._cloud_adapter.project_id,
                resource=self._cloud_object.name,
                region=region,
                region_set_labels_request_resource=labels_request,
                **DEFAULT_KWARGS,
            )
        else:
            self._cloud_adapter.compute_global_addresses_client.set_labels(
                project=self._cloud_adapter.project_id,
                resource=self._cloud_object.name,
                global_set_labels_request_resource=labels_request,
                **DEFAULT_KWARGS,
            )

    def post_discover(self):
        # Need to explicitly specify which parent's implementation to use
        return GcpResource.post_discover(self)


class Gcp(CloudBase):

    # gcp sdk creates urllib connection pools internally with pool size==10.
    # there seems to be no straightforward way to change that.
    # so we will limit the discovery worker parallelism for gcp instead.
    MAX_PARALLEL_REQUESTS = 10

    BILLING_CREDS = [
        CloudParameter(name="project_id", type=str, required=False),
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
    ]

    def __init__(self, cloud_config, *args, **kwargs):
        self.config = cloud_config
        self._currency = DEFAULT_CURRENCY

    @staticmethod
    def fix_region(region: str) -> str:
        if region:
            region_lower = region.lower()
            region = REGION_REPLACEMENTS.get(region_lower, region_lower)
        return region

    def discovery_calls_map(self):
        return {
            tools.cloud_adapter.model.VolumeResource: self.volume_discovery_calls,
            tools.cloud_adapter.model.InstanceResource: self.instance_discovery_calls,
            tools.cloud_adapter.model.SnapshotResource: self.snapshot_discovery_calls,
            tools.cloud_adapter.model.IpAddressResource: self.ip_address_discovery_calls,
            tools.cloud_adapter.model.BucketResource: self.bucket_discovery_calls,
            tools.cloud_adapter.model.ImageResource: self.image_discovery_calls,
        }

    @property
    def project_id(self):
        return self.config.get("project_id") or self.credentials.get("project_id")

    @property
    def credentials(self):
        return self.config.get("credentials")

    @property
    def cloud_account_id(self):
        return self.config.get("cloud_account_id")

    @property
    def organization_id(self):
        return self.config.get("organization_id")

    @property
    def billing_data(self):
        return self.config.get("billing_data", {})

    @property
    def billing_dataset(self) -> str:
        return self.billing_data.get("dataset_name", "")

    @property
    def billing_table(self) -> str:
        return self.billing_data.get("table_name", "")

    @property
    def billing_project_id(self) -> str:
        return self.billing_data.get("project_id", self.project_id)

    @property
    def pricing_data(self):
        return self.config.get("pricing_data", {})

    @property
    def pricing_dataset(self) -> str:
        return self.pricing_data.get("dataset_name", "")

    @property
    def pricing_table(self) -> str:
        return self.pricing_data.get("table_name", "")

    @property
    def pricing_project_id(self) -> str:
        return self.pricing_data.get("project_id", self.project_id)

    @cached_property
    def bigquery_client(self):
        return bigquery.Client.from_service_account_info(
            self.credentials,
            project=self.project_id,
        )

    @cached_property
    def compute_instances_client(self):
        return compute.InstancesClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_regions_client(self):
        return compute.RegionsClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_zones_client(self):
        return compute.ZonesClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_disks_client(self):
        return compute.DisksClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_snapshots_client(self):
        return compute.SnapshotsClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_images_client(self):
        return compute.ImagesClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_addresses_client(self):
        return compute.AddressesClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_global_addresses_client(self):
        return compute.GlobalAddressesClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def compute_instance_types_client(self):
        return compute.MachineTypesClient.from_service_account_info(
            self.credentials)

    @cached_property
    def compute_firewall_client(self):
        return compute.FirewallsClient.from_service_account_info(
            self.credentials)

    @cached_property
    def compute_networks_client(self):
        return compute.NetworksClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def iam_client(self):
        return IAMClient.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def storage_client(self):
        return storage.Client.from_service_account_info(
            self.credentials,
        )

    @cached_property
    def metrics_client(self):
        return monitoring_v3.MetricServiceClient.from_service_account_info(
            self.credentials,
        )

    def _billing_table_full_name(self):
        return f"{self.billing_project_id}.{self.billing_dataset}.{self.billing_table}"

    @staticmethod
    def _get_billing_threshold_date():
        # billing threshold means datasets should be updated at least 3 days ago
        return datetime.now(tz=timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=BILLING_THRESHOLD)

    def _test_bigquery_connection(self):
        dt = self._get_billing_threshold_date()
        query = f"""
            SELECT currency
            FROM `{self._billing_table_full_name()}`
            WHERE TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) >= TIMESTAMP("{dt}")
            LIMIT 1
        """
        query_job = self.bigquery_client.query(query, **DEFAULT_KWARGS)
        result = list(query_job.result())[0]
        if not result or dict(result).get("currency") != self._currency:
            raise tools.cloud_adapter.exceptions.CloudSettingNotSupported(
                'Currency "%s" is not supported' % dict(result).get("currency")
            )
        if self.pricing_data:
            query = f"""
                SELECT pricing_unit
                FROM `{self._pricing_table_full_name()}`
                WHERE TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) >= TIMESTAMP("{dt}")
                LIMIT 1
            """
            query_job = self.bigquery_client.query(query, **DEFAULT_KWARGS)
            try:
                list(query_job.result())[0]
            except Exception as e:
                raise tools.cloud_adapter.exceptions.CloudSettingNotSupported(
                    f'Invalid pricing data table: {str(e)}'
                )

    def _validate_billing_type(self):
        if not self.billing_table.startswith(STANDARD_BILLING_PREFIX):
            raise tools.cloud_adapter.exceptions.InvalidParameterException(
                "Invalid billing type. Expected billing type to be Standard."
            )

    def _validate_billing_config(self):
        if "." in self.billing_dataset:
            raise tools.cloud_adapter.exceptions.InvalidParameterException(
                "Invalid billing dataset_name. Should specify dataset_name and table_name separately."
            )
        if "." in self.billing_table:
            raise tools.cloud_adapter.exceptions.InvalidParameterException(
                "Invalid billing table_name. Should specify dataset_name and table_name separately."
            )

    def _validate_project_id(self):
        if not self.project_id:
            raise tools.cloud_adapter.exceptions.InvalidParameterException(
                "project_id should be set either in data source config or in cloud credentials."
            )

    def _validate_cloud_connection(self):
        try:
            list(self.regions)
        except Exception as ex:
            raise tools.cloud_adapter.exceptions.CloudConnectionError(
                "Failed to connect to the cloud with provided credentials - %s" % ex
            )

    def validate_credentials(self, org_id=None):
        try:
            self._validate_project_id()
            self._validate_billing_config()
            self._validate_billing_type()
            self._validate_cloud_connection()
            self._test_bigquery_connection()
        except api_exceptions.Forbidden as ex:
            # remove new-lines, otherwise tornado will fail to write response
            raise tools.cloud_adapter.exceptions.InvalidParameterException(
                str(ex).replace("\n", " ")
            )
        except Exception as ex:
            raise tools.cloud_adapter.exceptions.CloudConnectionError(str(ex))
        return {"account_id": self.project_id, "warnings": []}

    def get_usage(self, start_date, end_date):
        table_name = self._billing_table_full_name()
        query = f"""
        SELECT
            service.description as service,
            usage_start_time as start_date,
            usage_end_time as end_date,
            export_time, cost, cost_type, location,
            currency, currency_conversion_rate,
            sku.description as sku,
            sku.id as sku_id,
            labels as tags,
            usage.amount as usage_amount,
            usage.unit as usage_unit,
            usage.amount_in_pricing_units as usage_amount_in_pricing_units,
            usage.pricing_unit as usage_pricing_unit,
            system_labels as system_tags,
            credits, adjustment_info
        FROM `{table_name}`
        WHERE
            TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) = TIMESTAMP("{start_date}") AND
            project.id = "{self.project_id}"
        """
        return self.bigquery_client.query(
            query,
            **DEFAULT_KWARGS,
        )

    @cached_property
    def regions(self):
        return [
            region.name
            for region in self.compute_regions_client.list(
                project=self.project_id, **DEFAULT_KWARGS
            )
        ]

    @cached_property
    def zones(self):
        return self.list_zones()

    def list_zones(self, region=None):
        if region:
            request = compute.ListZonesRequest(
                project=self.project_id,
                # search for zones whose names start with the desired region name
                filter=f"name:{region}*",
            )
        else:
            request = compute.ListZonesRequest(project=self.project_id)
        return [
            zone.name
            for zone in self.compute_zones_client.list(
                request=request, **DEFAULT_KWARGS
            )
        ]

    @cached_property
    def region_to_zones_map(self):
        result = defaultdict(list)
        for region in self.regions:
            for zone in self.zones:
                if zone.startswith(region):
                    result[region].append(zone)
        return result

    @cached_property
    def zone_to_region_map(self):
        result = {}
        for region, zones in self.region_to_zones_map.items():
            for zone in zones:
                result[zone] = region
        return result

    def region_zones(self, region):
        return self.region_to_zones_map[region]

    def zone_region(self, zone):
        return self.zone_to_region_map[zone]

    ######################################################################################
    # GENERIC DISCOVERY
    ######################################################################################

    def discover_entities(
        self,
        list_function,
        list_request_type=None,
        **additional_list_args,
    ):
        """
        Generic method for discovering cloud objects. Handles API pagination.
        :param list_function: GCP SDK list function that returns cloud objects,
        e.g. instances_client.list()
        :param list_request_type: GCP SDK list request object type,
        e.g. compute.ListInstancesRequest.
        optional, if not set, list argumetns will be passed directly to the list function.
        :param additional_list_args: additional key-value arguments to pass to the lsit function
        :return: generator of cloud objects
        """
        next_page_token = None
        first_iteration = True
        while next_page_token or first_iteration:
            first_iteration = False

            list_args = dict(
                project=self.project_id,
                page_token=next_page_token,
                max_results=MAX_RESULTS,
            )
            list_args.update(additional_list_args)

            # Some GCP list functions accept special Request object that should contain all the parameters,
            # others accept parameters directly.
            if list_request_type is not None:
                request_object = list_request_type(**list_args)
                list_args = dict(request=request_object)

            entities = list_function(**list_args, timeout=30, retry=DEFAULT_RETRY)

            next_page_token = entities.next_page_token
            for entity in entities:
                yield entity

    ######################################################################################
    # INSTANCE DISCOVERY
    ######################################################################################

    def discover_zone_instances(self, zone):
        return self.discover_entities(
            self.compute_instances_client.list,
            compute.ListInstancesRequest,
            zone=zone,
        )

    def discover_region_instances(self, region):
        for zone in self.region_zones(region):
            for instance in self.discover_zone_instances(zone):
                yield GcpInstance(instance, self)

    def instance_discovery_calls(self):
        return [(self.discover_region_instances, (r,)) for r in self.regions]

    ######################################################################################
    # VOLUME DISCOVERY
    ######################################################################################

    def discover_zone_volumes(self, zone):
        return self.discover_entities(
            self.compute_disks_client.list,
            compute.ListDisksRequest,
            zone=zone,
        )

    def discover_region_volumes(self, region):
        for zone in self.region_zones(region):
            for volume in self.discover_zone_volumes(zone):
                yield GcpVolume(volume, self)

    def volume_discovery_calls(self):
        return [(self.discover_region_volumes, (r,)) for r in self.regions]

    ######################################################################################
    # SNAPSHOT DISCOVERY
    ######################################################################################

    def discover_snapshots(self):
        for snapshot in self.discover_entities(
            self.compute_snapshots_client.list,
            compute.ListSnapshotsRequest,
        ):
            yield GcpSnapshot(snapshot, self)

    def snapshot_discovery_calls(self):
        return [(self.discover_snapshots, ())]

    ######################################################################################
    # IMAGE DISCOVERY
    ######################################################################################

    def discover_images(self):
        for image in self.discover_entities(
            self.compute_images_client.list,
            compute.ListImagesRequest
        ):
            yield GcpImage(image, self)

    def image_discovery_calls(self):
        return [(self.discover_images, ())]

    ######################################################################################
    # BUCKET DISCOVERY
    ######################################################################################

    def discover_buckets(self):
        for bucket in self.discover_entities(
            self.storage_client.list_buckets,
            max_results=None,
            page_size=MAX_RESULTS,
        ):
            yield GcpBucket(bucket, self)

    def bucket_discovery_calls(self):
        return [(self.discover_buckets, ())]

    ######################################################################################
    # ADDRESS DISCOVERY
    ######################################################################################

    def _discover_instances_ips(self, zone):
        inst_gen = self.discover_zone_instances(zone)
        return list(inst_gen)

    @cached_property
    def _public_ip_to_instance_id_map(self):
        result = {}
        futures = []
        discovery_calls = [(self._discover_instances_ips, (z,)) for z in self.zones]
        instances = []
        with ThreadPoolExecutor(max_workers=self.MAX_PARALLEL_REQUESTS) as executor:
            for call in discovery_calls:
                futures.append(executor.submit(call[0], *call[1]))
        for f in futures:
            res = f.result()
            if isinstance(res, Exception):
                continue
            elif res:
                instances.extend(res)
        for instance in instances:
            for interface in instance.network_interfaces:
                for access_config in interface.access_configs:
                    if access_config.type == "ONE_TO_ONE_NAT":
                        address = access_config.nat_i_p
                        result[address] = instance.id
        return result

    def get_instance_id_for_address(self, address: compute.Address):
        return self._public_ip_to_instance_id_map.get(address.address)

    def discover_ip_addresses(self, region):
        if region:
            addresses = self.discover_entities(
                self.compute_addresses_client.list,
                compute.ListAddressesRequest,
                region=region,
            )
        else:
            addresses = self.discover_entities(
                self.compute_global_addresses_client.list,
                compute.ListGlobalAddressesRequest,
            )

        for address in addresses:
            yield GcpAddress(address, self)

    def ip_address_discovery_calls(self):
        return [(self.discover_ip_addresses, (r,))
                for r in self.regions + [None]]

    ######################################################################################
    # NETWORK DISCOVERY
    ######################################################################################

    def discover_networks(self):
        return self.discover_entities(
            self.compute_networks_client.list,
            compute.ListNetworksRequest,
        )

    @cached_property
    def network_name_to_id(self):
        result = {}
        for network in self.discover_networks():
            result[network.name] = str(network.id)
        return result

    def discover_firewalls(self):
        return self.discover_entities(
            self.compute_firewall_client.list,
            compute.ListFirewallsRequest,
            project=self.project_id
        )

    ######################################################################################
    # INSTANCE TYPES DISCOVERY
    ######################################################################################

    # Overview:
    #
    # The pricing data that we parse can be overwieved here:
    # https://console.cloud.google.com/bigquery?referrer=search&project=hystaxcom&ws=!1m23!1m4!4m3!1shystaxcom!2spricing_dataset!3scloud_pricing_export!1m4!1m3!1shystaxcom!2sbquxjob_404aff2_181045e7cfb!3sUS!1m3!3m2!1shystaxcom!2spricing_dataset!1m3!8m2!1s552850744845!2s42172348a7d84df384be41920e496fc4!1m4!1m3!1shystaxcom!2sbquxjob_514240c8_18143d887e2!3sUS&pli=1
    #
    # We are mainly interested in 2 columns: sku.description and list_price.
    # Sku description usually has the form:
    # "M3 Memory-optimized Instance Ram running in Las Vegas".
    # The first part describes machine family. E.g. "M3 Memory-optimized Instance" means "m3" machine family.
    # The second part describes resource type. "Core" means CPU and "Ram" means Ram.
    # The last part means region. E.g. "Las Vegas" means "us-west4".
    # There is no API that provides mapping between these textual descriptions in "sku" and
    # real values of regions and machine families. To overcome this we have hardcoded mappings in cloud adapter.
    # So it is possible that in the future we will have to extend these maps.
    #
    # To discover the price of e.g. "e2-standard-32" instance type, we need to
    # find out how many CPU cores and GBs of ram this instance type has,
    # how much 1 CPU core and 1GB of ram costs for the "e2" machine family
    # and do the math.
    # There are some exceptions to this. "g1" and "f1" instances do not allow custom
    # numbers of CPU and Ram and are billed per instance as a whole.
    # M2 instances are "extra memory" instances and are billed as "m1" instances plus
    # some premium for the additional Cpu and Ram.

    def _pricing_table_full_name(self) -> str:
        return f"{self.pricing_project_id}.{self.pricing_dataset}.{self.pricing_table}"

    @cached_property
    def _resource_priced_machine_series_descriptions(self) -> dict:
        return {
            "A2 Instance": "a2",
            "A3 Instance": "a3",
            "C2D AMD Instance": "c2d",
            "Compute optimized": "c2",
            "C3 Instance": "c3",
            "C3D Instance": "c3d",
            "C4 Instance": "c4",
            "C4A Arm Instance": "c4a",
            "E2 Instance": "e2",
            "G2 Instance": "g2",
            "Memory-optimized Instance": "m1",
            "Memory Optimized Upgrade Premium for Memory-optimized Instance": "m2",
            "M3 Memory-optimized Instance": "m3",
            "N1 Predefined Instance": "n1",
            "N2 Instance": "n2",
            "N2D AMD Instance": "n2d",
            "N4 Instance": "n4",
            "T2D AMD Instance": "t2d",
            "T2A Arm Instance": "t2a",
            "X4 Instance": "x4",
            "Z3 Instance": "z3",
        }

    @cached_property
    def _special_machine_series_descriptions(self) -> dict:
        return {
            "f1-micro": "Micro Instance with burstable CPU",
            "g1-small": "Small Instance with 1 VCPU",
        }

    @staticmethod
    def _build_sku_description_pattern(
        sku_text: str, location: str, wildcard_prefix: bool, custom: bool=False
    ) -> str:
        # sample pattern values:
        # '%Instance Core running in Delhi'
        # 'Small Instance with 1 VCPU running in London'
        # 'E2 Custom Instance Core running in Americas'
        prefix = "%" if wildcard_prefix else ""
        if custom:
            if 'Instance' in sku_text:
                sku_text.replace('Instance', 'Custom Instance')
            else:
                sku_text = f"Custom%{sku_text}"
        return f"{prefix}{sku_text} running in {location}"

    def _build_pricing_query(self, sku_desription_pattern: str) -> str:
        # sample query that we are building here:
        # SELECT prices.list_price
        # FROM `hystaxcom.pricing_dataset.cloud_pricing_export` prices
        # INNER JOIN (SELECT sku.id as sku_id, max(export_time) as export_time
        #             FROM `hystaxcom.pricing_dataset.cloud_pricing_export`
        #             WHERE service.id = '6F81-5844-456A'
        #               AND sku.description LIKE '%Instance Core running in Delhi'
        #             GROUP BY sku.id) inr
        # ON    prices.sku.id = inr.sku_id
        #   AND prices.export_time = inr.export_time
        dt = self._get_billing_threshold_date()
        inner_query = f"""
            SELECT sku.id as sku_id, max(export_time) as export_time
            FROM `{self._pricing_table_full_name()}`
            WHERE service.id = '{COMPUTE_SERVICE_ID}'
                AND sku.description LIKE '{sku_desription_pattern}'
                AND TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) >= TIMESTAMP("{dt}")
            GROUP BY sku.id"""
        query = f"""
            SELECT prices.list_price, prices.sku
            FROM `{self._pricing_table_full_name()}` prices
            INNER JOIN ({inner_query}) inr
                ON prices.sku.id = inr.sku_id
                AND prices.export_time = inr.export_time
            WHERE TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) >= TIMESTAMP("{dt}")
        """
        return query

    def _query_prices(self, sku_desription_pattern: str):
        query = self._build_pricing_query(sku_desription_pattern)
        try:
            query_job = self.bigquery_client.query(query, **DEFAULT_KWARGS)
            result = query_job.result()
        except Forbidden as ex:
            raise ForbiddenException(str(ex))
        return result

    @staticmethod
    def _parse_price(row, usd=True) -> float:
        amount_field = "account_currency_amount"
        if usd:
            amount_field = "usd_amount"
        # use tier 0 rate because this is the base price
        # and we don't know if a customer has any usage discounts.
        highest_price = row.list_price["tiered_rates"][0][amount_field]
        return highest_price

    def _parse_machine_family(self, row) -> (str, str):
        # - take sku description:
        #     M3 Memory-optimized Instance Core running in Las Vegas
        # - remove location part starting from "running":
        #     M3 Memory-optimized Instance Core
        # - remove sku type related words "Custom", "Core", "Ram":
        #    M3 Memory-optimized Instance
        # - lookup the remaining string in the map and get the family name (m3):
        #    M3 Memory-optimized Instance
        sku_description = row.sku["description"]
        custom = 'Custom' in sku_description
        sku_description = sku_description.split('running')[0]
        for param in ["Core", "Ram", "Custom"]:
            sku_description = sku_description.replace(param + " ", "")
        sku_description = sku_description.rstrip()
        machine_family = self._resource_priced_machine_series_descriptions.get(
            sku_description
        )
        if not machine_family and custom and sku_description == "Instance":
            # sku description for custom instance flavor for N1 family doesn't
            # contain N1 family name:
            # - Custom Instance Core running in Americas
            # - Custom Instance Ram running in Americas
            # so after processing it's just "Instance"
            machine_family = "n1"
        return machine_family, custom

    @staticmethod
    def _update_m2_prices(
            prices: Dict[Tuple[str, bool], MachineFamilyResourcePrice]):
        # m2 instance family is a special case.
        # Pricing table only contains "premium" prices
        # that need to be added to the regular m1 prices.
        if ("m2", False) in prices and ("m1", False) in prices:
            prices[("m2", False)].vcpu_price += prices[
                ("m1", False)].vcpu_price
            prices[("m2", False)].ram_gb_price += prices[
                ("m1", False)].ram_gb_price

    def _get_machine_family_resource_prices(
        self, region: str, usd: bool=True
    ) -> Dict[Tuple, MachineFamilyResourcePrice]:

        def _get_prices(sku_pattern, inst_family_prices):
            for row in self._query_prices(sku_pattern):
                machine_family, custom = self._parse_machine_family(row)
                if not machine_family:
                    continue
                price = self._parse_price(row, usd)
                inst_family_prices[(machine_family, custom)].set_price(
                    sku_text, price)
            return inst_family_prices

        # get per-cpu and per-ram-gb prices for machine families
        locations = self._get_region_locations(region)
        instance_family_prices = defaultdict(MachineFamilyResourcePrice)
        for sku_text in ("Core", "Ram"):
            for location in locations:
                sku_desription_pattern = self._build_sku_description_pattern(
                    sku_text, location, wildcard_prefix=True
                )
                for row in self._query_prices(sku_desription_pattern):
                    machine_family = self._parse_machine_family(row)
                    if not machine_family:
                        continue
                    price = self._parse_price(row, usd)
                    instance_family_prices[machine_family].set_price(
                        sku_text, price)
        self._update_m2_prices(instance_family_prices)
        return instance_family_prices

    def _get_special_instance_type_prices(
            self, region: str, usd: bool=True) -> dict:
        # get prices for instance types which are not prices separately for
        # each CPU core and each GB of RAM
        locations = self._get_region_locations(region)
        instance_type_prices = {}
        for (
            instance_type,
            sku_text,
        ) in self._special_machine_series_descriptions.items():
            for location in locations:
                sku_desription_pattern = self._build_sku_description_pattern(
                    sku_text, location, wildcard_prefix=False
                )
                for row in self._query_prices(sku_desription_pattern):
                    price = self._parse_price(row, usd)
                    instance_type_prices[instance_type] = price
        return instance_type_prices

    def get_instance_types(self, region: str) -> Dict[str, InstanceType]:
        request = compute.AggregatedListMachineTypesRequest(
            filter=f"zone:{region}*",
            project=self.project_id,
        )
        response = self.compute_instance_types_client.aggregated_list(
            request=request, **DEFAULT_KWARGS
        )
        result = {}
        for zone, node_types in response:
            for machine_type in node_types.machine_types:
                instance_type = InstanceType(region=region)
                instance_type.parse_compute_machine_type(machine_type)
                instance_type.parse_machine_family()
                result[instance_type.type_name] = instance_type
        return result

    @staticmethod
    def get_instance_type_resource_based_price(
        instance_type: InstanceType, resource_prices: MachineFamilyResourcePrice
    ) -> float:
        cpu_price = instance_type.cpu_cores * resource_prices.vcpu_price
        ram_price = instance_type.ram_gb * resource_prices.ram_gb_price
        return cpu_price + ram_price

    def get_instance_type_by_name(
            self, region: str, flavor: str) -> Dict[str, InstanceType]:
        request = compute.GetMachineTypeRequest(
            zone=region,
            project=self.project_id,
            machine_type=flavor
        )
        response = self.compute_instance_types_client.get(
            request=request, **DEFAULT_KWARGS
        )
        result = {}
        instance_type = InstanceType(region=region)
        instance_type.parse_compute_machine_type(response)
        return result

    @staticmethod
    def get_instance_type_price(
        instance_type: InstanceType,
        instance_type_prices: dict,
        machine_family_prices: dict,
    ) -> float:
        instance_type_price = instance_type_prices.get(instance_type.type_name)
        if instance_type_price is not None:
            return instance_type_price
        machine_family = instance_type.family
        custom = instance_type.custom
        resource_prices = machine_family_prices.get((machine_family, custom))
        if not resource_prices:
            return None
        if not resource_prices.vcpu_price or not resource_prices.ram_gb_price:
            return None
        return Gcp.get_instance_type_resource_based_price(
            instance_type, resource_prices
        )

    @property
    def _family_max_cpu_map(self):
        return {
            "e2": {
                "cpu": {"min": 0.25, "max": 22},
                "ram": {"min": 1, "max": 128},
                "min_ram_per_cpu": 0.5,
                "max_ram_per_cpu": 8,
                "cpu_step": 2,
            },
            "n1": {
                "cpu": {"min": 1, "max": 96},
                "ram": {"min": 1, "max": 624},
                "min_ram_per_cpu": 1,
                "max_ram_per_cpu": 6.5,
                "cpu_step": 2,
                "extended": True
            },
            "n2": {
                "cpu": {"min": 2, "max": 128},
                "ram": {"min": 2, "max": 864},
                "min_ram_per_cpu": 0.5,
                "max_ram_per_cpu": 8,
                "cpu_step": 2,
                "extended": True
            },
            "n2d": {
                "cpu": {"min": 2, "max": 224},
                "ram": {"min": 2, "max": 892},
                "min_ram_per_cpu": 0.5,
                "max_ram_per_cpu": 8,
                "cpu_step": 2,
                "extended": True
            },
            "n4": {
                "cpu": {"min": 2, "max": 80},
                "ram": {"min": 4, "max": 640},
                "min_ram_per_cpu": 2,
                "max_ram_per_cpu": 8,
                "cpu_step": 2,
                "extended": True
            }
        }

    @staticmethod
    def gbs_to_mbs(value):
        return value * 1024

    @staticmethod
    def mbs_to_gbs(value):
        return value / 1024

    def _generate_instance_types(
            self, source_instance_type: InstanceType,
            instance_types: Dict[str, InstanceType]=None,
            region: str=None, cpu_limit: float=0
    ):
        custom_instance_types = {}
        ram_step = 256
        predefined_flavors = []
        if instance_types:
            predefined_flavors = [
                (value.cpu_cores, value.ram_gb)
                for value in instance_types.values()
                if source_instance_type.family == value.family]
        family_description = self._family_max_cpu_map.get(
            source_instance_type.family)
        min_cpu = family_description["cpu"]["min"]
        max_cpu = family_description["cpu"]["max"]
        min_ram_gb = family_description["ram"]["min"]
        max_ram_gb = family_description["ram"]["max"]
        min_ram_per_cpu = family_description["min_ram_per_cpu"]
        family_max_ram_per_cpu = family_description["max_ram_per_cpu"]
        extended = family_description.get("extended")
        cpu_step = family_description["cpu_step"]

        max_ram_per_cpu = family_max_ram_per_cpu
        if source_instance_type.type_name.endswith("-ext") and extended:
            # extended memory flavors has no max ram per cpu limit
            max_ram_per_cpu = max_ram_gb

        if cpu_limit <= min_cpu < 2:
            for cpu_fraction in [0.25, 0.5, 1]:
                if cpu_fraction < min_cpu:
                    continue
                instance_type = InstanceType(cpu_cores=cpu_fraction,
                                             custom=True, region=region)
                cpu_name = next(
                    k for k, v in instance_type.SHARED_CPU_VALUES.items()
                    if v == cpu_fraction
                )
                size_ram_max_gb = cpu_fraction * max_ram_per_cpu
                size_ram_max_mb = self.gbs_to_mbs(size_ram_max_gb)
                size_ram_min_gb = cpu_fraction * min_ram_per_cpu
                if size_ram_min_gb < min_ram_gb:
                    size_ram_min_gb = min_ram_gb
                size_ram_min_mb = self.gbs_to_mbs(size_ram_min_gb)
                for ram_mb in range(int(size_ram_min_mb), int(size_ram_max_mb),
                                    ram_step):
                    instance_type.ram_gb = self.mbs_to_gbs(ram_mb)
                    instance_type.type_name = f"{source_instance_type.family}" \
                                              f"-custom-{cpu_name}-{ram_mb}"
                    instance_type.parse_machine_family()
                    custom_instance_types[instance_type.type_name] = instance_type
        min_cpu = 2
        for cpu in range(min_cpu, max_cpu, cpu_step):
            # generate nearest flavors
            if cpu_limit and not cpu_limit <= cpu < cpu_limit + cpu_step:
                continue
            size_ram_max_gb = cpu * max_ram_per_cpu
            if size_ram_max_gb > max_ram_gb:
                size_ram_max_gb = max_ram_gb
            size_ram_max_mb = self.gbs_to_mbs(size_ram_max_gb)
            size_ram_min_gb = cpu * min_ram_per_cpu
            if size_ram_min_gb < min_ram_gb:
                continue
            size_ram_min_mb = self.gbs_to_mbs(size_ram_min_gb)
            for ram_mb in range(int(size_ram_min_mb), int(size_ram_max_mb),
                                ram_step):
                ram_gb = self.mbs_to_gbs(ram_mb)
                if (cpu, ram_gb) in predefined_flavors:
                    continue
                flavor_name = f"custom-{cpu}-{ram_mb}"
                if source_instance_type.family != "n1":
                    flavor_name = f"{source_instance_type.family}-" + flavor_name
                if ram_gb > cpu * family_max_ram_per_cpu:
                    flavor_name = flavor_name + '-ext'
                instance_type = InstanceType(
                    type_name=flavor_name, cpu_cores=cpu, ram_gb=ram_gb,
                    family=source_instance_type.family, custom=True,
                    region=region
                )
                custom_instance_types[
                    instance_type.type_name] = instance_type
        return custom_instance_types

    def get_custom_instance_types(
            self, machine_family_prices: Dict[Tuple, MachineFamilyResourcePrice],
            source_flavor_id: str=None, mode: str=None,
            instance_types: Dict[str, InstanceType]=None,
            region: str=None, cpu: float=0
    ):
        custom_instance_types = {}
        source_instance_type = InstanceType(source_flavor_id)
        source_instance_type.parse_machine_family()
        for family, custom in machine_family_prices:
            if (not custom or family not in self._family_max_cpu_map or (
                    source_instance_type.family != family)):
                continue
            if mode == 'current':
                # parse source instance type
                instance_type = InstanceType(source_flavor_id, region=region)
                instance_type.parse_machine_family()
                instance_type.parse_ram_cpu_from_flavor_name()
                instance_type.parse_custom()
                if instance_type.custom and instance_type.cpu_cores < 1:
                    cpu_name = next((
                        k for k, v in instance_type.SHARED_CPU_VALUES.items()
                        if v == instance_type.cpu_cores), None)
                    if not cpu_name:
                        continue
                    if cpu_name not in instance_type.type_name:
                        instance_type.type_name = instance_type.type_name.replace(
                            str(instance_type.cpu_cores), cpu_name
                        )
                if (source_flavor_id.endswith('-ext') and
                        source_flavor_id[:-4] == instance_type.type_name):
                    instance_type.type_name = source_flavor_id
                custom_instance_types[instance_type.type_name] = instance_type
            else:
                # generate available custom instance types by family
                custom_instance_types = self._generate_instance_types(
                    source_instance_type, instance_types, region, cpu)
        return custom_instance_types

    @staticmethod
    def _is_custom_flavor(source_flavor_id):
        return source_flavor_id and "custom" in source_flavor_id

    def get_instance_types_priced(
            self, region: str, source_flavor_id: str=None, mode: str=None,
            cpu: float=0, use_usd_price: bool=True) -> Dict[str, dict]:
        instance_types = self.get_instance_types(region)
        machine_family_prices = self._get_machine_family_resource_prices(
            region, use_usd_price)
        instance_type_prices = self._get_special_instance_type_prices(
            region, use_usd_price)
        if self._is_custom_flavor(source_flavor_id) or (
                mode != "current" and source_flavor_id):
            custom_types = self.get_custom_instance_types(
                machine_family_prices, source_flavor_id, mode, instance_types,
                region, cpu
            )
            instance_types.update(custom_types)
        result = {}
        for instance_type_name, instance_type in instance_types.items():
            price = self.get_instance_type_price(
                instance_type, instance_type_prices, machine_family_prices
            )
            if price is None:
                LOG.warning(
                    f"failed to dicover price for {instance_type_name} in {region}"
                )
                continue
            instance_type.price = price
            result[instance_type_name] = instance_type.to_dict()
        return result

    ######################################################################################
    # METRICS
    ######################################################################################

    @staticmethod
    def _datetime_to_metrics_time(dt):
        timestamp = dt.timestamp()
        return {"seconds": int(timestamp), "nanos": 0}

    @staticmethod
    def _metrics_interval(start_date, end_date):
        return monitoring_v3.TimeInterval(
            {
                "end_time": Gcp._datetime_to_metrics_time(end_date),
                "start_time": Gcp._datetime_to_metrics_time(start_date),
            }
        )

    @staticmethod
    def _metrics_aggregation(interval):
        return monitoring_v3.Aggregation(
            {
                "alignment_period": {"seconds": interval},
                "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            }
        )

    @staticmethod
    def _metrics_filter(metric_name, instance_ids, id_field):
        type_filter = f'metric.type = "{metric_name}"'
        instance_ids_filter = " OR ".join(
            [
                f"resource.labels.{id_field} = " + instance_id
                for instance_id in instance_ids
            ]
        )
        return f"{type_filter} AND ({instance_ids_filter})"

    def get_metric(self, metric_name, instance_ids, interval, start_date,
                   end_date, id_field="instance_id"):
        results = self.metrics_client.list_time_series(
            request={
                "name": f"projects/{self.project_id}",
                "filter": self._metrics_filter(metric_name, instance_ids,
                                               id_field),
                "interval": self._metrics_interval(start_date, end_date),
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": self._metrics_aggregation(interval),
            },
            **DEFAULT_KWARGS,
        )
        return results

    ######################################################################################
    # NOT IMPLEMENTED
    ######################################################################################

    def pod_discovery_calls(self):
        return []

    def snapshot_chain_discovery_calls(self):
        return []

    def rds_instance_discovery_calls(self):
        return []

    def configure_last_import_modified_at(self):
        pass

    def configure_report(self):
        pass

    def set_currency(self, currency):
        self._currency = currency

    ######################################################################################
    # MISC
    ######################################################################################

    def _get_regions_coordinates(self):
        # based on information from this article - https://cloud.google.com/compute/docs/regions-zones
        return {
            "asia-east1": {
                "latitude": 24.07555,
                "longitude": 120.545067,
                "name": "APAC",
                "alias": "Taiwan"
            },
            "asia-east2": {
                "latitude": 22.396427,
                "longitude": 114.109497,
                "name": "Hong Kong",
            },
            "asia-northeast1": {
                "latitude": 35.689487,
                "longitude": 139.691711,
                "name": "Tokyo",
            },
            "asia-northeast2": {
                "latitude": 34.693737,
                "longitude": 135.502167,
                "name": "Osaka",
            },
            "asia-northeast3": {
                "latitude": 37.566536,
                "longitude": 126.977966,
                "name": "Seoul",
            },
            "asia-south1": {
                "latitude": 19.076111,
                "longitude": 72.8775,
                "name": "Mumbai",
            },
            "asia-south2": {
                "latitude": 28.61,
                "longitude": 77.23,
                "name": "Delhi"
            },
            "asia-southeast1": {
                "latitude": 1.339722,
                "longitude": 103.704444,
                "name": "Singapore",
            },
            "asia-southeast2": {
                "latitude": -6.2,
                "longitude": 106.816667,
                "name": "Jakarta",
            },
            "australia-southeast1": {
                "latitude": -33.867778,
                "longitude": 151.21,
                "name": "Sydney",
            },
            "australia-southeast2": {
                "latitude": -37.816667,
                "longitude": 144.966667,
                "name": "Melbourne",
            },
            "africa-south1": {
                "latitude": -26.195246,
                "longitude": 28.034088,
                "name": "Johannesburg",
            },
            "europe-central2": {
                "latitude": 52.23,
                "longitude": 21.011111,
                "name": "Warsaw",
            },
            "europe-north1": {
                "latitude": 60.566667,
                "longitude": 27.2,
                "name": "Finland",
            },
            "europe-north2": {
                "latitude": 59.334591,
                "longitude": 18.06324,
                "name": "Stockholm",
            },
            "europe-southwest1": {
                "latitude": 40.416667,
                "longitude": -3.716667,
                "name": "Madrid",
            },
            "europe-west1": {
                "latitude": 50.45,
                "longitude": 3.816667,
                "name": "EMEA",
                "alias": "Belgium"
            },
            "europe-west2": {
                "latitude": 51.507222,
                "longitude": -0.1275,
                "name": "London",
            },
            "europe-west3": {
                "latitude": 50.116667,
                "longitude": 8.683333,
                "name": "Frankfurt",
            },
            "europe-west4": {
                "latitude": 53.448333,
                "longitude": 6.831111,
                "name": "Netherlands",
            },
            "europe-west6": {
                "latitude": 47.374444,
                "longitude": 8.541111,
                "name": "Zurich",
            },
            "europe-west8": {
                "latitude": 45.466944,
                "longitude": 9.19,
                "name": "Milan"
            },
            "europe-west9": {
                "latitude": 48.856613,
                "longitude": 2.352222,
                "name": "Paris",
            },
            "europe-west10": {
                "latitude": 52.520008,
                "longitude": 13.404954,
                "name": "Berlin",
            },
            "europe-west12": {
                "latitude": 45.116177,
                "longitude": 7.742615,
                "name": "Turin",
            },
            "me-central1": {
                "latitude": 25.286106,
                "longitude": 51.534817,
                "name": "Doha",
            },
            "me-central2": {
                "latitude": 26.425699,
                "longitude": 50.055164,
                "name": "Dammam",
            },
            "me-west1": {
                "latitude": 32.109333,
                "longitude": 34.855499,
                "name": "Tel Aviv",
            },
            "northamerica-northeast1": {
                "latitude": 45.508889,
                "longitude": -73.554167,
                "name": "Montreal",
            },
            "northamerica-northeast2": {
                "latitude": 43.741667,
                "longitude": -79.373333,
                "name": "Toronto",
            },
            "northamerica-south1": {
                "latitude": 19.432608,
                "longitude": -99.133209,
                "name": "Mexico",
            },
            "southamerica-east1": {
                "latitude": -23.532778,
                "longitude": -46.791944,
                "name": "Sao Paulo",
            },
            "southamerica-west1": {
                "latitude": -33.45,
                "longitude": -70.666667,
                "name": "Santiago",
            },
            "us-central1": {
                "latitude": 41.25,
                "longitude": -95.866667,
                "name": "Iowa",
                "alias": "Americas",
            },
            "us-east1": {
                "latitude": 33.2,
                "longitude": -80,
                "name": "South Carolina",
                "alias": "Americas",
            },
            "us-east4": {
                "latitude": 39.03,
                "longitude": -77.471111,
                "name": "Northern Virginia",
            },
            "us-east5": {
                "latitude": 39.962222,
                "longitude": -83.000556,
                "name": "Columbus",
            },
            "us-south1": {
                "latitude": 32.779167,
                "longitude": -96.808891,
                "name": "Dallas",
            },
            "us-west1": {
                "latitude": 45.601111,
                "longitude": -121.182778,
                "name": "Oregon",
                "alias": "Americas",
            },
            "us-west2": {
                "latitude": 34.05,
                "longitude": -118.25,
                "name": "Los Angeles",
            },
            "us-west3": {
                "latitude": 40.760833,
                "longitude": -111.891111,
                "name": "Salt Lake City",
            },
            "us-west4": {
                "latitude": 36.175,
                "longitude": -115.136389,
                "name": "Las Vegas",
            },
        }

    @staticmethod
    def _add_global_coordinates(regions: dict):
        # in addition to the regular regions, some resources, e.g buckets,
        # can belong to wider areas, like europe or US.
        # simply set locations of some real cities for these larger areas.

        # Dresden
        regions["europe"] = {
            "latitude": 51.05,
            "longitude": 13.74,
            "name": "Europe",
        }
        # Denver
        regions["us"] = {
            "latitude": 39.7392,
            "longitude": -104.985,
            "name": "US",
        }
        # Kathmandu
        regions["asia"] = {
            "latitude": 27.7172,
            "longitude": 85.324,
            "name": "Asia",
        }
        # Global
        regions["global"] = {
            "longitude": -98.48424,
            "latitude": 39.01190,
            "name": 'Global'
        }

        regions["australia-southeast1"]["alias"] = "Australia"
        regions["asia-east2"]["alias"] = "China"

    def get_regions_coordinates(self):
        coordinates = self._get_regions_coordinates()
        self._add_global_coordinates(coordinates)
        return coordinates

    @cached_property
    def _region_locations(self) -> dict:
        result = defaultdict(list)
        for region, coords in self._get_regions_coordinates().items():
            result[region].append(coords["name"])
            alias = coords.get("alias")
            if alias:
                result[region].append(alias)
        return result

    def _get_region_locations(self, region: str) -> list[str]:
        locations = self._region_locations.get(region)
        if locations is None:
            raise RegionNotFoundException(f"Region `{region}` was not found in cloud")
        return locations

    def service_accounts_list(self):
        request = types.ListServiceAccountsRequest()
        request.name = f"projects/{self.project_id}"
        return list(self.iam_client.list_service_accounts(request=request))

    def start_instance(self, instance_name, zone):
        try:
            self.compute_instances_client.start(
                project=self.project_id,
                zone=zone,
                instance=instance_name,
                **DEFAULT_KWARGS,
            )
        except api_exceptions.NotFound as exc:
            raise ResourceNotFound(str(exc))

    def stop_instance(self, instance_name, zone):
        try:
            self.compute_instances_client.stop(
                project=self.project_id,
                zone=zone,
                instance=instance_name,
                **DEFAULT_KWARGS,
            )
        except api_exceptions.NotFound as exc:
            raise ResourceNotFound(str(exc))

