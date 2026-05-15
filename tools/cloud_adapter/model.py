from enum import Enum

"""
Domain models for discovered cloud resources.

This module defines lightweight dataclasses (via __slots__) representing
cloud resources discovered by the cloud adapter (instances, volumes,
snapshots, buckets, etc.). Each resource exposes:
- attributes used during discovery and post-processing,
- a `meta` property returning fields excluded from general serialization,
- a `to_dict()` method for converting instance state to a dict.

Bucket-related fields include intelligent-tiering and storage-metric
attributes populated by AWS-specific discovery code:
- intelligent_tiering_enabled (bool): whether any Intelligent-Tiering
  configuration exists for the bucket.
- intelligent_tiering_configs (list): raw IntelligentTieringConfigurationList.
- lifecycle_rules (list): lifecycle configuration rules (if present).
- storage_class_analysis (list): analytics configs for storage-class analysis.
- metrics_configurations (list): metrics configs attached to the bucket.
- total_size_bytes (int|None): aggregated bucket size in bytes (if available).
- object_count (int|None): estimated/exact number of objects in the bucket.
- it_status_bucket (str|None): 'enabled' if IT applies to entire bucket.
- tiers (list): per-storage-tier sizes (e.g. Standard, Glacier).
- last_checked (list): dates (YYYY-MM-DD) when GET activity was observed.

Note: the model layer is cloud-agnostic; AWS-specific discovery populates the
bucket intelligent-tiering and CloudWatch-derived metrics.
"""

NONEXISTENT_VOLUME_ID = 'vol-ffffffff'


class ResourceTypes(Enum):
    # resource type in mariadb -> resource type in mongodb
    instance = 'Instance'
    volume = 'Volume'
    snapshot = 'Snapshot'
    bucket = 'Bucket'
    k8s_pod = 'K8s Pod'
    snapshot_chain = 'Snapshot Chain'
    rds_instance = 'RDS Instance'
    redshift_cluster = 'Redshift Cluster'
    redshift_serverless = 'Redshift Serverless'
    emr_application = 'EMR Application'
    ip_address = 'IP Address'
    savings_plan = 'Savings Plan'
    reserved_instances = 'Reserved Instances'
    image = 'Image'
    load_balancer = 'Load Balancer'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def objects(cls):
        return (cls._member_map_[name] for name in cls._member_names_)


class CloudResource:
    __slots__ = ('cloud_resource_id', 'cloud_account_id', 'cloud_account_name',
                 'region', 'organization_id', 'pool_id', 'owner_id',
                 'pool_name', 'owner_name', 'pool_purpose', 'resource_id',
                 'last_seen', 'active', 'tags', 'cloud_console_link',
                 'cluster_id', 'cluster_type_id', 'cloud_type')

    def __init__(self, cloud_resource_id=None, cloud_account_id=None,
                 region=None, organization_id=None,
                 pool_id=None, owner_id=None, tags=None, cloud_console_link=None):
        self.cloud_resource_id = cloud_resource_id
        self.cloud_account_id = cloud_account_id
        self.region = region
        self.organization_id = organization_id
        self.pool_id = pool_id
        self.owner_id = owner_id
        self.pool_name = None  # placeholder
        self.owner_name = None  # placeholder
        self.pool_purpose = None  # placeholder
        self.resource_id = None  # placeholder
        self.last_seen = None  # placeholder
        self.active = None  # placeholder
        self.tags = tags
        self.cloud_console_link = cloud_console_link
        self.cluster_id = None  # placeholder
        self.cluster_type_id = None  # placeholder
        self.cloud_account_name = None  # placeholder
        self.cloud_type = None  # placeholder

    def _is_field(self, attribute):
        if attribute.startswith('_'):
            return False
        if callable(getattr(self, attribute)):
            return False
        return True

    def fields(self, meta_fields_incl=True):
        exclusions = {} if meta_fields_incl else self.meta
        return {attr for attr in dir(self)
                if self._is_field(attr) and attr not in exclusions}

    def to_dict(self):
        result = {}
        for attr in self.fields(meta_fields_incl=False):
            result[attr] = getattr(self, attr)
        return result

    @property
    def meta(self):
        return {
            'cloud_console_link': self.cloud_console_link,
        }

    def post_discover(self):
        # Method that will be called after resource has been discovered
        pass


class InstanceResource(CloudResource):
    __slots__ = ('name', 'flavor', 'security_groups', 'spotted',
                 'stopped_allocated', 'last_seen_not_stopped', 'image_id',
                 'cloud_created_at', 'cpu_count', 'os', 'preinstalled',
                 'vpc_id', 'vpc_name', 'folder_id', 'zone_id', 'cpu_fraction',
                 'ram', 'platform_id', 'platform_name', 'architecture')

    def __init__(self, name=None, flavor=None, security_groups=None,
                 spotted=False, stopped_allocated=False,
                 last_seen_not_stopped=0, image_id=None,
                 cloud_created_at=0, cpu_count=None, os=None,
                 preinstalled=None, vpc_id=None, vpc_name=None, folder_id=None,
                 zone_id=None, cpu_fraction=None, ram=None, platform_id=None,
                 platform_name=None, architecture=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.flavor = flavor
        self.architecture = architecture
        self.security_groups = security_groups
        self.spotted = spotted
        self.stopped_allocated = stopped_allocated
        self.last_seen_not_stopped = last_seen_not_stopped
        self.image_id = image_id
        self.cloud_created_at = cloud_created_at
        self.cpu_count = cpu_count
        self.os = os
        self.preinstalled = preinstalled
        self.vpc_id = vpc_id
        self.vpc_name = vpc_name
        self.folder_id = folder_id
        self.zone_id = zone_id
        self.cpu_fraction = cpu_fraction
        self.ram = ram
        self.platform_id = platform_id
        self.platform_name = platform_name

    def __repr__(self):
        return 'Instance {0} name={1} flavor={2} stopped_allocated={3}'.format(
            self.cloud_resource_id, self.name, self.flavor, self.stopped_allocated)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'stopped_allocated': self.stopped_allocated,
            'last_seen_not_stopped': self.last_seen_not_stopped,
            'spotted': self.spotted,
            'cpu_count': self.cpu_count,
            'os': self.os,
            'security_groups': self.security_groups,
            'image_id': self.image_id,
            'flavor': self.flavor,
            'architecture': self.architecture,
            'preinstalled': self.preinstalled,
            'vpc_id': self.vpc_id,
            'vpc_name': self.vpc_name,
            'folder_id': self.folder_id,
            'zone_id': self.zone_id,
            'cpu_fraction': self.cpu_fraction,
            'ram': self.ram,
            'platform_id': self.platform_id,
            'platform_name': self.platform_name
        })
        return meta


class VolumeResource(CloudResource):
    __slots__ = ('name', 'size', 'volume_type', 'attached', 'last_attached',
                 'snapshot_id', 'folder_id', 'zone_id', 'image_id')

    def __init__(self, name=None, size=None, volume_type=None, attached=False,
                 last_attached=0, snapshot_id=None, folder_id=None,
                 zone_id=None, image_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.size = size
        self.volume_type = volume_type
        self.attached = attached
        self.last_attached = last_attached
        self.snapshot_id = snapshot_id if snapshot_id != '' else None
        self.folder_id = folder_id
        self.zone_id = zone_id
        self.image_id = image_id if image_id != '' else None

    def __repr__(self):
        return 'Volume {0} size={1} type={2} attached={3} snapshot_id={4}'.format(
            self.cloud_resource_id, self.size, self.volume_type,
            self.attached, self.snapshot_id)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'attached': self.attached,
            'last_attached': self.last_attached,
            'size': self.size,
            'volume_type': self.volume_type,
            'snapshot_id': self.snapshot_id,
            'folder_id': self.folder_id,
            'zone_id': self.zone_id,
            'image_id': self.image_id
        })
        return meta


class SnapshotResource(CloudResource):
    __slots__ = ('name', 'size', 'description', 'state', 'volume_id',
                 'last_used', 'folder_id')

    def __init__(self, name=None, size=None, description=None, state=None,
                 volume_id=None, last_used=0, folder_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.size = size
        self.description = description
        self.state = state
        self.volume_id = volume_id if volume_id != NONEXISTENT_VOLUME_ID else None
        self.last_used = last_used
        self.folder_id = folder_id

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'size': self.size,
            'description': self.description,
            'state': self.state,
            'volume_id': self.volume_id,
            'last_used': self.last_used,
            'folder_id': self.folder_id
        })
        return meta

    def __repr__(self):
        return 'Snapshot {0} name={1} size={2} state={3} volume_id={4} info={5}'.format(
            self.cloud_resource_id, self.name, self.size, self.state,
            self.volume_id, self.description)


class BucketResource(CloudResource):
    __slots__ = ('name',
                 'is_public_policy',
                 'is_public_acls',
                 'folder_id',
                 'intelligent_tiering_enabled',
                 'intelligent_tiering_configs',
                 'lifecycle_rules',
                 'storage_class_analysis',
                 'metrics_configurations',
                 'total_size_bytes',
                 'object_count',
                 'it_status_bucket',
                 'tiers',
                 'last_checked',
                )

    def __init__(self,
                name=None,
                is_public_policy=False,
                is_public_acls=False,
                folder_id=None,
                intelligent_tiering_enabled=False,
                intelligent_tiering_configs=None,
                lifecycle_rules=None,
                storage_class_analysis=None,
                metrics_configurations=None,
                total_size_bytes=None,
                object_count=None,
                it_status_bucket=None,
                tiers=None,
                last_checked=None,
                **kwargs
            ):
        """
        Representation of an object storage bucket (S3 / compatible).

        This model stores both generic bucket metadata (name, public flags)
        and intelligent-tiering / storage-analysis attributes that are
        populated by cloud-specific discovery routines (for example,
        AWS provider populates these using S3 and CloudWatch metrics).

        Parameters
        - name (str): bucket name
        - is_public_policy (bool): True if bucket policy exposes public access
        - is_public_acls (bool): True if bucket ACLs expose public access
        - intelligent_tiering_enabled (bool): presence of any IT configuration
        - intelligent_tiering_configs (list): raw IT configuration entries
        - lifecycle_rules (list): lifecycle rules for the bucket
        - storage_class_analysis (list): analytics configuration entries
        - metrics_configurations (list): metrics configuration entries
        - total_size_bytes (int|None): aggregated size in bytes (CloudWatch)
        - object_count (int|None): number of objects (estimate or exact)
        - it_status_bucket (str|None): 'enabled' if IT applies to whole bucket
        - tiers (list): list of [display_name, size_gb] per storage tier
        - last_checked (list): dates strings when object GETs were observed
        """
        super().__init__(**kwargs)
        self.name = name
        self.is_public_policy = is_public_policy
        self.is_public_acls = is_public_acls
        self.folder_id = folder_id

        self.intelligent_tiering_enabled = intelligent_tiering_enabled
        self.intelligent_tiering_configs = intelligent_tiering_configs or []
        self.lifecycle_rules = lifecycle_rules or []
        self.storage_class_analysis = storage_class_analysis or []
        self.metrics_configurations = metrics_configurations or []
        self.total_size_bytes = total_size_bytes
        self.object_count = object_count
        self.it_status_bucket = it_status_bucket
        self.tiers = tiers or []
        self.last_checked = last_checked or []

    def __repr__(self):
        return (
            f"Bucket {self.cloud_resource_id} "
            f"name={self.name} "
            f"is_public_policy={self.is_public_policy} "
            f"is_public_acls={self.is_public_acls} "
            f"IT_enabled={self.intelligent_tiering_enabled}"
            f"IT_configs={self.intelligent_tiering_configs}"
            f"lifecycle_rules={self.lifecycle_rules}"
            f"storage_class_analysis={self.storage_class_analysis}"
            f"metrics_configurations={self.metrics_configurations}"
            f"total_size_bytes={self.total_size_bytes}"
            f"object_count={self.object_count}"
            f"it_status_bucket={self.it_status_bucket}"
            f"tiers={self.tiers}"
            f"last_checked={self.last_checked}"
        )

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'is_public_policy': self.is_public_policy,
            'is_public_acls': self.is_public_acls,
            'folder_id': self.folder_id,
            'intelligent_tiering_enabled': self.intelligent_tiering_enabled,
            'intelligent_tiering_configs': self.intelligent_tiering_configs,
            'lifecycle_rules': self.lifecycle_rules,
            'storage_class_analysis': self.storage_class_analysis,
            'metrics_configurations': self.metrics_configurations,
            'total_size_bytes': self.total_size_bytes,
            'object_count': self.object_count,
            'it_status_bucket': self.it_status_bucket,
            'tiers': self.tiers,
            'last_checked': self.last_checked,
        })
        return meta


class PodResource(CloudResource):
    __slots__ = ('name', 'created_by_kind', 'created_by_name', 'host_ip',
                 'instance_address', 'k8s_node', 'k8s_namespace', 'pod_ip',
                 'k8s_service', 'k8s_cluster')

    def __init__(self, name=None, created_by_kind=None, created_by_name=None,
                 host_ip=None, instance_address=None, k8s_node=None,
                 k8s_namespace=None, pod_ip=None, k8s_service=None,
                 k8s_cluster=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.created_by_kind = created_by_kind
        self.created_by_name = created_by_name
        self.host_ip = host_ip
        self.instance_address = instance_address
        self.k8s_node = k8s_node
        self.k8s_namespace = k8s_namespace
        self.pod_ip = pod_ip
        self.k8s_service = k8s_service
        self.k8s_cluster = k8s_cluster

    def __repr__(self):
        return 'Pod {0} name {1} node={2}'.format(self.cloud_resource_id, self.name, self.k8s_node)

    @property
    def meta(self):
        return {
            'pod_ip': self.pod_ip,
            'instance_address': self.instance_address,
            'host_ip': self.host_ip,
        }

    def to_dict(self):
        result = super().to_dict()
        result.pop('cloud_console_link')
        return result


class SnapshotChainResource(CloudResource):
    __slots__ = ('size', 'volume_id', 'snapshots', 'last_used')

    def __init__(self, size=None, volume_id=None, snapshots=None, last_used=0,
                 **kwargs):
        super().__init__(**kwargs)
        self.size = size
        self.volume_id = volume_id
        self.snapshots = snapshots or []
        self.last_used = last_used

    def __repr__(self):
        return 'SnapshotChain {0} size={1} volume_id={2} snap_ids={3}'.format(
            self.cloud_resource_id, self.size, self.volume_id,
            [x['cloud_resource_id'] for x in self.snapshots])

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'volume_id': self.volume_id,
            'snapshots': self.snapshots,
            'last_used': self.last_used,
            'size': self.size
        })
        return meta


class RdsInstanceResource(CloudResource):
    __slots__ = ('name', 'flavor', 'zone_id', 'category', 'engine',
                 'engine_version', 'storage_type', 'cloud_created_at',
                 'cpu_count', 'vpc_id', 'vpc_name', 'folder_id',
                 'source_cluster_id', 'ram', 'platform_name',
                 'stopped_allocated', 'architecture')

    def __init__(self, name=None, flavor=None, zone_id=None, category=None,
                 engine=None, engine_version=None, storage_type=None,
                 cloud_created_at=0, cpu_count=None, vpc_id=None,
                 vpc_name=None, folder_id=None, source_cluster_id=None,
                 ram=None, platform_name=None, stopped_allocated=False,
                 architecture=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.flavor = flavor
        self.zone_id = zone_id
        self.category = category
        self.engine = engine
        self.engine_version = engine_version
        self.storage_type = storage_type
        self.cloud_created_at = cloud_created_at
        self.cpu_count = cpu_count
        self.vpc_id = vpc_id
        self.vpc_name = vpc_name
        self.folder_id = folder_id
        self.source_cluster_id = source_cluster_id
        self.ram = ram
        self.platform_name = platform_name
        self.stopped_allocated = stopped_allocated
        self.architecture = architecture

    def __repr__(self):
        return 'RDS Instance {0} name={1} flavor={2}'.format(
            self.cloud_resource_id, self.name, self.flavor)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'zone_id': self.zone_id,
            'category': self.category,
            'engine': self.engine,
            'engine_version': self.engine_version,
            'storage_type': self.storage_type,
            'cpu_count': self.cpu_count,
            'flavor': self.flavor,
            'vpc_id': self.vpc_id,
            'vpc_name': self.vpc_name,
            'folder_id': self.folder_id,
            'source_cluster_id': self.source_cluster_id,
            'ram': self.ram,
            'platform_name': self.platform_name,
            'stopped_allocated': self.stopped_allocated,
        })
        return meta


class RedshiftClusterResource(CloudResource):
    __slots__ = ('name', 'flavor', 'stopped_allocated', 'engine',
                 'engine_version', 'cpu_count', 'ram')

    def __init__(self, name=None, flavor=None, stopped_allocated=False,
                 engine=None, engine_version=None, cpu_count=None, ram=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.flavor = flavor
        self.stopped_allocated = stopped_allocated
        self.engine = engine
        self.engine_version = engine_version
        self.cpu_count = cpu_count
        self.ram = ram

    def __repr__(self):
        return 'Redshift Cluster {0} name={1} flavor={2}'.format(
            self.cloud_resource_id, self.name, self.flavor)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'flavor': self.flavor,
            'stopped_allocated': self.stopped_allocated,
            'engine': self.engine,
            'engine_version': self.engine_version,
            'cpu_count': self.cpu_count,
            'ram': self.ram,
        })
        return meta


class EmrApplicationResource(CloudResource):
    __slots__ = ('name', 'stopped_allocated', 'application_type')

    def __init__(self, name=None, stopped_allocated=False,
                 application_type=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.stopped_allocated = stopped_allocated
        self.application_type = application_type

    def __repr__(self):
        return 'EMR Application {0} name={1}'.format(
            self.cloud_resource_id, self.name)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'stopped_allocated': self.stopped_allocated,
            'application_type': self.application_type,
        })
        return meta



class RedshiftServerlessWorkgroupResource(CloudResource):
    __slots__ = ('name', 'stopped_allocated')

    def __init__(self, name=None, stopped_allocated=False, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.stopped_allocated = stopped_allocated

    def __repr__(self):
        return 'Redshift Serverless {0} name={1}'.format(
            self.cloud_resource_id, self.name)

    @property
    def meta(self):
        meta = super().meta
        meta.update({'stopped_allocated': self.stopped_allocated})
        return meta


class IpAddressResource(CloudResource):
    __slots__ = ('name', 'instance_id', 'available', 'last_used', 'folder_id',
                 'zone_id')

    def __init__(self, name=None, instance_id=None, available=False,
                 last_used=0, folder_id=None, zone_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.instance_id = instance_id
        self.available = available
        self.last_used = last_used
        self.folder_id = folder_id
        self.zone_id = zone_id

    def __repr__(self):
        return 'IP Address {0} name={1} instance_id={2} available={3} last_used={4}'.format(
            self.cloud_resource_id, self.name, self.instance_id, self.available, self.last_used)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'available': self.available,
            'last_used': self.last_used,
            'instance_id': self.instance_id,
            'folder_id': self.folder_id,
            'zone_id': self.zone_id
        })
        return meta


class ImageResource(CloudResource):
    __slots__ = ('name', 'block_device_mappings', 'cloud_created_at',
                 'folder_id', 'snapshot_id', 'disk_size')

    def __init__(self, name=None, block_device_mappings=None,
                 cloud_created_at=None, folder_id=None, snapshot_id=None,
                 disk_size=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.block_device_mappings = block_device_mappings or []
        self.cloud_created_at = cloud_created_at
        self.folder_id = folder_id
        self.snapshot_id = snapshot_id
        self.disk_size = disk_size

    def __repr__(self):
        return (
            'Image {0} name={1} block_device_mappings={2} '
            'cloud_created_at={3} snapshot_id={4} disk_size={5}'.format(
                self.cloud_resource_id, self.name, self.block_device_mappings,
                self.cloud_created_at, self.snapshot_id, self.disk_size))

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'block_device_mappings': self.block_device_mappings,
            'folder_id': self.folder_id,
            'snapshot_id': self.snapshot_id,
            'disk_size': self.disk_size,
        })
        return meta


class SavingsPlanResource(CloudResource):
    __slots__ = ('payment_option', 'offering_type', 'purchase_term',
                 'applied_region', 'start', 'end')

    def __init__(self, payment_option=None, offering_type=None,
                 purchase_term=None, applied_region=None, start=None, end=None,
                 **kwargs):
        super().__init__(**kwargs)
        self.payment_option = payment_option
        self.offering_type = offering_type
        self.purchase_term = purchase_term
        self.applied_region = applied_region
        self.start = start
        self.end = end

    def __repr__(self):
        return (
            'Savings Plan {0} payment_option={1} offering_type={2} '
            'purchase_term={3} applied_region={4} start={5} end={6}'.format(
                self.cloud_resource_id, self.payment_option, self.offering_type,
                self.purchase_term, self.applied_region, self.start, self.end))

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'payment_option': self.payment_option,
            'offering_type': self.offering_type,
            'purchase_term': self.purchase_term,
            'applied_region': self.applied_region,
            'start': self.start,
            'end': self.end
        })
        return meta


class ReservedInstancesResource(CloudResource):
    __slots__ = ('payment_option', 'offering_type', 'purchase_term', 'start',
                 'end', 'platform', 'instance_type', 'zone')

    def __init__(self, payment_option=None, offering_type=None,
                 purchase_term=None, start=None, end=None, platform=None,
                 instance_type=None, zone=None, **kwargs):
        super().__init__(**kwargs)
        self.payment_option = payment_option
        self.offering_type = offering_type
        self.purchase_term = purchase_term
        self.start = start
        self.end = end
        self.platform = platform
        self.instance_type = instance_type
        self.zone = zone

    def __repr__(self):
        return (
            'Reserved Instances {0} payment_option={1} offering_type={2} '
            'purchase_term={3} start={4} end={5}'.format(
                self.cloud_resource_id, self.payment_option, self.offering_type,
                self.purchase_term, self.start, self.end))

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'payment_option': self.payment_option,
            'offering_type': self.offering_type,
            'purchase_term': self.purchase_term,
            'start': self.start,
            'end': self.end,
            'platform': self.platform,
            'instance_type': self.instance_type,
            'zone': self.zone
        })
        return meta


class LoadBalancerResource(CloudResource):
    __slots__ = ('name', 'vpc_id', 'security_groups', 'category')

    def __init__(self, name=None, vpc_id=None, security_groups=None,
                 category=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.vpc_id = vpc_id
        self.security_groups = security_groups
        self.category = category

    def __repr__(self):
        return 'Load Balancer {0} name={1}'.format(
            self.cloud_resource_id, self.name)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'vpc_id': self.vpc_id,
            'security_groups': self.security_groups,
            'category': self.category,
        })
        return meta


# resource type in mariadb -> resource model
RES_MODEL_MAP = {
    ResourceTypes.instance.name: InstanceResource,
    ResourceTypes.volume.name: VolumeResource,
    ResourceTypes.snapshot.name: SnapshotResource,
    ResourceTypes.bucket.name: BucketResource,
    ResourceTypes.k8s_pod.name: PodResource,
    ResourceTypes.snapshot_chain.name: SnapshotChainResource,
    ResourceTypes.rds_instance.name: RdsInstanceResource,
    ResourceTypes.redshift_cluster.name: RedshiftClusterResource,
    ResourceTypes.emr_application.name: EmrApplicationResource,
    ResourceTypes.redshift_serverless.name: RedshiftServerlessWorkgroupResource,
    ResourceTypes.ip_address.name: IpAddressResource,
    ResourceTypes.savings_plan.name: SavingsPlanResource,
    ResourceTypes.reserved_instances.name: ReservedInstancesResource,
    ResourceTypes.image.name: ImageResource,
    ResourceTypes.load_balancer.name: LoadBalancerResource,
}
