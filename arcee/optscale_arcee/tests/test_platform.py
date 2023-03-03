from unittest.mock import patch
from unittest import IsolatedAsyncioTestCase

from optscale_arcee.platform import (
    Platform,
    AzureCollector,
    CollectorFactory,
    PlatformType,
    AwsCollector,
    PlatformMeta,
    InstanceLifeCycle,
)
from tests.test_data import TestDataAzure


class TestPlatform(IsolatedAsyncioTestCase):
    def test_platform_is_static(self):
        self.assertRaises(TypeError, Platform())

    @patch("optscale_arcee.platform.Platform.sys_vendor")
    async def test_platform_factory(self, mock_sys_vendor):
        mock_sys_vendor.return_value = PlatformType.aws
        self.assertEqual(await CollectorFactory.get(), AwsCollector)


class TestAzureCollector(IsolatedAsyncioTestCase):
    @patch("optscale_arcee.platform.AzureCollector.collect")
    async def test_azure_base_collector(self, mocked_collect):
        mocked_collect.return_value = TestDataAzure.get_test_data()
        platform_meta = await AzureCollector().get_platform_meta()
        self.assertTrue(isinstance(platform_meta, PlatformMeta))
        self.assertTrue(platform_meta.platform_type, PlatformType.azure)
        self.assertTrue(platform_meta.local_ip)
        self.assertTrue(platform_meta.instance_lc, InstanceLifeCycle.Unknown)
        self.assertTrue(platform_meta.to_dict())

    @patch("optscale_arcee.platform.AzureCollector.collect")
    async def test_azure_no_network(self, mocked_collect):
        mocked_collect.return_value = TestDataAzure.get_test_data_no_network()
        platform_meta = await AzureCollector().get_platform_meta()
        self.assertTrue(isinstance(platform_meta, PlatformMeta))
        self.assertTrue(platform_meta.platform_type, PlatformType.azure)
        self.assertFalse(platform_meta.public_ip)
        self.assertFalse(platform_meta.local_ip)
        self.assertTrue(platform_meta.instance_lc, InstanceLifeCycle.Unknown)
        self.assertTrue(platform_meta.to_dict())

    @patch("optscale_arcee.platform.AzureCollector.collect")
    async def test_azure_no_data(self, mocked_collect):
        mocked_collect.return_value = None
        platform_meta = await AzureCollector().get_platform_meta()
        self.assertTrue(isinstance(platform_meta, PlatformMeta))
        self.assertTrue(platform_meta.platform_type, PlatformType.azure)
        self.assertTrue(platform_meta.instance_lc, InstanceLifeCycle.Unknown)
        self.assertTrue(platform_meta.to_dict())


class TestAwsCollector(IsolatedAsyncioTestCase):
    @patch("optscale_arcee.platform.AwsCollector.get_instance_type")
    @patch("optscale_arcee.platform.AwsCollector.get_region")
    @patch("optscale_arcee.platform.AwsCollector.get_az")
    @patch("optscale_arcee.platform.AwsCollector.get_life_cycle")
    @patch("optscale_arcee.platform.AwsCollector.get_public_ip")
    @patch("optscale_arcee.platform.AwsCollector.get_local_ip")
    @patch("optscale_arcee.platform.AwsCollector.get_account_id")
    @patch("optscale_arcee.platform.AwsCollector.get_instance_id")
    async def test_aws_collector_iface(
        self,
        m_instance_id,
        m_account_id,
        m_local_ip,
        m_public_ip,
        m_life_cycle,
        m_az,
        m_region,
        m_type,
    ):
        m_instance_id.return_value = "i-09dc9f5553f84a9ad"
        m_account_id.return_value = "00000000000"
        m_local_ip.return_value = "172.31.24.6"
        m_public_ip.return_value = "1.1.1.1"
        m_life_cycle.return_value = InstanceLifeCycle.OnDemand
        m_az.return_value = "eu-central-1a"
        m_region.return_value = "eu-central-1a"
        m_type.return_value = "m6in.large"
        platform_meta = await AwsCollector().get_platform_meta()
        self.assertTrue(platform_meta.platform_type, PlatformType.aws)
        self.assertTrue(platform_meta.instance_lc, InstanceLifeCycle.OnDemand)
        self.assertTrue(platform_meta.to_dict())
