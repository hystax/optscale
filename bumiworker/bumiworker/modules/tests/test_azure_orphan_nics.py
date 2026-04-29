"""Unit tests for bumiworker azure_orphan_nics recommendation + archive modules.

SDK availability guard: if azure.mgmt.network is absent the entire suite is
skipped gracefully rather than erroring with ImportError.
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

azure_mgmt_network = pytest.importorskip("azure.mgmt.network")
azure_mgmt_network_models = pytest.importorskip("azure.mgmt.network.models")

from azure.mgmt.network.models import NetworkInterface  # noqa: E402

from bumiworker.bumiworker.modules.recommendations.azure_orphan_nics import (  # noqa: E402
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
        assert result[0]["reason"] == ArchiveReason.RECOMMENDATION_IRRELEVANT
