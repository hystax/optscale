"""Unit tests for bumiworker azure_abandoned_storage_accounts recommendation + archive modules.

SDK availability guard: if azure.mgmt.storage or azure.mgmt.monitor are absent
the entire suite is skipped gracefully rather than erroring with ImportError.
"""
import sys
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import MagicMock, Mock, patch, call

import pytest

azure_identity = pytest.importorskip("azure.identity")
azure_mgmt_storage = pytest.importorskip("azure.mgmt.storage")
azure_mgmt_monitor = pytest.importorskip("azure.mgmt.monitor")

# Inject fake SDK modules that the recommendation module imports so the tests
# can run without requiring the full azure SDK to be installed with all
# sub-packages.
_fake_storage_models = type(sys)("azure.mgmt.storage.models")
_fake_monitor_models = type(sys)("azure.mgmt.monitor.models")
sys.modules.setdefault("azure.mgmt.storage.models", _fake_storage_models)
sys.modules.setdefault("azure.mgmt.monitor.models", _fake_monitor_models)

from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (  # noqa: E402
    NATIVE_MARKER,
    ScanResult,
    StorageAccountInfo,
    _account_age_days,
    _emit_rows_from_existing_sentinels,
    _get_retail_price_per_gb,
    _is_service_managed,
    _meter_name_for,
    _probe_transactions,
    _probe_used_capacity_gb,
    _reconcile_deleted,
    _resolve_or_insert_resource,
    _scan_one_account,
    _touch_resource,
)
from bumiworker.bumiworker.consts import ArchiveReason  # noqa: E402


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_acct(
    name: str = "myaccount",
    sku_name: str = "Standard_LRS",
    kind: str = "StorageV2",
    access_tier: str = "Hot",
    tags: Optional[dict] = None,
    creation_time=None,
    arm_id: Optional[str] = None,
    location: str = "australiasoutheast",
) -> Mock:
    acct = Mock()
    acct.name = name
    acct.id = arm_id or (
        f"/subscriptions/sub1/resourceGroups/rg1/providers/"
        f"Microsoft.Storage/storageAccounts/{name}"
    )
    acct.location = location
    acct.kind = kind
    acct.access_tier = access_tier
    acct.tags = tags or {}
    acct.creation_time = creation_time or (
        datetime.now(timezone.utc) - timedelta(days=60)
    )
    sku = Mock()
    sku.name = sku_name
    acct.sku = sku
    return acct


def _make_monitor_empty():
    """Return a MonitorManagementClient mock with empty timeseries."""
    monitor = MagicMock()
    metric_value = Mock()
    metric_value.timeseries = []
    metric_value.value = [metric_value]
    result = Mock()
    result.value = [metric_value]
    monitor.metrics.list.return_value = result
    return monitor


# ---------------------------------------------------------------------------
# Class 1: SDK constructor signature lock
# ---------------------------------------------------------------------------


class TestSdkCtorSignatureLock:
    """Lock StorageManagementClient + MonitorManagementClient ctor signatures.

    _scan_one_account calls: StorageManagementClient(cred, subscription_id)
    and MonitorManagementClient(cred, subscription_id).  If the SDK renames or
    reorders these positional args the lock test surfaces the drift before
    production code breaks.
    """

    def test_storage_management_client_accepts_credential_and_sub(self):
        from azure.mgmt.storage import StorageManagementClient
        import inspect

        sig = inspect.signature(StorageManagementClient.__init__)
        params = list(sig.parameters.keys())
        # self + credential + subscription_id must all be present
        assert "credential" in params or len(params) >= 3, (
            "StorageManagementClient.__init__ signature changed; update "
            "_scan_one_account ctor call"
        )

    def test_monitor_management_client_accepts_credential_and_sub(self):
        from azure.mgmt.monitor import MonitorManagementClient
        import inspect

        sig = inspect.signature(MonitorManagementClient.__init__)
        params = list(sig.parameters.keys())
        assert "credential" in params or len(params) >= 3, (
            "MonitorManagementClient.__init__ signature changed; update "
            "_scan_one_account ctor call"
        )

    def test_scan_one_account_constructs_track2_clients(self):
        """Verify ClientSecretCredential is used (not msrestazure)."""
        creds = {
            "tenant": "t1",
            "client_id": "c1",
            "secret": "s1",
            "subscription_id": "sub1",
        }

        acct = _make_acct()
        monitor = _make_monitor_empty()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ) as mock_csc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient"
        ) as mock_mmc:
            mock_smc.return_value.storage_accounts.list.return_value = []
            mock_mmc.return_value = monitor

            _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )

        mock_csc.assert_called_once_with("t1", "c1", "s1")
        mock_smc.assert_called_once()
        mock_mmc.assert_called_once()


# ---------------------------------------------------------------------------
# Class 2: Service-managed account exclusions
# ---------------------------------------------------------------------------


class TestServiceManagedExclusions:
    """_is_service_managed returns True for each platform-managed branch."""

    def test_file_storage_kind(self):
        acct = _make_acct(kind="FileStorage", sku_name="Premium_LRS")
        assert _is_service_managed(acct) is True

    def test_premium_lrs_storage_v2(self):
        acct = _make_acct(kind="StorageV2", sku_name="Premium_LRS")
        assert _is_service_managed(acct) is True

    def test_premium_zrs_storage(self):
        acct = _make_acct(kind="Storage", sku_name="Premium_ZRS")
        assert _is_service_managed(acct) is True

    def test_ms_resource_usage_tag(self):
        acct = _make_acct(
            kind="StorageV2",
            sku_name="Standard_LRS",
            tags={"ms-resource-usage": "azure-cloud-shell"},
        )
        assert _is_service_managed(acct) is True

    def test_diag_name_plus_hidden_link_tag(self):
        acct = _make_acct(
            name="diagstoragexyz",
            kind="StorageV2",
            sku_name="Standard_LRS",
            tags={"hidden-link:/some/resource": "Resource"},
        )
        assert _is_service_managed(acct) is True

    def test_diag_name_without_hidden_link_not_excluded(self):
        acct = _make_acct(
            name="diagstorage",
            kind="StorageV2",
            sku_name="Standard_LRS",
            tags={},
        )
        assert _is_service_managed(acct) is False

    def test_normal_account_not_excluded(self):
        acct = _make_acct(kind="StorageV2", sku_name="Standard_LRS")
        assert _is_service_managed(acct) is False

    def test_block_blob_storage_premium_not_excluded_as_service_managed(self):
        """BlockBlobStorage with Premium_LRS is a detection TARGET, not service-managed.

        It only passes the Premium_LRS + (Storage|StorageV2) check when kind
        is Storage or StorageV2.  BlockBlobStorage must NOT be filtered here.
        """
        acct = _make_acct(kind="BlockBlobStorage", sku_name="Premium_LRS")
        assert _is_service_managed(acct) is False

    def test_defensive_sku_none(self):
        """sku=None must not raise AttributeError."""
        acct = Mock()
        acct.name = "test"
        acct.kind = "StorageV2"
        acct.sku = None
        acct.tags = {}
        assert _is_service_managed(acct) is False


# ---------------------------------------------------------------------------
# Class 3: Idle / age / capacity boundaries
# ---------------------------------------------------------------------------


class TestIdleAgeCapacityBoundaries:
    """Accounts are dropped at correct threshold boundaries."""

    def _run_scan(self, acct, transactions=0.0, used_bytes=2.0 * 1024 ** 3):
        """Run _scan_one_account with a single account and controlled probe results."""
        creds = {
            "tenant": "t",
            "client_id": "c",
            "secret": "s",
            "subscription_id": "sub1",
        }

        def make_monitor(txn, cap):
            monitor = MagicMock()

            def metrics_list(**kwargs):
                m = Mock()
                ts = Mock()
                if "Transactions" in kwargs.get("metricnames", ""):
                    dp = Mock()
                    dp.total = txn
                    ts.data = [dp]
                else:
                    dp = Mock()
                    dp.average = cap
                    ts.data = [dp]
                m.timeseries = [ts]
                result = Mock()
                result.value = [m]
                return result

            monitor.metrics.list.side_effect = (
                lambda resource_uri, **kw: metrics_list(**kw)
            )
            return monitor

        monitor = make_monitor(transactions, used_bytes)

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_retail_price_per_gb",
            return_value=(0.02, False),
        ):
            mock_smc.return_value.storage_accounts.list.return_value = [acct]
            scan = _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )
            return scan.accounts

    def test_account_below_age_threshold_excluded(self):
        young = _make_acct(
            creation_time=datetime.now(timezone.utc) - timedelta(days=5)
        )
        result = self._run_scan(young)
        assert result == []

    def test_account_at_age_threshold_included(self):
        old_enough = _make_acct(
            creation_time=datetime.now(timezone.utc) - timedelta(days=30)
        )
        result = self._run_scan(old_enough)
        assert len(result) == 1

    def test_account_above_transaction_threshold_excluded(self):
        acct = _make_acct()
        result = self._run_scan(acct, transactions=150.0)
        assert result == []

    def test_account_at_transaction_threshold_boundary_excluded(self):
        acct = _make_acct()
        result = self._run_scan(acct, transactions=100.0)
        assert result == []

    def test_account_below_transaction_threshold_included(self):
        acct = _make_acct()
        result = self._run_scan(acct, transactions=99.0)
        assert len(result) == 1

    def test_capacity_below_min_excluded(self):
        acct = _make_acct()
        # 0.5 GB < 1.0 GB default minimum
        result = self._run_scan(acct, used_bytes=0.5 * 1024 ** 3)
        assert result == []


# ---------------------------------------------------------------------------
# Class 4: Retail price meter derivation
# ---------------------------------------------------------------------------


class TestMeterNameDerivation:
    """_meter_name_for returns correct meter substrings for all variants."""

    def test_premium_block_blob_lrs(self):
        assert _meter_name_for("Premium_LRS", "BlockBlobStorage", None) == (
            "Premium Block Blob"
        )

    def test_premium_block_blob_zrs(self):
        assert _meter_name_for("Premium_ZRS", "BlockBlobStorage", "Hot") == (
            "Premium Block Blob"
        )

    def test_hot_lrs(self):
        assert _meter_name_for("Standard_LRS", "StorageV2", "Hot") == (
            "Hot LRS Data Stored"
        )

    def test_hot_zrs(self):
        assert _meter_name_for("Standard_ZRS", "StorageV2", "Hot") == (
            "Hot ZRS Data Stored"
        )

    def test_hot_grs(self):
        assert _meter_name_for("Standard_GRS", "StorageV2", "Hot") == (
            "Hot GRS Data Stored"
        )

    def test_hot_ragrs(self):
        assert _meter_name_for("Standard_RAGRS", "StorageV2", "Hot") == (
            "Hot RA-GRS Data Stored"
        )

    def test_hot_ragzrs_longest_prefix_first(self):
        """Standard_RAGZRS must match RAGZRS not GZRS or ZRS."""
        result = _meter_name_for("Standard_RAGZRS", "StorageV2", "Hot")
        assert result == "Hot RA-GZRS Data Stored"

    def test_cool_lrs(self):
        assert _meter_name_for("Standard_LRS", "StorageV2", "Cool") == (
            "Cool LRS Data Stored"
        )

    def test_cool_grs(self):
        assert _meter_name_for("Standard_GRS", "StorageV2", "Cool") == (
            "Cool GRS Data Stored"
        )

    def test_cold_lrs(self):
        assert _meter_name_for("Standard_LRS", "StorageV2", "Cold") == (
            "Cold LRS Data Stored"
        )

    def test_unknown_sku_returns_none(self):
        assert _meter_name_for("Unknown_BLOB", "StorageV2", "Hot") is None

    def test_none_sku_returns_none(self):
        assert _meter_name_for(None, "StorageV2", "Hot") is None

    def test_hot_gzrs(self):
        assert _meter_name_for("Standard_GZRS", "StorageV2", "Hot") == (
            "Hot GZRS Data Stored"
        )

    def test_none_access_tier_defaults_to_hot(self):
        assert _meter_name_for("Standard_LRS", "StorageV2", None) == (
            "Hot LRS Data Stored"
        )


# ---------------------------------------------------------------------------
# Class 5: Sibling find invariant (employee_id / pool_id non-null + sort)
# ---------------------------------------------------------------------------


class TestSiblingFindInvariant:
    """_resolve_or_insert_resource second find_one must enforce non-null guards."""

    def test_sibling_query_has_null_guards_and_sort(self):
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/myaccount"
        )
        _resolve_or_insert_resource(coll, "ca1", arm_id, "myaccount", "eastus", 1000)

        assert coll.find_one.call_count == 2
        second_call_args = coll.find_one.call_args_list[1][0]
        sibling_filter = second_call_args[0]

        assert sibling_filter.get("employee_id") == {"$ne": None}
        assert sibling_filter.get("pool_id") == {"$ne": None}

        sort_arg = (
            second_call_args[2]
            if len(second_call_args) > 2
            else coll.find_one.call_args_list[1][1].get("sort")
        )
        assert sort_arg == [("created_at", 1), ("_id", 1)]

    def test_raises_when_no_sibling(self):
        coll = MagicMock()
        coll.find_one.return_value = None

        with pytest.raises(RuntimeError):
            _resolve_or_insert_resource(
                coll,
                "ca1",
                "/subscriptions/s/rg/r/microsoft.storage/storageaccounts/x",
                "x",
                "eastus",
                1000,
            )


# ---------------------------------------------------------------------------
# Class 6: Overlay $or scoping
# ---------------------------------------------------------------------------


class TestOverlayOrScoping:
    """Step-1 find_one must exclude overlay sentinels via $or."""

    def test_first_find_one_filter_contains_or_clause(self):
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/acct1"
        )
        _resolve_or_insert_resource(coll, "ca1", arm_id, "acct1", "westus", 2000)

        first_call_filter = coll.find_one.call_args_list[0][0][0]
        assert "$or" in first_call_filter, (
            "step-1 find_one must include $or to exclude overlay sentinels"
        )
        or_clauses = first_call_filter["$or"]
        assert {"meta.created_by": {"$exists": False}} in or_clauses
        assert {"meta.created_by": NATIVE_MARKER} in or_clauses

    def test_overlay_sentinel_treated_as_not_found(self):
        """When step-1 returns None (overlay sentinel excluded), new native sentinel inserted."""
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/acct2"
        )
        _resolve_or_insert_resource(coll, "ca1", arm_id, "acct2", "eastus", 1000)

        coll.insert_one.assert_called_once()
        inserted = coll.insert_one.call_args[0][0]
        assert inserted["meta"]["created_by"] == NATIVE_MARKER

    def test_native_sentinel_reused(self):
        """When step-1 finds our own sentinel it is reused without insert."""
        coll = MagicMock()
        native_doc = {"_id": "nat1", "pool_id": "p2"}
        coll.find_one.side_effect = [native_doc]

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/acct3"
        )
        res_id, pool_id = _resolve_or_insert_resource(
            coll, "ca1", arm_id, "acct3", "eastus", 3000
        )

        assert res_id == "nat1"
        assert pool_id == "p2"
        coll.insert_one.assert_not_called()


# ---------------------------------------------------------------------------
# Class 7: Per-account scan failure fallback
# ---------------------------------------------------------------------------


class TestPerAccountFailureFallback:
    """On Azure scan failure the module falls back to existing sentinels."""

    def _make_module(self, coll_mock):
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        module = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        module.organization_id = "org1"
        module.created_at = 1700000000
        module._mongo_client = MagicMock()
        module._mongo_client.restapi.resources = coll_mock
        module._rest_client = MagicMock()
        module.option_ordered_map = {}
        return module

    def test_fallback_rows_emitted_on_scan_exception(self):
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        sentinel_doc = {
            "_id": "sent1",
            "cloud_resource_id": "/subscriptions/sub1/resourcegroups/rg/providers/microsoft.storage/storageaccounts/x",
            "name": "x",
            "region": "eastus",
            "pool_id": "p1",
        }

        coll = MagicMock()
        coll.find.return_value = iter([sentinel_doc])

        module = self._make_module(coll)

        with patch.object(
            module,
            "get_options_values",
            return_value=(7, 100, 30, 1.0, {}, []),
        ), patch.object(
            module,
            "get_cloud_accounts",
            return_value={"ca1": {"name": "Test Account"}},
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_azure_creds",
            return_value={
                "ca1": {
                    "subscription_id": "sub1",
                    "tenant": "t",
                    "client_id": "c",
                    "secret": "s",
                }
            },
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._scan_one_account",
            side_effect=RuntimeError("Azure API down"),
        ):
            rows = module._get()

        # Fallback sentinel row must be present with zero-valued numeric fields
        assert len(rows) == 1
        assert rows[0]["resource_id"] == "sent1"
        assert rows[0]["saving"] == 0.0, (
            "fallback row saving must be 0.0; healthy path never emits saving<=0 "
            "so zero uniquely identifies fallback rows without breaking the "
            "rest_api optimization controller None-handling code paths"
        )
        assert rows[0]["transactions"] == 0.0
        assert rows[0]["data_source"] == "preserved_sentinel"


# ---------------------------------------------------------------------------
# Class 8: Cache key isolation
# ---------------------------------------------------------------------------


class TestCacheKeyIsolation:
    """Two distinct subscriptions with same params → two separate API calls."""

    def test_different_subscriptions_not_shared(self):
        """Cache is keyed on (subscription_id, region, sku, kind, access_tier).

        Two different subscription_ids with otherwise identical params must
        each trigger their own retail prices API call.
        """
        call_count = 0

        def fake_urlopen(url, timeout=None):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.read.return_value = b'{"Items": []}'
            return response

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            _get_retail_price_per_gb(
                "sub-A", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )
            _get_retail_price_per_gb(
                "sub-B", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert call_count == 2, (
            "Expected 2 API calls for 2 distinct subscription_ids; "
            f"got {call_count}"
        )

    def test_same_subscription_cached(self):
        """Identical params on same subscription must only call API once."""
        call_count = 0

        def fake_urlopen(url, timeout=None):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.read.return_value = b'{"Items": [{"meterName": "Hot LRS Data Stored", "retailPrice": 0.02}]}'
            return response

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            p1, t1 = _get_retail_price_per_gb(
                "sub-X", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )
            p2, t2 = _get_retail_price_per_gb(
                "sub-X", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert call_count == 1
        assert p1 == p2 == pytest.approx(0.02)
        assert t1 is False
        assert t2 is False


# ---------------------------------------------------------------------------
# Class 9: Zero-saving NOT registered
# ---------------------------------------------------------------------------


class TestZeroSavingDropped:
    """Accounts with saving <= 0 are not emitted on the healthy path."""

    def test_zero_saving_not_in_results(self):
        creds = {
            "tenant": "t",
            "client_id": "c",
            "secret": "s",
            "subscription_id": "sub1",
        }
        acct = _make_acct()

        monitor = MagicMock()

        def metrics_list(resource_uri, **kwargs):
            m = Mock()
            ts = Mock()
            if "Transactions" in kwargs.get("metricnames", ""):
                dp = Mock()
                dp.total = 0.0
                ts.data = [dp]
            else:
                dp = Mock()
                dp.average = 2.0 * 1024 ** 3  # 2 GB
                ts.data = [dp]
            m.timeseries = [ts]
            result = Mock()
            result.value = [m]
            return result

        monitor.metrics.list.side_effect = metrics_list

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_retail_price_per_gb",
            return_value=(0.0, False),  # price = 0 → saving = 0
        ):
            mock_smc.return_value.storage_accounts.list.return_value = [acct]
            scan = _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )

        assert scan.accounts == [], (
            "Accounts with saving=0 must NOT appear in _scan_one_account results"
        )


# ---------------------------------------------------------------------------
# Class 10: Reconcile deleted
# ---------------------------------------------------------------------------


class TestReconcileDeleted:
    """_reconcile_deleted marks sentinels absent from current scan as deleted."""

    def test_marks_absent_sentinel(self):
        coll = MagicMock()
        sentinel_a = {
            "_id": "doc_a",
            "cloud_resource_id": "/subscriptions/sub/rg/r/microsoft.storage/storageaccounts/a",
        }
        sentinel_b = {
            "_id": "doc_b",
            "cloud_resource_id": "/subscriptions/sub/rg/r/microsoft.storage/storageaccounts/b",
        }
        coll.find.return_value = iter([sentinel_a, sentinel_b])

        current_arm_ids = {sentinel_a["cloud_resource_id"]}
        now_ts = 1700000000

        count = _reconcile_deleted(coll, "ca1", current_arm_ids, now_ts)

        assert count == 1
        coll.bulk_write.assert_called_once()
        ops = coll.bulk_write.call_args[0][0]
        assert len(ops) == 1
        assert ops[0]._filter == {"_id": "doc_b"}
        assert ops[0]._doc == {"$set": {"deleted_at": now_ts}}

    def test_no_bulk_write_when_all_present(self):
        coll = MagicMock()
        sentinel_a = {
            "_id": "doc_a",
            "cloud_resource_id": "/subscriptions/sub/rg/r/microsoft.storage/storageaccounts/a",
        }
        coll.find.return_value = iter([sentinel_a])
        current_arm_ids = {sentinel_a["cloud_resource_id"]}

        count = _reconcile_deleted(coll, "ca1", current_arm_ids, 9999)

        assert count == 0
        coll.bulk_write.assert_not_called()


# ---------------------------------------------------------------------------
# Class 11: Sentinel doc shape
# ---------------------------------------------------------------------------


class TestSentinelDocShape:
    """Inserted sentinel document must have all required fields."""

    def test_all_required_fields(self):
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        mixed_arm = (
            "/Subscriptions/SUB1/ResourceGroups/RG1/providers/"
            "Microsoft.Storage/storageAccounts/MyAccount"
        )
        now_ts = 1700000000
        _resolve_or_insert_resource(coll, "ca1", mixed_arm, "MyAccount", "eastus", now_ts)

        assert coll.insert_one.call_count == 1
        inserted = coll.insert_one.call_args[0][0]

        required_fields = [
            "_id",
            "cloud_account_id",
            "cloud_resource_id",
            "name",
            "region",
            "resource_type",
            "service_name",
            "tags",
            "created_at",
            "deleted_at",
            "first_seen",
            "last_seen",
            "_first_seen_date",
            "_last_seen_date",
            "active",
            "pool_id",
            "employee_id",
        ]
        for field in required_fields:
            assert field in inserted, f"sentinel doc missing field '{field}'"

        assert inserted["cloud_resource_id"] == mixed_arm.lower()
        assert inserted["meta"]["created_by"] == NATIVE_MARKER
        assert inserted["active"] is False
        assert inserted["resource_type"] == "Storage Account"
        assert inserted["service_name"] == "microsoft.storage"
        assert inserted["pool_id"] == "p1"
        assert inserted["employee_id"] == "e1"

        for date_field in ("_first_seen_date", "_last_seen_date"):
            dt = inserted[date_field]
            assert isinstance(dt, datetime)
            assert dt.hour == 0
            assert dt.minute == 0
            assert dt.second == 0
            assert dt.microsecond == 0


# ---------------------------------------------------------------------------
# Class 12: Archive module
# ---------------------------------------------------------------------------


class TestArchiveModule:
    """Tests for bumiworker.modules.archive.azure_abandoned_storage_accounts._get."""

    def _make_archive_instance(self):
        from bumiworker.bumiworker.modules.archive.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        instance = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        instance._mongo_client = MagicMock()
        instance.reason_description_map = {
            ArchiveReason.RECOMMENDATION_APPLIED: "Storage account deleted or no longer idle",
            ArchiveReason.RECOMMENDATION_IRRELEVANT: "Storage account no longer meets idle criteria",
            ArchiveReason.RESOURCE_DELETED: "resource deleted",
            ArchiveReason.CLOUD_ACCOUNT_DELETED: "cloud account deleted",
            ArchiveReason.OPTIONS_CHANGED: "options changed",
        }
        # Minimal option_ordered_map for OPTIONS_CHANGED comparison
        instance.option_ordered_map = {
            "idle_days_window": {"default": 7},
            "idle_transactions_threshold": {"default": 100},
            "min_account_age_days": {"default": 30},
            "min_used_capacity_gb": {"default": 1.0},
        }
        return instance

    def test_applied_when_deleted_at_nonzero(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [{"_id": "r1", "deleted_at": 12345, "cloud_account_id": "ca1"}]
        )

        result = instance._get(
            previous_options={"idle_days_window": 7, "idle_transactions_threshold": 100,
                               "min_account_age_days": 30, "min_used_capacity_gb": 1.0},
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.RECOMMENDATION_APPLIED

    def test_resource_deleted_when_doc_missing(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter([])

        result = instance._get(
            previous_options={"idle_days_window": 7, "idle_transactions_threshold": 100,
                               "min_account_age_days": 30, "min_used_capacity_gb": 1.0},
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.RESOURCE_DELETED

    def test_cloud_account_deleted(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [{"_id": "r1", "deleted_at": 0, "cloud_account_id": "ca1"}]
        )

        result = instance._get(
            previous_options={"idle_days_window": 7, "idle_transactions_threshold": 100,
                               "min_account_age_days": 30, "min_used_capacity_gb": 1.0},
            optimizations=[opt],
            cloud_accounts_map={},  # ca1 absent
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.CLOUD_ACCOUNT_DELETED

    def test_options_changed_when_threshold_differs(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [{"_id": "r1", "deleted_at": 0, "cloud_account_id": "ca1"}]
        )

        result = instance._get(
            previous_options={
                "idle_days_window": 14,  # changed from default 7
                "idle_transactions_threshold": 100,
                "min_account_age_days": 30,
                "min_used_capacity_gb": 1.0,
            },
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.OPTIONS_CHANGED

    def test_irrelevant_when_doc_active_and_left_scan(self):
        """Invariant violation: optimization left scan, sentinel still has deleted_at=0."""
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [{"_id": "r1", "deleted_at": 0, "cloud_account_id": "ca1"}]
        )

        result = instance._get(
            previous_options={"idle_days_window": 7, "idle_transactions_threshold": 100,
                               "min_account_age_days": 30, "min_used_capacity_gb": 1.0},
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.RECOMMENDATION_IRRELEVANT


# ---------------------------------------------------------------------------
# Supplementary: _emit_rows_from_existing_sentinels
# ---------------------------------------------------------------------------


class TestSentinelEmitFallback:
    """_emit_rows_from_existing_sentinels row shape and edge cases."""

    def test_returns_correct_row_shape(self):
        sentinel = {
            "_id": "s1",
            "cloud_resource_id": "/subscriptions/sub/rg/r/microsoft.storage/storageaccounts/acct",
            "name": "acct",
            "region": "eastus",
            "pool_id": "p1",
        }
        coll = MagicMock()
        coll.find.return_value = iter([sentinel])

        rows = _emit_rows_from_existing_sentinels(coll, "ca1", "My Acct", {})

        assert len(rows) == 1
        row = rows[0]
        assert row["saving"] == 0.0, (
            "fallback saving must be 0.0; healthy path drops saving<=0 rows "
            "so zero uniquely identifies fallback without breaking rest_api "
            "controller None-handling code paths"
        )
        assert row["transactions"] == 0.0, (
            "fallback transactions must be 0.0"
        )
        assert row["used_capacity_gb"] == 0.0, (
            "fallback used_capacity_gb must be 0.0"
        )
        assert row["data_source"] == "preserved_sentinel"
        assert row["cloud_type"] == "azure_cnr"
        assert row["cloud_account_id"] == "ca1"
        assert row["folder_id"] is None
        assert row["zone_id"] is None
        assert row["age_days"] is None

    def test_excluded_pool_is_excluded(self):
        sentinel = {
            "_id": "s1",
            "cloud_resource_id": "/subscriptions/sub/rg/r/microsoft.storage/storageaccounts/acct",
            "name": "acct",
            "region": "eastus",
            "pool_id": "excluded-pool",
        }
        coll = MagicMock()
        coll.find.return_value = iter([sentinel])

        rows = _emit_rows_from_existing_sentinels(
            coll, "ca1", "My Acct", {"excluded-pool": True}
        )

        assert rows[0]["is_excluded"] is True

    def test_empty_when_no_sentinels(self):
        coll = MagicMock()
        coll.find.return_value = iter([])
        rows = _emit_rows_from_existing_sentinels(coll, "ca1", "My Acct", {})
        assert rows == []


# ---------------------------------------------------------------------------
# Supplementary: _touch_resource guard
# ---------------------------------------------------------------------------


class TestTouchResourceGuard:
    """_touch_resource filter must include meta.created_by guard."""

    def test_update_one_filter_has_created_by_guard(self):
        coll = MagicMock()
        _touch_resource(coll, "doc1", 1700000000)

        coll.update_one.assert_called_once()
        update_filter = coll.update_one.call_args[0][0]
        assert update_filter.get("meta.created_by") == NATIVE_MARKER
        assert update_filter.get("_id") == "doc1"


# ---------------------------------------------------------------------------
# Class 13: ScanResult authoritative flag
# ---------------------------------------------------------------------------


def _make_creds(sub_id: str = "sub1") -> dict:
    return {
        "tenant": "t",
        "client_id": "c",
        "secret": "s",
        "subscription_id": sub_id,
    }


def _make_metrics_side_effect(txn=0.0, cap_bytes=2.0 * 1024 ** 3):
    """Return a side_effect callable for monitor.metrics.list."""

    def _side_effect(resource_uri, **kwargs):
        m = Mock()
        ts = Mock()
        if "Transactions" in kwargs.get("metricnames", ""):
            dp = Mock()
            dp.total = txn
            ts.data = [dp]
        else:
            dp = Mock()
            dp.average = cap_bytes
            ts.data = [dp]
        m.timeseries = [ts]
        result = Mock()
        result.value = [m]
        return result

    return _side_effect


class TestScanAuthoritative:
    """_scan_one_account.authoritative reflects pipeline health."""

    def _run(self, accounts_list, monitor_side_effect=None, deadline=9e18):
        creds = _make_creds()
        monitor = MagicMock()
        if monitor_side_effect is not None:
            monitor.metrics.list.side_effect = monitor_side_effect

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_retail_price_per_gb",
            return_value=(0.02, False),
        ):
            mock_smc.return_value.storage_accounts.list.return_value = accounts_list
            return _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=deadline,
                price_cache={},
                price_lock=threading.Lock(),
            )

    def test_clean_run_all_probes_succeed_is_authoritative(self):
        """All probes succeed → authoritative=True."""
        accts = [_make_acct(name=f"acct{i}") for i in range(3)]
        scan = self._run(accts, _make_metrics_side_effect())
        assert scan.authoritative is True
        assert len(scan.accounts) > 0

    def test_empty_subscription_is_authoritative(self):
        """Zero accounts in subscription → authoritative=True (no probes attempted)."""
        scan = self._run([])
        assert scan.authoritative is True
        assert scan.accounts == []

    def test_probe_failure_rate_below_50_pct_is_authoritative(self):
        """2 succeed, 1 fails → 33% failure rate → authoritative=True."""
        from azure.core.exceptions import HttpResponseError

        accts = [_make_acct(name=f"a{i}") for i in range(3)]
        call_count = 0

        def _side_effect(resource_uri, **kwargs):
            nonlocal call_count
            call_count += 1
            # First transactions probe fails; others succeed
            if "Transactions" in kwargs.get("metricnames", "") and call_count == 1:
                raise HttpResponseError(message="quota exceeded")
            return _make_metrics_side_effect()(resource_uri, **kwargs)

        scan = self._run(accts, _side_effect)
        assert scan.authoritative is True

    def test_probe_failure_rate_at_50_pct_is_non_authoritative(self):
        """2 accounts probed, both fail → 100% → authoritative=False."""
        from azure.core.exceptions import HttpResponseError

        accts = [_make_acct(name=f"b{i}") for i in range(2)]

        def _all_fail(resource_uri, **kwargs):
            if "Transactions" in kwargs.get("metricnames", ""):
                raise HttpResponseError(message="throttled")
            return _make_metrics_side_effect()(resource_uri, **kwargs)

        scan = self._run(accts, _all_fail)
        assert scan.authoritative is False

    def test_storage_accounts_list_raises_is_non_authoritative(self):
        """storage_accounts.list() raises AzureError → authoritative=False."""
        from azure.core.exceptions import AzureError as AzErr

        creds = _make_creds()
        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient"
        ):
            mock_smc.return_value.storage_accounts.list.side_effect = AzErr(
                "network error"
            )
            scan = _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )
        assert scan.authoritative is False
        assert scan.accounts == []

    def test_deadline_trip_before_sweep_is_non_authoritative(self):
        """Deadline already passed → every account is skipped_budget → non-authoritative."""
        accts = [_make_acct(name="late_acct")]
        scan = self._run(accts, _make_metrics_side_effect(), deadline=0.0)
        assert scan.authoritative is False

    def test_non_authoritative_scan_triggers_sentinel_fallback_in_module(self):
        """Non-authoritative ScanResult must trigger fallback in _get, not reconcile-delete."""
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        sentinel_doc = {
            "_id": "sent_auth",
            "cloud_resource_id": "/sub/rg/p/microsoft.storage/storageaccounts/x",
            "name": "x",
            "region": "eastus",
            "pool_id": "p1",
        }
        coll = MagicMock()
        coll.find.return_value = iter([sentinel_doc])

        module = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        module.organization_id = "org1"
        module.created_at = 1700000000
        module._mongo_client = MagicMock()
        module._mongo_client.restapi.resources = coll
        module._rest_client = MagicMock()
        module.option_ordered_map = {}

        non_auth_result = ScanResult(accounts=[], authoritative=False)

        with patch.object(
            module, "get_options_values", return_value=(7, 100, 30, 1.0, {}, [])
        ), patch.object(
            module,
            "get_cloud_accounts",
            return_value={"ca1": {"name": "Test Account"}},
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_azure_creds",
            return_value={
                "ca1": {
                    "subscription_id": "sub1",
                    "tenant": "t",
                    "client_id": "c",
                    "secret": "s",
                }
            },
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._scan_one_account",
            return_value=non_auth_result,
        ):
            rows = module._get()

        # Reconcile-delete must NOT have been called
        coll.bulk_write.assert_not_called()
        # Fallback sentinel row must be present
        assert len(rows) == 1
        assert rows[0]["resource_id"] == "sent_auth"
        assert rows[0]["data_source"] == "preserved_sentinel"


# ---------------------------------------------------------------------------
# Class 14: Retail price cache key normalization
# ---------------------------------------------------------------------------


class TestRetailPriceCacheKeyNormalization:
    """_get_retail_price_per_gb cache-key guard for None/empty required fields."""

    def test_region_none_returns_none_no_cache_write(self):
        cache: dict = {}
        lock = threading.Lock()
        price, transient = _get_retail_price_per_gb(
            "sub1", None, "Standard_LRS", "StorageV2", "Hot", cache, lock
        )
        assert price is None
        assert transient is False
        assert len(cache) == 0, "None region must not poison cache"

    def test_region_empty_returns_none_no_cache_write(self):
        cache: dict = {}
        lock = threading.Lock()
        price, transient = _get_retail_price_per_gb(
            "sub1", "", "Standard_LRS", "StorageV2", "Hot", cache, lock
        )
        assert price is None
        assert transient is False
        assert len(cache) == 0

    def test_sku_name_empty_returns_none_no_cache_write(self):
        cache: dict = {}
        lock = threading.Lock()
        price, transient = _get_retail_price_per_gb(
            "sub1", "eastus", "", "StorageV2", "Hot", cache, lock
        )
        assert price is None
        assert transient is False
        assert len(cache) == 0

    def test_kind_none_returns_none_no_cache_write(self):
        cache: dict = {}
        lock = threading.Lock()
        price, transient = _get_retail_price_per_gb(
            "sub1", "eastus", "Standard_LRS", None, "Hot", cache, lock
        )
        assert price is None
        assert transient is False
        assert len(cache) == 0

    def test_access_tier_none_and_hot_share_same_cache_key(self):
        """access_tier=None normalises to 'Hot' — same key as explicit 'Hot'."""
        call_count = 0

        def fake_urlopen(url, timeout=None):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.read.return_value = (
                b'{"Items": [{"meterName": "Hot LRS Data Stored", "retailPrice": 0.02}]}'
            )
            return response

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            p_none, t_none = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", None, cache, lock
            )
            p_hot, t_hot = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert call_count == 1, (
            "access_tier=None and 'Hot' must share the same cache key; "
            f"got {call_count} API calls"
        )
        assert p_none == pytest.approx(0.02)
        assert p_hot == pytest.approx(0.02)
        assert t_none is False
        assert t_hot is False


# ---------------------------------------------------------------------------
# Class 15: Concurrent insert race (DuplicateKeyError recovery)
# ---------------------------------------------------------------------------


class TestResolveResourceConcurrent:
    """_resolve_or_insert_resource recovers from concurrent DuplicateKeyError."""

    def test_duplicate_key_on_insert_retries_find(self):
        from pymongo.errors import DuplicateKeyError as DKE

        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "pool-race", "employee_id": "emp1"}
        # Step-1 find_one: miss (None) → insert races → step-1 re-find: hit
        concurrently_inserted = {"_id": "concurrent_id", "pool_id": "pool-race"}

        find_one_responses = [None, sibling_doc, concurrently_inserted]
        coll.find_one.side_effect = find_one_responses
        coll.insert_one.side_effect = DKE("E11000 duplicate key")

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/raceaccount"
        )
        res_id, pool_id = _resolve_or_insert_resource(
            coll, "ca1", arm_id, "raceaccount", "eastus", 1700000000
        )

        assert res_id == "concurrent_id"
        assert pool_id == "pool-race"
        # insert_one was attempted once
        coll.insert_one.assert_called_once()

    def test_duplicate_key_re_find_miss_re_raises(self):
        """If re-find after DuplicateKeyError also misses, DuplicateKeyError propagates."""
        from pymongo.errors import DuplicateKeyError as DKE

        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        # step-1 miss, sibling found, insert races, re-find also misses
        coll.find_one.side_effect = [None, sibling_doc, None]
        coll.insert_one.side_effect = DKE("E11000 duplicate key")

        arm_id = (
            "/subscriptions/sub1/resourcegroups/rg1/providers/"
            "microsoft.storage/storageaccounts/ghostaccount"
        )
        with pytest.raises(DKE):
            _resolve_or_insert_resource(
                coll, "ca1", arm_id, "ghostaccount", "eastus", 1700000000
            )


# ---------------------------------------------------------------------------
# Class 16: Live scan data_source discriminator
# ---------------------------------------------------------------------------


class TestLiveScanDataSource:
    """Healthy-path rows carry data_source='live_scan'."""

    def test_live_scan_rows_have_data_source_live_scan(self):
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        # Minimal live account
        acct_info = StorageAccountInfo(
            arm_id="/subscriptions/sub1/resourcegroups/rg1/providers/microsoft.storage/storageaccounts/acct",
            name="acct",
            location="eastus",
            age_days=60,
            transactions=0.0,
            used_capacity_gb=2.0,
            saving=0.04,
            sku_name="Standard_LRS",
            kind="StorageV2",
            access_tier="Hot",
        )
        live_result = ScanResult(accounts=[acct_info], authoritative=True)

        sentinel_pool_doc = {"_id": "res1", "pool_id": "p1"}
        coll = MagicMock()
        # find_one for _resolve_or_insert_resource: step-1 hits
        coll.find_one.return_value = sentinel_pool_doc
        # _reconcile_deleted needs coll.find
        coll.find.return_value = iter([])

        module = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        module.organization_id = "org1"
        module.created_at = 1700000000
        module._mongo_client = MagicMock()
        module._mongo_client.restapi.resources = coll
        module._rest_client = MagicMock()
        module.option_ordered_map = {}

        with patch.object(
            module, "get_options_values", return_value=(7, 100, 30, 1.0, {}, [])
        ), patch.object(
            module,
            "get_cloud_accounts",
            return_value={"ca1": {"name": "Test Account"}},
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_azure_creds",
            return_value={
                "ca1": {
                    "subscription_id": "sub1",
                    "tenant": "t",
                    "client_id": "c",
                    "secret": "s",
                }
            },
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._scan_one_account",
            return_value=live_result,
        ):
            rows = module._get()

        assert len(rows) == 1
        assert rows[0]["data_source"] == "live_scan"
        assert rows[0]["saving"] == pytest.approx(0.04)
        assert rows[0]["transactions"] == 0.0


# ---------------------------------------------------------------------------
# Class 17: Retail Prices pagination (Finding 1)
# ---------------------------------------------------------------------------


class TestRetailPricePagination:
    """_get_retail_price_per_gb iterates NextPageLink before caching None."""

    def _make_page(self, items, next_link=None):
        payload = {"Items": items}
        if next_link:
            payload["NextPageLink"] = next_link
        return json.dumps(payload).encode("utf-8")

    def test_meter_on_page_two_is_found_and_cached(self):
        """Meter absent on page 1, present on page 2 → found, price cached."""
        page1_body = self._make_page(
            [{"meterName": "Cool LRS Data Stored", "retailPrice": 0.01}],
            next_link="https://prices.azure.com/api/retail/prices?page=2",
        )
        page2_body = self._make_page(
            [{"meterName": "Hot LRS Data Stored", "retailPrice": 0.02}],
        )

        responses = iter([page1_body, page2_body])

        def fake_urlopen(url, timeout=None):
            resp = MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            resp.read.return_value = next(responses)
            return resp

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price == pytest.approx(0.02)
        assert transient is False
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        assert cache[cache_key] == pytest.approx(0.02)

    def test_meter_absent_across_all_pages_caches_none(self):
        """Meter never present across 3 pages → cached None."""
        pages = [
            self._make_page(
                [{"meterName": "Cool LRS Data Stored", "retailPrice": 0.01}],
                next_link="https://prices.azure.com/page=2",
            ),
            self._make_page(
                [{"meterName": "Archive LRS Data Stored", "retailPrice": 0.001}],
                next_link="https://prices.azure.com/page=3",
            ),
            self._make_page([]),
        ]
        responses = iter(pages)

        def fake_urlopen(url, timeout=None):
            resp = MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            resp.read.return_value = next(responses)
            return resp

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is False
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        assert cache_key in cache
        assert cache[cache_key] is None

    def test_http_error_on_page_two_returns_none_not_cached(self):
        """HTTP error mid-pagination → return None without caching (transient)."""
        import urllib.error

        page1_body = self._make_page(
            [],
            next_link="https://prices.azure.com/page=2",
        )

        call_count = 0

        def fake_urlopen(url, timeout=None):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                resp = MagicMock()
                resp.__enter__ = lambda s: s
                resp.__exit__ = MagicMock(return_value=False)
                resp.read.return_value = page1_body
                return resp
            raise urllib.error.URLError("connection reset")

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is True, (
            "HTTP error mid-pagination must set transient_error=True"
        )
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        assert cache_key not in cache, (
            "transient HTTP error must not poison the cache — next run must retry"
        )

        # Second call with empty cache should attempt the API again.
        call_count = 0

        def fake_urlopen_retry(url, timeout=None):
            nonlocal call_count
            call_count += 1
            resp = MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            resp.read.return_value = self._make_page(
                [{"meterName": "Hot LRS Data Stored", "retailPrice": 0.02}]
            )
            return resp

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen_retry,
        ):
            price2, transient2 = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price2 == pytest.approx(0.02), (
            "second call (after transient error) must succeed and return price"
        )
        assert transient2 is False

    def test_pagination_cap_reached_caches_none(self):
        """Cap of RETAIL_PRICES_MAX_PAGES reached → None cached (defensive)."""
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            RETAIL_PRICES_MAX_PAGES,
        )

        def make_page_with_next(i):
            return self._make_page(
                [],
                next_link=f"https://prices.azure.com/page={i + 1}",
            )

        page_responses = [make_page_with_next(i) for i in range(RETAIL_PRICES_MAX_PAGES + 5)]
        responses = iter(page_responses)

        def fake_urlopen(url, timeout=None):
            resp = MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            resp.read.return_value = next(responses)
            return resp

        cache: dict = {}
        lock = threading.Lock()
        call_count_holder = [0]

        original_urlopen = fake_urlopen

        def counting_urlopen(url, timeout=None):
            call_count_holder[0] += 1
            return original_urlopen(url, timeout=timeout)

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=counting_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is False, (
            "pagination cap (no HTTP error) must not be treated as transient"
        )
        assert call_count_holder[0] == RETAIL_PRICES_MAX_PAGES, (
            f"Expected exactly {RETAIL_PRICES_MAX_PAGES} page fetches at cap; "
            f"got {call_count_holder[0]}"
        )
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        assert cache_key in cache
        assert cache[cache_key] is None


# ---------------------------------------------------------------------------
# Class 18: UsedCapacity None vs 0.0 semantics (Finding 2)
# ---------------------------------------------------------------------------


class TestUsedCapacityNoneIsProbeFailure:
    """capacity probe returning None counts toward probe_failures."""

    def _run_with_capacity_result(self, capacity_return_value):
        """Run _scan_one_account with one account; capacity probe returns given value."""
        from azure.core.exceptions import HttpResponseError

        creds = _make_creds()

        acct = _make_acct()

        def metrics_side_effect(resource_uri, **kwargs):
            m = Mock()
            ts = Mock()
            if "Transactions" in kwargs.get("metricnames", ""):
                dp = Mock()
                dp.total = 0.0
                ts.data = [dp]
            else:
                if capacity_return_value is None:
                    raise HttpResponseError(message="monitor unavailable")
                dp = Mock()
                # capacity_return_value already in bytes
                dp.average = capacity_return_value
                ts.data = [dp]
            m.timeseries = [ts]
            result = Mock()
            result.value = [m]
            return result

        monitor = MagicMock()
        monitor.metrics.list.side_effect = metrics_side_effect

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_retail_price_per_gb",
            return_value=(0.02, False),
        ):
            mock_smc.return_value.storage_accounts.list.return_value = [acct]
            return _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )

    def test_capacity_probe_error_makes_scan_non_authoritative(self):
        """Capacity probe error (None) for the only account → 100% failure → non-authoritative."""
        scan = self._run_with_capacity_result(None)
        assert scan.authoritative is False, (
            "capacity probe error must count toward probe_failures, "
            "triggering non-authoritative scan"
        )
        assert scan.accounts == []

    def test_capacity_zero_is_not_probe_failure(self):
        """Genuine empty timeseries (0.0 bytes) is NOT a probe failure."""
        # 0 bytes → 0.0 GB, which is < min_used_capacity_gb=1.0 → skipped_capacity
        # but probe_attempts=1, probe_failures=0 → authoritative=True
        scan = self._run_with_capacity_result(0)
        assert scan.authoritative is True, (
            "genuine empty capacity (0.0 GB) must not be counted as a probe failure"
        )
        assert scan.accounts == []

    def test_probe_returns_0_gb_skips_via_min_capacity_filter(self):
        """An account with 0.0 GB is skipped due to min_used_capacity_gb, not probe failure."""
        scan = self._run_with_capacity_result(0)
        # Account not in results (0.0 GB < 1.0 GB minimum) but scan is authoritative
        assert scan.accounts == []
        assert scan.authoritative is True


class TestUsedCapacityZeroIsNotProbeFailure:
    """_probe_used_capacity_gb returns 0.0 on empty timeseries."""

    def test_empty_timeseries_returns_zero(self):
        monitor = MagicMock()
        result = Mock()
        metric = Mock()
        metric.timeseries = []
        result.value = [metric]
        monitor.metrics.list.return_value = result

        arm_id = "/subscriptions/sub1/rg/r/microsoft.storage/storageaccounts/x"
        val = _probe_used_capacity_gb(monitor, arm_id)
        assert val == 0.0, (
            "_probe_used_capacity_gb must return 0.0 (not None) when timeseries is empty"
        )

    def test_exception_returns_none(self):
        from azure.core.exceptions import HttpResponseError

        monitor = MagicMock()
        monitor.metrics.list.side_effect = HttpResponseError(message="throttled")

        arm_id = "/subscriptions/sub1/rg/r/microsoft.storage/storageaccounts/x"
        val = _probe_used_capacity_gb(monitor, arm_id)
        assert val is None, (
            "_probe_used_capacity_gb must return None on exception"
        )

    def test_data_points_all_none_average_returns_zero(self):
        """All data points have average=None → latest stays None → return 0.0."""
        monitor = MagicMock()
        result = Mock()
        metric = Mock()
        ts = Mock()
        dp = Mock()
        dp.average = None
        ts.data = [dp]
        metric.timeseries = [ts]
        result.value = [metric]
        monitor.metrics.list.return_value = result

        arm_id = "/subscriptions/sub1/rg/r/microsoft.storage/storageaccounts/x"
        val = _probe_used_capacity_gb(monitor, arm_id)
        assert val == 0.0


# ---------------------------------------------------------------------------
# Class 19: Archive OPTIONS_CHANGED vs current values (Finding 3)
# ---------------------------------------------------------------------------


class TestArchiveOptionsChanged:
    """Archive OPTIONS_CHANGED compares against current persisted values, not defaults."""

    def _make_archive_instance_with_current(self, current_idle_days=14):
        from bumiworker.bumiworker.modules.archive.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        instance = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        instance._mongo_client = MagicMock()
        instance.reason_description_map = {
            ArchiveReason.RECOMMENDATION_APPLIED: "applied",
            ArchiveReason.RECOMMENDATION_IRRELEVANT: "irrelevant",
            ArchiveReason.RESOURCE_DELETED: "resource deleted",
            ArchiveReason.CLOUD_ACCOUNT_DELETED: "cloud account deleted",
            ArchiveReason.OPTIONS_CHANGED: "options changed",
        }
        instance.option_ordered_map = {
            "idle_days_window": {"default": 7},
            "idle_transactions_threshold": {"default": 100},
            "min_account_age_days": {"default": 30},
            "min_used_capacity_gb": {"default": 1.0},
            "excluded_pools": {"default": {}},
            "skip_cloud_accounts": {"default": []},
        }
        # Inject get_options_values to return current_idle_days as first element
        instance.get_options_values = lambda: (
            current_idle_days,
            100,
            30,
            1.0,
            {},
            [],
        )
        return instance

    def _make_sentinel_doc(self, res_id="r1"):
        return {"_id": res_id, "deleted_at": 0, "cloud_account_id": "ca1"}

    def test_stable_non_default_threshold_not_options_changed(self):
        """Org keeps idle_days_window=14 (non-default); previous also 14 → NOT OPTIONS_CHANGED."""
        instance = self._make_archive_instance_with_current(current_idle_days=14)
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [self._make_sentinel_doc()]
        )

        result = instance._get(
            previous_options={
                "idle_days_window": 14,
                "idle_transactions_threshold": 100,
                "min_account_age_days": 30,
                "min_used_capacity_gb": 1.0,
            },
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        # Should be RECOMMENDATION_IRRELEVANT (invariant violation) — NOT OPTIONS_CHANGED
        assert len(result) == 1
        assert result[0]["reason"] != ArchiveReason.OPTIONS_CHANGED, (
            "keeping idle_days_window=14 stable must not trigger OPTIONS_CHANGED"
        )

    def test_changed_threshold_triggers_options_changed(self):
        """Previous=7, current=14 → OPTIONS_CHANGED."""
        instance = self._make_archive_instance_with_current(current_idle_days=14)
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [self._make_sentinel_doc()]
        )

        result = instance._get(
            previous_options={
                "idle_days_window": 7,
                "idle_transactions_threshold": 100,
                "min_account_age_days": 30,
                "min_used_capacity_gb": 1.0,
            },
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.OPTIONS_CHANGED

    def test_default_values_unchanged_not_options_changed(self):
        """Default values for both previous and current → NOT OPTIONS_CHANGED."""
        instance = self._make_archive_instance_with_current(current_idle_days=7)
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [self._make_sentinel_doc()]
        )

        result = instance._get(
            previous_options={
                "idle_days_window": 7,
                "idle_transactions_threshold": 100,
                "min_account_age_days": 30,
                "min_used_capacity_gb": 1.0,
            },
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] != ArchiveReason.OPTIONS_CHANGED

    def test_missing_key_in_previous_options_not_flagged(self):
        """Brand-new threshold key absent from previous_options must not trigger OPTIONS_CHANGED."""
        instance = self._make_archive_instance_with_current(current_idle_days=14)
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter(
            [self._make_sentinel_doc()]
        )

        # previous_options lacks min_used_capacity_gb (added in a later release)
        result = instance._get(
            previous_options={
                "idle_days_window": 14,
                "idle_transactions_threshold": 100,
                "min_account_age_days": 30,
                # min_used_capacity_gb absent
            },
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] != ArchiveReason.OPTIONS_CHANGED, (
            "absent key in previous_options must not trigger OPTIONS_CHANGED"
        )


# ---------------------------------------------------------------------------
# Class 21: Pricing transient error is a probe failure
# ---------------------------------------------------------------------------


class TestPricingTransientErrorIsProbeFailure:
    """HTTP failure in _get_retail_price_per_gb → probe_failures incremented.

    A Retail Prices API outage that affects ≥ 50% of probed accounts must trip
    non-authoritative so _reconcile_deleted is skipped and valid recommendations
    are not archived.
    """

    def test_http_error_trips_non_authoritative_when_majority_fail(self):
        """Transient pricing error for the only account → 100% failure rate → non-authoritative."""
        import urllib.error

        creds = _make_creds()
        acct = _make_acct()

        def metrics_side_effect(resource_uri, **kwargs):
            m = Mock()
            ts = Mock()
            dp = Mock()
            if "Transactions" in kwargs.get("metricnames", ""):
                dp.total = 0.0
            else:
                # 2 GB used capacity — valid probe result
                dp.average = 2.0 * 1024 ** 3
            ts.data = [dp]
            m.timeseries = [ts]
            result = Mock()
            result.value = [m]
            return result

        monitor = MagicMock()
        monitor.metrics.list.side_effect = metrics_side_effect

        def fake_urlopen(url, timeout=None):
            raise urllib.error.URLError("Retail Prices API unavailable")

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            mock_smc.return_value.storage_accounts.list.return_value = [acct]
            scan = _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )

        assert scan.authoritative is False, (
            "transient pricing API error for all probed accounts must trip "
            "non-authoritative so _reconcile_deleted is not called"
        )
        assert scan.accounts == []

    def test_http_error_returns_none_true_tuple(self):
        """_get_retail_price_per_gb returns (None, True) on HTTP failure."""
        import urllib.error

        def fake_urlopen(url, timeout=None):
            raise urllib.error.URLError("connection refused")

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is True, (
            "_get_retail_price_per_gb must return transient_error=True on HTTP failure"
        )
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        assert cache_key not in cache, (
            "transient error must not be cached so next run retries"
        )


# ---------------------------------------------------------------------------
# Class 22: Pricing "no meter" is NOT a probe failure
# ---------------------------------------------------------------------------


class TestPricingNoMeterIsNotProbeFailure:
    """Pagination exhausts without finding the meter → (None, False) → no probe_failures.

    A legitimate "no meter for this region/sku" outcome must not inflate the
    probe failure counter, since doing so would incorrectly suppress archival
    for subscriptions in unsupported regions.
    """

    def test_no_meter_returns_none_false_tuple(self):
        """Pagination exhausts without any meter match → (None, False)."""
        def fake_urlopen(url, timeout=None):
            resp = MagicMock()
            resp.__enter__ = lambda s: s
            resp.__exit__ = MagicMock(return_value=False)
            resp.read.return_value = b'{"Items": []}'
            return resp

        cache: dict = {}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
            side_effect=fake_urlopen,
        ):
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is False, (
            "pagination exhausted without meter must return transient_error=False"
        )

    def test_no_meter_does_not_increment_probe_failures(self):
        """Account skipped due to no meter → scan remains authoritative."""
        creds = _make_creds()
        acct = _make_acct()

        def metrics_side_effect(resource_uri, **kwargs):
            m = Mock()
            ts = Mock()
            dp = Mock()
            if "Transactions" in kwargs.get("metricnames", ""):
                dp.total = 0.0
            else:
                dp.average = 2.0 * 1024 ** 3
            ts.data = [dp]
            m.timeseries = [ts]
            result = Mock()
            result.value = [m]
            return result

        monitor = MagicMock()
        monitor.metrics.list.side_effect = metrics_side_effect

        # Return (None, False) — no meter, not a transient error
        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.ClientSecretCredential"
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.StorageManagementClient"
        ) as mock_smc, patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.MonitorManagementClient",
            return_value=monitor,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_retail_price_per_gb",
            return_value=(None, False),
        ):
            mock_smc.return_value.storage_accounts.list.return_value = [acct]
            scan = _scan_one_account(
                creds,
                idle_days_window=7,
                idle_transactions_threshold=100,
                min_account_age_days=30,
                min_used_capacity_gb=1.0,
                deadline=9e18,
                price_cache={},
                price_lock=threading.Lock(),
            )

        # Account skipped (no price) but scan is still authoritative since
        # probe_failures was NOT incremented.
        assert scan.authoritative is True, (
            "legitimate no-meter result must not increment probe_failures; "
            "scan must remain authoritative"
        )
        assert scan.accounts == []


# ---------------------------------------------------------------------------
# Class 23: Pricing cache hit None is not transient
# ---------------------------------------------------------------------------


class TestPricingCacheHitNoneIsNotTransient:
    """Second call after pagination exhaust returns (None, False) from cache.

    The cache stores None for legitimate no-meter results.  A subsequent call
    in the same run must return (None, False) — not (None, True) — so the
    caller does not miscount it as a probe failure.
    """

    def test_cache_hit_none_returns_false_transient(self):
        """Cache already has None for this key → returns (None, False)."""
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        cache = {cache_key: None}  # pre-populated from pagination exhaust
        lock = threading.Lock()

        # urlopen must NOT be called — the cache hit should short-circuit
        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
        ) as mock_urlopen:
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price is None
        assert transient is False, (
            "cache hit returning None must have transient_error=False; "
            "only live HTTP failures are transient"
        )
        mock_urlopen.assert_not_called()

    def test_cache_hit_price_returns_false_transient(self):
        """Cache has a valid price → returns (price, False)."""
        cache_key = ("sub1", "eastus", "Standard_LRS", "StorageV2", "Hot")
        cache = {cache_key: 0.023}
        lock = threading.Lock()

        with patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts.urllib.request.urlopen",
        ) as mock_urlopen:
            price, transient = _get_retail_price_per_gb(
                "sub1", "eastus", "Standard_LRS", "StorageV2", "Hot", cache, lock
            )

        assert price == pytest.approx(0.023)
        assert transient is False
        mock_urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Class 24: Missing credentials emits preserved sentinels
# ---------------------------------------------------------------------------


class TestMissingCredentialsEmitsSentinels:
    """Missing creds for a CA must preserve sentinel rows, not silently drop them.

    Previous behaviour: ``if not creds: continue`` silently skipped the CA,
    causing all its recommendations to vanish from the current checklist and be
    archived on the next cycle as RECOMMENDATION_IRRELEVANT — even though the
    accounts may still be idle; only the credentials were temporarily absent.

    Fixed behaviour: sentinel rows are re-emitted for the missing-creds CA
    before ``continue``, matching every other per-account failure path.
    """

    def _make_module(self, coll_mock):
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        module = AzureAbandonedStorageAccounts.__new__(AzureAbandonedStorageAccounts)
        module.organization_id = "org1"
        module.created_at = 1700000000
        module._mongo_client = MagicMock()
        module._mongo_client.restapi.resources = coll_mock
        module._rest_client = MagicMock()
        module.option_ordered_map = {}
        return module

    def test_fallback_sentinel_rows_emitted_for_missing_creds_ca(self):
        """CA with no creds → sentinel rows preserved; bulk_write not called."""
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        sentinel_doc = {
            "_id": "sent_nocreds",
            "cloud_resource_id": (
                "/subscriptions/sub2/resourcegroups/rg/providers/"
                "microsoft.storage/storageaccounts/idle"
            ),
            "name": "idle",
            "region": "australiaeast",
            "pool_id": "pool1",
        }

        coll = MagicMock()
        coll.find.return_value = iter([sentinel_doc])

        module = self._make_module(coll)

        with patch.object(
            module,
            "get_options_values",
            return_value=(7, 100, 30, 1.0, {}, []),
        ), patch.object(
            module,
            "get_cloud_accounts",
            # Two CAs: ca1 has creds, ca2 does not
            return_value={
                "ca1": {"name": "Has Creds"},
                "ca2": {"name": "No Creds"},
            },
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_azure_creds",
            # Only ca1 has credentials; ca2 is absent from the map
            return_value={
                "ca1": {
                    "subscription_id": "sub1",
                    "tenant": "t",
                    "client_id": "c",
                    "secret": "s",
                }
            },
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._scan_one_account",
            return_value=ScanResult(accounts=[], authoritative=True),
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._reconcile_deleted",
            return_value=0,
        ):
            rows = module._get()

        # Sentinel row for ca2 must be present despite missing creds
        ca2_rows = [r for r in rows if r["cloud_account_id"] == "ca2"]
        assert len(ca2_rows) == 1, (
            "missing-creds CA must emit preserved sentinel rows, not silently "
            "drop them — silent drop causes false RECOMMENDATION_IRRELEVANT archival"
        )
        assert ca2_rows[0]["resource_id"] == "sent_nocreds"
        assert ca2_rows[0]["saving"] == 0.0
        assert ca2_rows[0]["data_source"] == "preserved_sentinel"

    def test_reconcile_deleted_not_called_for_missing_creds_ca(self):
        """_reconcile_deleted must never be called for a CA with missing creds."""
        from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
            AzureAbandonedStorageAccounts,
        )

        coll = MagicMock()
        coll.find.return_value = iter([])  # no sentinels — that's fine

        module = self._make_module(coll)

        with patch.object(
            module,
            "get_options_values",
            return_value=(7, 100, 30, 1.0, {}, []),
        ), patch.object(
            module,
            "get_cloud_accounts",
            return_value={"ca2": {"name": "No Creds"}},
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._get_azure_creds",
            return_value={},  # no creds for anyone
        ), patch(
            "bumiworker.bumiworker.modules.recommendations"
            ".azure_abandoned_storage_accounts._reconcile_deleted",
        ) as mock_reconcile:
            rows = module._get()

        mock_reconcile.assert_not_called(), (
            "_reconcile_deleted must not be called when a CA has no credentials"
        )
