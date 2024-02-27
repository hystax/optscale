from enum import Enum


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
    ip_address = 'IP Address'
    savings_plan = 'Savings Plan'
    reserved_instances = 'Reserved Instances'
    image = 'Image'

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
                 'cluster_id', 'cluster_type_id')

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
                 'ram', 'platform_id', 'platform_name')

    def __init__(self, name=None, flavor=None, security_groups=None,
                 spotted=False, stopped_allocated=False,
                 last_seen_not_stopped=0, image_id=None,
                 cloud_created_at=0, cpu_count=None, os=None,
                 preinstalled=None, vpc_id=None, vpc_name=None, folder_id=None,
                 zone_id=None, cpu_fraction=None, ram=None, platform_id=None,
                 platform_name=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.flavor = flavor
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
    __slots__ = ('name', 'is_public_policy', 'is_public_acls', 'folder_id')

    def __init__(self, name=None, is_public_policy=False, is_public_acls=False,
                 folder_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.is_public_policy = is_public_policy
        self.is_public_acls = is_public_acls
        self.folder_id = folder_id

    def __repr__(self):
        return 'Bucket {0} name={1} is_public_policy={2} is_public_acls={3}'.format(
            self.cloud_resource_id, self.name, self.is_public_policy,
            self.is_public_acls)

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'is_public_policy': self.is_public_policy,
            'is_public_acls': self.is_public_acls,
            'folder_id': self.folder_id
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
                 'source_cluster_id', 'ram', 'platform_name')

    def __init__(self, name=None, flavor=None, zone_id=None, category=None,
                 engine=None, engine_version=None, storage_type=None,
                 cloud_created_at=0, cpu_count=None, vpc_id=None,
                 vpc_name=None, folder_id=None, source_cluster_id=None,
                 ram=None, platform_name=None, **kwargs):
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
            'platform_name': self.platform_name
        })
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
                 'folder_id')

    def __init__(self, name=None, block_device_mappings=None,
                 cloud_created_at=None, folder_id=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.block_device_mappings = block_device_mappings or []
        self.cloud_created_at = cloud_created_at
        self.folder_id = folder_id

    def __repr__(self):
        return (
            'Image {0} name={1} block_device_mappings={2} '
            'cloud_created_at={3}'.format(
                self.cloud_resource_id, self.name, self.block_device_mappings,
                self.cloud_created_at))

    @property
    def meta(self):
        meta = super().meta
        meta.update({
            'block_device_mappings': self.block_device_mappings,
            'folder_id': self.folder_id
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


# resource type in mariadb -> resource model
RES_MODEL_MAP = {
    ResourceTypes.instance.name: InstanceResource,
    ResourceTypes.volume.name: VolumeResource,
    ResourceTypes.snapshot.name: SnapshotResource,
    ResourceTypes.bucket.name: BucketResource,
    ResourceTypes.k8s_pod.name: PodResource,
    ResourceTypes.snapshot_chain.name: SnapshotChainResource,
    ResourceTypes.rds_instance.name: RdsInstanceResource,
    ResourceTypes.ip_address.name: IpAddressResource,
    ResourceTypes.savings_plan.name: SavingsPlanResource,
    ResourceTypes.reserved_instances.name: ReservedInstancesResource,
    ResourceTypes.image.name: ImageResource,
}
