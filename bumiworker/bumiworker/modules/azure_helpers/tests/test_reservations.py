"""Unit tests for the reservation rate helper, focused on the two
correctness fixes flagged by Codex on PR #1:

  1. Cache must be keyed by subscription_id (cross-sub poisoning).
  2. applied_scope must be honoured (Single-scope reservation must not
     discount sibling subscriptions; ManagementGroup-scope conservatively
     skipped).
"""
import sys
import types
from unittest import mock

import pytest

from bumiworker.bumiworker.modules.azure_helpers import reservations
from bumiworker.bumiworker.modules.azure_helpers.reservations import (
    get_effective_storage_rate,
)


# ---- helpers ----------------------------------------------------------

class _Sku:
    def __init__(self, name):
        self.name = name


class _Props:
    def __init__(self, term="1 Year", applied_scope_type=None,
                 applied_scopes=None):
        self.term = term
        self.applied_scope_type = applied_scope_type
        self.applied_scopes = applied_scopes or []


class _Reservation:
    def __init__(self, sku_name, applied_scope_type=None,
                 applied_scopes=None, term="1 Year"):
        self.sku = _Sku(sku_name)
        self.properties = _Props(term=term,
                                 applied_scope_type=applied_scope_type,
                                 applied_scopes=applied_scopes)


def _install_fake_azure_sdk():
    """Inject lightweight stubs for azure.mgmt.reservations and
    azure.core.exceptions so the helper's lazy imports succeed without
    real Azure deps. Returns the AzureReservationAPI mock the test can
    program."""
    api_mock = mock.MagicMock(name="AzureReservationAPI")

    mgmt_mod = types.ModuleType("azure.mgmt.reservations")
    mgmt_mod.AzureReservationAPI = api_mock

    # azure.core.exceptions.HttpResponseError — provide a real class so
    # `raise` works in tests that need it.
    core_exc_mod = types.ModuleType("azure.core.exceptions")

    class HttpResponseError(Exception):
        pass

    core_exc_mod.HttpResponseError = HttpResponseError

    # Parent packages must exist for `from azure.mgmt.reservations ...`
    # style imports to resolve.
    azure_pkg = sys.modules.get("azure") or types.ModuleType("azure")
    azure_mgmt_pkg = sys.modules.get("azure.mgmt") or types.ModuleType("azure.mgmt")
    azure_core_pkg = sys.modules.get("azure.core") or types.ModuleType("azure.core")

    sys.modules["azure"] = azure_pkg
    sys.modules["azure.mgmt"] = azure_mgmt_pkg
    sys.modules["azure.mgmt.reservations"] = mgmt_mod
    sys.modules["azure.core"] = azure_core_pkg
    sys.modules["azure.core.exceptions"] = core_exc_mod

    return api_mock, HttpResponseError


@pytest.fixture(autouse=True)
def _clear_cache():
    reservations._CACHE.clear()
    yield
    reservations._CACHE.clear()


@pytest.fixture
def api_mock():
    api, _exc = _install_fake_azure_sdk()
    api.reset_mock()
    return api


@pytest.fixture
def http_error():
    _api, exc = _install_fake_azure_sdk()
    return exc


# ---- BUG 1: cache isolation by subscription_id ------------------------

def test_cache_isolated_by_subscription_id(api_mock):
    """A second call with a different subscription_id must NOT reuse the
    first call's cached entry — list_all must be invoked again."""
    # Return an empty list both times — what we care about is whether the
    # SDK was hit twice.
    api_mock.return_value.reservation.list_all.return_value = iter([])
    # subA
    rate_a = get_effective_storage_rate(
        credential=mock.Mock(), subscription_id="subA",
        region="eastus", redundancy="LRS", tier="Hot")
    # subB — same region/redundancy/tier
    api_mock.return_value.reservation.list_all.return_value = iter([])
    rate_b = get_effective_storage_rate(
        credential=mock.Mock(), subscription_id="subB",
        region="eastus", redundancy="LRS", tier="Hot")

    assert rate_a is None
    assert rate_b is None
    assert api_mock.return_value.reservation.list_all.call_count == 2, (
        "expected list_all to be called once per subscription; the cache "
        "key is leaking across subs"
    )


# ---- BUG 2: applied_scope filter --------------------------------------

def test_single_scope_other_subscription_skipped(api_mock):
    res = _Reservation(
        sku_name="Blob_Storage_Reserved_Capacity_LRS_Hot_100TB",
        applied_scope_type="Single",
        applied_scopes=["/subscriptions/subA"],
    )
    api_mock.return_value.reservation.list_all.return_value = iter([res])

    # Even if retail pricing would otherwise resolve a rate, the loop
    # must `continue` past this reservation before reaching the SKU
    # match — so patching _fetch_retail_reservation_rate to a non-None
    # sentinel still yields None.
    with mock.patch.object(reservations,
                           "_fetch_retail_reservation_rate",
                           return_value=0.99):
        rate = get_effective_storage_rate(
            credential=mock.Mock(), subscription_id="subB",
            region="eastus", redundancy="LRS", tier="Hot")
    assert rate is None


def test_single_scope_matching_subscription_accepted(api_mock):
    res = _Reservation(
        sku_name="Blob_Storage_Reserved_Capacity_LRS_Hot_100TB",
        applied_scope_type="Single",
        applied_scopes=["/subscriptions/subA"],
    )
    api_mock.return_value.reservation.list_all.return_value = iter([res])
    with mock.patch.object(reservations,
                           "_fetch_retail_reservation_rate",
                           return_value=0.02):
        rate = get_effective_storage_rate(
            credential=mock.Mock(), subscription_id="subA",
            region="eastus", redundancy="LRS", tier="Hot")
    assert rate == 0.02


def test_shared_scope_accepted(api_mock):
    res = _Reservation(
        sku_name="Blob_Storage_Reserved_Capacity_LRS_Hot_100TB",
        applied_scope_type="Shared",
        applied_scopes=[],
    )
    api_mock.return_value.reservation.list_all.return_value = iter([res])
    with mock.patch.object(reservations,
                           "_fetch_retail_reservation_rate",
                           return_value=0.03):
        rate = get_effective_storage_rate(
            credential=mock.Mock(), subscription_id="subZ",
            region="eastus", redundancy="LRS", tier="Hot")
    assert rate == 0.03


def test_managementgroup_scope_skipped(api_mock):
    res = _Reservation(
        sku_name="Blob_Storage_Reserved_Capacity_LRS_Hot_100TB",
        applied_scope_type="ManagementGroup",
        applied_scopes=["/providers/Microsoft.Management/managementGroups/mg1"],
    )
    api_mock.return_value.reservation.list_all.return_value = iter([res])
    with mock.patch.object(reservations,
                           "_fetch_retail_reservation_rate",
                           return_value=0.99):
        rate = get_effective_storage_rate(
            credential=mock.Mock(), subscription_id="subA",
            region="eastus", redundancy="LRS", tier="Hot")
    assert rate is None


# ---- never-throws contract --------------------------------------------

def test_helper_never_throws_on_sdk_http_exception(api_mock, http_error):
    api_mock.return_value.reservation.list_all.side_effect = (
        http_error("boom"))
    rate = get_effective_storage_rate(
        credential=mock.Mock(), subscription_id="subA",
        region="eastus", redundancy="LRS", tier="Hot")
    assert rate is None


def test_helper_never_throws_on_generic_exception(api_mock):
    api_mock.return_value.reservation.list_all.side_effect = (
        RuntimeError("kaboom"))
    rate = get_effective_storage_rate(
        credential=mock.Mock(), subscription_id="subA",
        region="eastus", redundancy="LRS", tier="Hot")
    assert rate is None
