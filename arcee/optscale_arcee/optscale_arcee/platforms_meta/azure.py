from typing import List


class AzureComputeMeta:
    """
    AzureComputeMeta ...
    """

    def __init__(
        self,
        name: str,
        location: str,
        resourceId: str,
        vmSize: str,
        zone: str,
        subscriptionId: str,
        **kwargs
    ):
        self.name = name
        self.location = location
        self.resourceId = resourceId.lower()
        self.vmSize = vmSize
        self.zone = zone
        self.subscriptionId = subscriptionId


class AzureIpMeta:
    def __init__(self, privateIpAddress: str, publicIpAddress: str, **kwargs):
        self.privateIpAddress = privateIpAddress
        self.publicIpAddress = publicIpAddress


class AzureSubnetMeta:
    def __init__(self, address: str, prefix: str):
        self.address = address
        self.prefix = prefix


class AzureIPv4Meta:
    def __init__(
        self, ipAddress: List[AzureIpMeta], subnet: List[AzureSubnetMeta], **kwargs
    ):
        self.ipAddress = ipAddress
        self.subnet = subnet

    @classmethod
    def from_dict(cls, d):
        ipAddress = d.get("ipAddress")
        if ipAddress:
            d["ipAddress"] = [AzureIpMeta(**addr) for addr in ipAddress]
        subnet = d.get("subnet")
        if subnet:
            d["subnet"] = [AzureSubnetMeta(**sbn) for sbn in subnet]
        return cls(**d)


class AzureInterfaceMeta:
    def __init__(self, ipv4: AzureIPv4Meta, macAddress: str, **kwargs):
        self.ipv4 = ipv4
        self.macAddress = macAddress

    @classmethod
    def from_dict(cls, d):
        ipv4 = d.get("ipv4")
        if ipv4:
            d["ipv4"] = AzureIPv4Meta.from_dict(ipv4)
        return cls(**d)


class AzureNetworkMeta:
    def __init__(self, interface: List[AzureInterfaceMeta]):
        self.interface = interface

    @classmethod
    def from_dict(cls, d):
        interface = d.get("interface")
        if interface:
            d["interface"] = [AzureInterfaceMeta.from_dict(i) for i in interface]
        return cls(**d)


class AzureMeta:
    def __init__(self, compute: AzureComputeMeta, network: AzureNetworkMeta, **kwargs):
        self.compute = compute
        self.network = network

    @classmethod
    def from_dict(cls, d):
        compute = d.get("compute")
        if compute:
            d["compute"] = AzureComputeMeta(**compute)
        network = d.get("network")
        if network:
            d["network"] = AzureNetworkMeta.from_dict(network)
        return cls(**d)
