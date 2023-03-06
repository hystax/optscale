import json
import copy


class TestDataAzure:
    @staticmethod
    def get_test_data():
        return json.dumps(
            {
                "compute": {
                    "azEnvironment": "AzurePublicCloud",
                    "customData": "",
                    "evictionPolicy": "",
                    "extendedLocation": {"name": "", "type": ""},
                    "isHostCompatibilityLayerVm": "false",
                    "licenseType": "",
                    "location": "westeurope",
                    "name": "vlad-ml-mini",
                    "offer": "0001-com-ubuntu-server-focal",
                    "osProfile": {
                        "adminUsername": "ubuntu",
                        "computerName": "vlad-ml-mini",
                        "disablePasswordAuthentication": "true",
                    },
                    "osType": "Linux",
                    "placementGroupId": "",
                    "plan": {"name": "", "product": "", "publisher": ""},
                    "platformFaultDomain": "0",
                    "platformSubFaultDomain": "",
                    "platformUpdateDomain": "0",
                    "priority": "",
                    "provider": "Microsoft.Compute",
                    "publicKeys": [
                        {
                            "keyData": "ssh-rsa AAAAB\n",
                            "path": "/home/ubuntu/.ssh/authorized_keys",
                        }
                    ],
                    "publisher": "canonical",
                    "resourceGroupName": "vlad-rg",
                    "resourceId": "/subscriptions/..",
                    "securityProfile": {
                        "secureBootEnabled": "false",
                        "virtualTpmEnabled": "false",
                    },
                    "sku": "20_04-lts-gen2",
                    "storageProfile": {
                        "dataDisks": [],
                        "imageReference": {
                            "id": "",
                            "offer": "0001-com-ubuntu-server-focal",
                            "publisher": "canonical",
                            "sku": "20_04-lts-gen2",
                            "version": "latest",
                        },
                        "osDisk": {
                            "caching": "ReadWrite",
                            "createOption": "FromImage",
                            "diffDiskSettings": {"option": ""},
                            "diskSizeGB": "30",
                            "encryptionSettings": {"enabled": "false"},
                            "image": {"uri": ""},
                            "managedDisk": {
                                "id": "/subscriptions/7ab2fde4b3b6df3300",
                                "storageAccountType": "Premium_LRS",
                            },
                            "name": "vlad-ml-mini_OsDisk_1_c63ece7f1e0340aab0",
                            "osType": "Linux",
                            "vhd": {"uri": ""},
                            "writeAcceleratorEnabled": "false",
                        },
                        "resourceDisk": {"size": "16384"},
                    },
                    "subscriptionId": "fff",
                    "tags": "",
                    "tagsList": [],
                    "userData": "",
                    "version": "20.04.202209050",
                    "virtualMachineScaleSet": {"id": ""},
                    "vmId": "7940abd0-a8c6-403f-8102-e47738e3cd4a",
                    "vmScaleSetName": "",
                    "vmSize": "Standard_D2s_v3",
                    "zone": "1",
                },
                "network": {
                    "interface": [
                        {
                            "ipv4": {
                                "ipAddress": [
                                    {
                                        "privateIpAddress": "172.18.0.5",
                                        "publicIpAddress": "",
                                    }
                                ],
                                "subnet": [{"address": "172.18.0.0", "prefix": "24"}],
                            },
                            "ipv6": {"ipAddress": []},
                            "macAddress": "000D3A46E876",
                        }
                    ]
                },
            }
        )

    @classmethod
    def get_test_data_no_network(cls):
        d = copy.copy(json.loads(cls.get_test_data()))
        d["network"] = dict()
        return json.dumps(d)
