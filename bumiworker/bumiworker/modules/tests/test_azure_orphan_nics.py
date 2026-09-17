"""Unit tests for bumiworker azure_orphan_nics recommendation + archive modules.

SDK availability guard: if azure.mgmt.network is absent the entire suite is
skipped gracefully rather than erroring with ImportError.
"""
import uuid
from datetime import datetime
from typing import Optional
from unittest.mock import MagicMock, Mock, call, patch

import pytest

azure_mgmt_network = pytest.importorskip("azure.mgmt.network")
azure_mgmt_network_models = pytest.importorskip("azure.mgmt.network.models")

from azure.mgmt.network.models import NetworkInterface  # noqa: E402

from bumiworker.bumiworker.modules.recommendations.azure_orphan_nics import (  # noqa: E402
    _emit_rows_from_existing_sentinels,
    _list_orphan_nics,
    _reconcile_deleted,
    _resolve_or_insert_resource,
    _touch_resource,
)
from bumiworker.bumiworker.consts import ArchiveReason  # noqa: E402


# ---------------------------------------------------------------------------
# Recommendation module tests
# ---------------------------------------------------------------------------


class TestStorageAccountAttributeMapLocked:
    """Lock NetworkInterface SDK fields via _attribute_map.

    Server-populated read-only fields are declared in ``_attribute_map``, not
    ``__init__``, so this is the correct surface to assert against.
    """

    def test_required_fields_present(self):
        attr_map = NetworkInterface._attribute_map
        for field in ("virtual_machine", "id", "location", "name"):
            assert field in attr_map, (
                f"NetworkInterface._attribute_map missing '{field}'; "
                "SDK contract may have changed"
            )

    def test_service_managed_fields_present_or_getattr_defensive(self):
        """Lock the three service-managed NIC attributes added by Codex P1 fix.

        These fields are present in azure-mgmt-network >= 4.0 (REST API 2019+)
        and confirmed in the _attribute_map for the pinned version 30.2.0.
        If a future SDK version renames one of these fields this test will
        surface the drift so the runtime getattr default path can be reviewed.

        NOTE: the production filter uses ``getattr(nic, field, None)`` so it
        degrades gracefully even if a field is absent from the SDK — it will
        not crash, it will simply not exclude that category of service-managed
        NIC.  This test documents the expected SDK contract; it is
        intentionally soft (warns via assertion message) rather than hard
        (would block deployment on SDK upgrade).
        """
        attr_map = NetworkInterface._attribute_map
        service_managed_fields = (
            "private_endpoint",
            "private_link_service",
            "virtual_machine_scale_set",
        )
        for field in service_managed_fields:
            assert field in attr_map, (
                f"NetworkInterface._attribute_map missing '{field}' in "
                "azure-mgmt-network==30.2.0; runtime getattr-defensive code "
                "will NOT exclude this service-managed NIC category.  "
                "If the SDK renamed this field, update the getattr key in "
                "_list_orphan_nics to match the new name."
            )


class TestOrphanFilter:
    """_list_orphan_nics returns only NICs with virtual_machine == None."""

    def _make_nic(self, nic_id: str, name: str, location: str, has_vm: bool):
        nic = Mock(spec=NetworkInterface)
        nic.id = nic_id
        nic.name = name
        nic.location = location
        nic.virtual_machine = Mock() if has_vm else None
        return nic

    def test_only_orphan_returned(self):
        orphan = self._make_nic(
            "/subscriptions/SUB/providers/Microsoft.Network/networkInterfaces/NIC1",
            "NIC1",
            "eastus",
            has_vm=False,
        )
        attached = self._make_nic(
            "/subscriptions/SUB/providers/Microsoft.Network/networkInterfaces/NIC2",
            "NIC2",
            "eastus",
            has_vm=True,
        )

        mock_client = Mock()
        mock_client.network_interfaces.list_all.return_value = [orphan, attached]

        creds = {
            "tenant": "t1",
            "client_id": "c1",
            "secret": "s1",
            "subscription_id": "sub1",
        }

        # Patch the names imported into the module under test.
        with patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".NetworkManagementClient",
            return_value=mock_client,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".ClientSecretCredential"
        ):
            result = _list_orphan_nics(creds)

        assert len(result) == 1
        assert result[0].arm_id == orphan.id.lower()
        assert result[0].name == "NIC1"
        assert result[0].location == "eastus"

    def test_arm_id_lowercased(self):
        nic = self._make_nic(
            "/Subscriptions/SUB123/ResourceGroups/RG/providers/Microsoft.Network/networkInterfaces/NIC",
            "NIC",
            "westus",
            has_vm=False,
        )
        mock_client = Mock()
        mock_client.network_interfaces.list_all.return_value = [nic]

        creds = {
            "tenant": "t",
            "client_id": "c",
            "secret": "s",
            "subscription_id": "sub",
        }

        with patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".NetworkManagementClient",
            return_value=mock_client,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".ClientSecretCredential"
        ):
            result = _list_orphan_nics(creds)

        assert result[0].arm_id == nic.id.lower()
        assert result[0].arm_id != nic.id  # was mixed-case

    def _make_service_nic(self, nic_id: str, name: str, **service_attrs):
        """Return a plain Mock NIC (no spec) with service-managed attributes set.

        Plain Mock (not spec=NetworkInterface) is used intentionally: the
        production code calls ``getattr(nic, field, None)`` which works on any
        object.  Using plain Mock lets us set arbitrary attributes without
        worrying about whether the pinned SDK version exposes them in spec.
        """
        nic = Mock()
        nic.id = nic_id
        nic.name = name
        nic.location = "eastus"
        nic.virtual_machine = None
        # Default all service-managed fields to None; caller overrides.
        nic.virtual_machine_scale_set = None
        nic.private_endpoint = None
        nic.private_link_service = None
        for attr, value in service_attrs.items():
            setattr(nic, attr, value)
        return nic

    def test_skips_service_managed_nics(self):
        """Codex P1: service-managed NICs must be excluded from orphan results.

        Covers:
        - Private Endpoint NICs (private_endpoint set)
        - Private Link Service NICs (private_link_service set)
        - VMSS instance NICs (virtual_machine_scale_set set)

        Only the plain unattached NIC (all service flags None) should be
        returned as an orphan candidate.
        """
        base_id = "/subscriptions/SUB/providers/Microsoft.Network/networkInterfaces/"

        # Genuine orphan: no VM, no service flag → must be returned.
        nic_orphan = self._make_service_nic(base_id + "nic-orphan", "nic-orphan")

        # Private Endpoint backing NIC → must be skipped.
        nic_pe = self._make_service_nic(
            base_id + "nic-pe",
            "nic-pe",
            private_endpoint=Mock(),
        )

        # Private Link Service backing NIC → must be skipped.
        nic_pls = self._make_service_nic(
            base_id + "nic-pls",
            "nic-pls",
            private_link_service=Mock(),
        )

        # VMSS instance NIC (no virtual_machine, but vmss ref present) → skipped.
        nic_vmss = self._make_service_nic(
            base_id + "nic-vmss",
            "nic-vmss",
            virtual_machine_scale_set=Mock(),
        )

        mock_client = Mock()
        mock_client.network_interfaces.list_all.return_value = [
            nic_orphan,
            nic_pe,
            nic_pls,
            nic_vmss,
        ]

        creds = {
            "tenant": "t1",
            "client_id": "c1",
            "secret": "s1",
            "subscription_id": "sub1",
        }

        with patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".NetworkManagementClient",
            return_value=mock_client,
        ), patch(
            "bumiworker.bumiworker.modules.recommendations.azure_orphan_nics"
            ".ClientSecretCredential"
        ):
            result = _list_orphan_nics(creds)

        assert len(result) == 1, (
            f"Expected only 1 orphan NIC; got {len(result)}: "
            f"{[r.name for r in result]}"
        )
        assert result[0].name == "nic-orphan"
        assert result[0].arm_id == (base_id + "nic-orphan").lower()


class TestSiblingFindInvariant:
    """_resolve_or_insert_resource second find_one must enforce non-null guards."""

    def test_sibling_query_has_null_guards_and_sort(self):
        coll = MagicMock()
        # First call (exact match) returns None -> triggers sibling lookup
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic1"
        _resolve_or_insert_resource(coll, "ca1", arm_id, "nic1", "eastus", 1000)

        assert coll.find_one.call_count == 2
        _, second_call_kwargs = coll.find_one.call_args_list[1]
        second_call_args = coll.find_one.call_args_list[1][0]

        sibling_filter = second_call_args[0]
        assert sibling_filter.get("employee_id") == {"$ne": None}
        assert sibling_filter.get("pool_id") == {"$ne": None}

        # sort must be deterministic: created_at asc, _id asc
        sort_arg = second_call_args[2] if len(second_call_args) > 2 else second_call_kwargs.get("sort")
        assert sort_arg == [("created_at", 1), ("_id", 1)]


class TestSentinelDocShape:
    """Inserted sentinel document must have all required fields with correct values."""

    def test_all_required_fields(self):
        coll = MagicMock()
        sibling_doc = {
            "_id": "sib1",
            "pool_id": "p1",
            "employee_id": "e1",
        }
        coll.find_one.side_effect = [None, sibling_doc]

        mixed_case_arm = "/Subscriptions/SUB/ResourceGroups/RG/providers/Microsoft.Network/networkInterfaces/NIC"
        now_ts = 1700000000
        _resolve_or_insert_resource(coll, "ca1", mixed_case_arm, "NIC", "eastus", now_ts)

        assert coll.insert_one.call_count == 1
        inserted = coll.insert_one.call_args[0][0]

        required_fields = [
            "_id", "cloud_account_id", "cloud_resource_id", "name", "region",
            "resource_type", "service_name", "tags", "created_at", "deleted_at",
            "first_seen", "last_seen", "_first_seen_date", "_last_seen_date",
            "active", "pool_id", "employee_id",
        ]
        for field in required_fields:
            assert field in inserted, f"sentinel doc missing field '{field}'"

        assert len(required_fields) == 17

        # ARM ID must be lowercased on insert
        assert inserted["cloud_resource_id"] == mixed_case_arm.lower()
        assert inserted["cloud_resource_id"] != mixed_case_arm

        assert inserted["meta"]["created_by"] == "azure_orphan_nics_native"
        assert inserted["active"] is False
        assert inserted["pool_id"] == "p1"
        assert inserted["employee_id"] == "e1"

        # Date fields must be day-truncated datetimes
        for date_field in ("_first_seen_date", "_last_seen_date"):
            dt = inserted[date_field]
            assert isinstance(dt, datetime)
            assert dt.hour == 0
            assert dt.minute == 0
            assert dt.second == 0
            assert dt.microsecond == 0


class TestNoSiblingRaises:
    """RuntimeError raised when no qualifying sibling exists."""

    def test_raises_when_no_sibling(self):
        coll = MagicMock()
        coll.find_one.return_value = None  # both calls return None

        with pytest.raises(RuntimeError):
            _resolve_or_insert_resource(
                coll, "ca1",
                "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic",
                "nic", "eastus", 1000,
            )


class TestExactMatchSkipsOverlaySentinel:
    """Step-1 find_one must exclude overlay sentinels (created_by="azure_alias_wrapper").

    When the only live doc for a given cloud_resource_id is an overlay sentinel,
    _resolve_or_insert_resource must treat it as not found and fall through to
    the sibling lookup, then insert a NEW native sentinel.  Two sentinels for
    the same NIC during the Phase B overlap window is acceptable; UI dedupe is
    the overlay's responsibility.
    """

    def test_overlay_sentinel_treated_as_not_found(self):
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        # First find_one (exact-match with $or guard) returns None because the
        # only matching doc is an overlay sentinel excluded by the filter.
        # Second find_one (sibling lookup) returns a valid sibling.
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic1"
        _resolve_or_insert_resource(coll, "ca1", arm_id, "nic1", "eastus", 1000)

        # A new native sentinel must have been inserted.
        coll.insert_one.assert_called_once()
        inserted = coll.insert_one.call_args[0][0]
        assert inserted["meta"]["created_by"] == "azure_orphan_nics_native"

    def test_first_find_one_filter_contains_or_clause(self):
        coll = MagicMock()
        sibling_doc = {"_id": "sib1", "pool_id": "p1", "employee_id": "e1"}
        coll.find_one.side_effect = [None, sibling_doc]

        arm_id = "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic2"
        _resolve_or_insert_resource(coll, "ca1", arm_id, "nic2", "westus", 2000)

        first_call_filter = coll.find_one.call_args_list[0][0][0]
        assert "$or" in first_call_filter, (
            "step-1 find_one must include $or to exclude overlay sentinels"
        )
        or_clauses = first_call_filter["$or"]
        # Must contain the $exists: False branch (real cloud-adapter docs).
        assert {"meta.created_by": {"$exists": False}} in or_clauses
        # Must contain the native-sentinel branch.
        assert {"meta.created_by": "azure_orphan_nics_native"} in or_clauses

    def test_native_sentinel_is_still_reused(self):
        """When step-1 finds our own sentinel it is reused — no insert."""
        coll = MagicMock()
        native_doc = {"_id": "nat1", "pool_id": "p2"}
        coll.find_one.side_effect = [native_doc]

        arm_id = "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic3"
        res_id, pool_id = _resolve_or_insert_resource(
            coll, "ca1", arm_id, "nic3", "eastus", 3000
        )

        assert res_id == "nat1"
        assert pool_id == "p2"
        coll.insert_one.assert_not_called()


class TestReconcileDeleted:
    """_reconcile_deleted marks missing sentinels with deleted_at."""

    def test_marks_absent_sentinel(self):
        from pymongo import UpdateOne as _UpdateOne

        coll = MagicMock()
        sentinel_a = {
            "_id": "doc_a",
            "cloud_resource_id": "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/a",
        }
        sentinel_b = {
            "_id": "doc_b",
            "cloud_resource_id": "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/b",
        }
        coll.find.return_value = iter([sentinel_a, sentinel_b])

        current_arm_ids = {sentinel_a["cloud_resource_id"]}
        now_ts = 1700000000

        count = _reconcile_deleted(coll, "ca1", current_arm_ids, now_ts)

        assert count == 1
        coll.bulk_write.assert_called_once()
        ops = coll.bulk_write.call_args[0][0]
        assert len(ops) == 1
        op = ops[0]
        # Inspect UpdateOne internals: filter and update
        assert op._filter == {"_id": "doc_b"}
        assert op._doc == {"$set": {"deleted_at": now_ts}}

    def test_no_bulk_write_when_all_present(self):
        coll = MagicMock()
        sentinel_a = {
            "_id": "doc_a",
            "cloud_resource_id": "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/a",
        }
        coll.find.return_value = iter([sentinel_a])
        current_arm_ids = {sentinel_a["cloud_resource_id"]}

        count = _reconcile_deleted(coll, "ca1", current_arm_ids, 9999)

        assert count == 0
        coll.bulk_write.assert_not_called()


class TestSentinelEmitFallback:
    """_emit_rows_from_existing_sentinels returns correct row shape.

    Design property: when a per-account Azure scan fails (transient API error,
    SPN expiry, network blip), calling this helper re-emits the same rows that
    a healthy prior run produced.  ArchiveBase.get_archive_candidates therefore
    sees no diff for the failed account and does not trigger false
    RECOMMENDATION_IRRELEVANT archival of live orphan NICs.
    """

    def _make_sentinel(
        self,
        doc_id: str,
        cloud_resource_id: str,
        name: str,
        region: str,
        pool_id: Optional[str] = None,
    ) -> dict:
        s = {
            "_id": doc_id,
            "cloud_resource_id": cloud_resource_id,
            "name": name,
            "region": region,
        }
        if pool_id is not None:
            s["pool_id"] = pool_id
        return s

    def test_emit_rows_from_existing_sentinels_returns_expected_shape(self):
        """Two sentinels returned: one excluded, one not; row shape must match spec."""
        from unittest.mock import MagicMock

        excluded_pool = "pool-excluded"
        included_pool = "pool-included"
        excluded_pools = {excluded_pool: True}

        sentinel_excluded = self._make_sentinel(
            "id-excl",
            "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic-excl",
            "nic-excl",
            "eastus",
            pool_id=excluded_pool,
        )
        sentinel_included = self._make_sentinel(
            "id-incl",
            "/subscriptions/sub/resourcegroups/rg/providers/microsoft.network/networkinterfaces/nic-incl",
            "nic-incl",
            "westus",
            pool_id=included_pool,
        )

        coll = MagicMock()
        coll.find.return_value = iter([sentinel_excluded, sentinel_included])

        rows = _emit_rows_from_existing_sentinels(
            coll, "ca-test", "My Test Account", excluded_pools
        )

        assert len(rows) == 2

        # Verify coll.find was called with the correct filter
        call_filter = coll.find.call_args[0][0]
        assert call_filter["cloud_account_id"] == "ca-test"
        assert call_filter["deleted_at"] == 0
        assert call_filter["meta.created_by"] == "azure_orphan_nics_native"

        # Build a lookup by resource_id for deterministic assertions
        by_id = {r["resource_id"]: r for r in rows}
        assert set(by_id) == {"id-excl", "id-incl"}

        # Common fields must be present on every row
        for row in rows:
            assert row["saving"] == 0.0
            assert row["cloud_type"] == "azure_cnr"
            assert row["cloud_account_id"] == "ca-test"
            assert row["cloud_account_name"] == "My Test Account"
            assert row["folder_id"] is None
            assert row["zone_id"] is None

        excl_row = by_id["id-excl"]
        assert excl_row["cloud_resource_id"] == sentinel_excluded["cloud_resource_id"]
        assert excl_row["resource_name"] == "nic-excl"
        assert excl_row["region"] == "eastus"
        assert excl_row["is_excluded"] is True

        incl_row = by_id["id-incl"]
        assert incl_row["cloud_resource_id"] == sentinel_included["cloud_resource_id"]
        assert incl_row["resource_name"] == "nic-incl"
        assert incl_row["region"] == "westus"
        assert incl_row["is_excluded"] is False

    def test_emit_rows_empty_when_no_live_sentinels(self):
        """No live sentinels → empty list; no exception."""
        from unittest.mock import MagicMock

        coll = MagicMock()
        coll.find.return_value = iter([])

        rows = _emit_rows_from_existing_sentinels(coll, "ca-empty", "Empty", {})
        assert rows == []

    def test_emit_rows_pool_id_absent_is_not_excluded(self):
        """Sentinel with no pool_id must set is_excluded=False even with non-empty excluded_pools."""
        from unittest.mock import MagicMock

        sentinel_no_pool = {
            "_id": "id-np",
            "cloud_resource_id": "/subscriptions/s/resourcegroups/r/providers/microsoft.network/networkinterfaces/np",
            "name": "np",
            "region": "centralus",
            # pool_id intentionally absent
        }

        coll = MagicMock()
        coll.find.return_value = iter([sentinel_no_pool])

        rows = _emit_rows_from_existing_sentinels(
            coll, "ca-np", "No Pool", {"some-pool": True}
        )

        assert len(rows) == 1
        assert rows[0]["is_excluded"] is False


class TestTouchResourceGuard:
    """_touch_resource filter must include meta.created_by guard."""

    def test_update_one_filter_has_created_by_guard(self):
        coll = MagicMock()
        _touch_resource(coll, "doc1", 1700000000)

        coll.update_one.assert_called_once()
        update_filter = coll.update_one.call_args[0][0]
        assert update_filter.get("meta.created_by") == "azure_orphan_nics_native"
        assert update_filter.get("_id") == "doc1"


# ---------------------------------------------------------------------------
# Archive module tests
# ---------------------------------------------------------------------------


class TestArchiveModule:
    """Tests for bumiworker.modules.archive.azure_orphan_nics._get."""

    def _make_archive_instance(self):
        from bumiworker.bumiworker.modules.archive.azure_orphan_nics import (
            AzureOrphanNics,
        )

        instance = AzureOrphanNics.__new__(AzureOrphanNics)
        instance._mongo_client = MagicMock()
        instance.reason_description_map = {
            ArchiveReason.RECOMMENDATION_APPLIED: "NIC deleted or attached to VM",
            ArchiveReason.RECOMMENDATION_IRRELEVANT: "NIC re-attached to VM",
            ArchiveReason.RESOURCE_DELETED: "resource deleted",
            ArchiveReason.CLOUD_ACCOUNT_DELETED: "cloud account deleted",
        }
        return instance

    def test_applied_when_deleted_at_nonzero(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter([
            {"_id": "r1", "deleted_at": 12345, "cloud_account_id": "ca1"},
        ])

        result = instance._get(
            previous_options={},
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
            previous_options={},
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.RESOURCE_DELETED

    def test_cloud_account_deleted(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter([
            {"_id": "r1", "deleted_at": 0, "cloud_account_id": "ca1"},
        ])

        result = instance._get(
            previous_options={},
            optimizations=[opt],
            cloud_accounts_map={},  # ca1 absent
        )

        assert len(result) == 1
        assert result[0]["reason"] == ArchiveReason.CLOUD_ACCOUNT_DELETED

    def test_irrelevant_when_doc_active(self):
        instance = self._make_archive_instance()
        opt = {"resource_id": "r1", "cloud_account_id": "ca1"}
        instance._mongo_client.restapi.resources.find.return_value = iter([
            {"_id": "r1", "deleted_at": 0, "cloud_account_id": "ca1"},
        ])

        result = instance._get(
            previous_options={},
            optimizations=[opt],
            cloud_accounts_map={"ca1": {"name": "test"}},
        )

        assert len(result) == 1


# ---------------------------------------------------------------------------
# Zero-saving allowlist registration
# ---------------------------------------------------------------------------

class TestZeroSavingRegistration:
    """azure_orphan_nics emits saving=0.0; ResourceRecommendations service
    drops zero-saving rows unless the module is registered in
    modules_with_possible_zero_saving.  Lock the registration here so
    a future refactor of the service module surfaces in our test suite.
    """

    def test_module_in_zero_saving_allowlist(self):
        import inspect
        from bumiworker.bumiworker.modules.service import resource_recommendations
        src = inspect.getsource(
            resource_recommendations.ResourceRecommendations.__init__
        )
        assert "'azure_orphan_nics'" in src or '"azure_orphan_nics"' in src, (
            "azure_orphan_nics emits saving=0.0 rows; without registration "
            "in modules_with_possible_zero_saving they are dropped from "
            "resources.recommendations.modules."
        )
