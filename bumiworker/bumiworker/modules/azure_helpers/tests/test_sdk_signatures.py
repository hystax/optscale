"""Lock Azure SDK client constructor signatures used by bumiworker helpers.

The failure mode this file guards against: an SDK upgrade renames or
reorders positional parameters, the caller silently passes the wrong
value, the resulting HTTP call hits an invalid endpoint, the broad
``except Exception`` in every helper swallows the error, and the
recommendation run returns 0 rows.  The canonical example is
``AzureReservationAPI(credential, subscription_id)`` where
``subscription_id`` silently became ``base_url`` — ``list_all`` then
targeted a malformed URL, returned nothing, and phantom over-savings
figures were emitted for every tenant with Blob reservations.

Each test function here imports the *real* SDK class (or skips if the
package is absent), reads its ``__init__`` signature at runtime via
``inspect``, and asserts the parameter contract our callers rely on.
No fakes, no mocks — the whole point is to catch real SDK drift.

Clients covered
---------------
* ``AzureReservationAPI``      (azure-mgmt-reservations)
* ``MonitorManagementClient``  (azure-mgmt-monitor)
* ``StorageManagementClient``  (azure-mgmt-storage)
* ``ClientSecretCredential``   (azure-identity)
"""
import inspect

import pytest


# ---------------------------------------------------------------------------
# AzureReservationAPI
# ---------------------------------------------------------------------------

azure_mgmt_reservations = pytest.importorskip("azure.mgmt.reservations")


def test_azure_reservation_api_ctor_signature():
    """Guard the AzureReservationAPI(credential, base_url=None) contract.

    Failure mode: if the SDK adds ``subscription_id`` as the second
    positional parameter, any existing call of the form
    ``AzureReservationAPI(credential)`` would silently stop working
    because no parameter would be provided for the new slot, or a
    future refactor might accidentally re-introduce the positional
    ``subscription_id`` seen in the original bug where it was mistaken
    for ``base_url``, causing ``reservation.list_all()`` to target an
    invalid URL with errors swallowed by the broad ``except``.
    """
    from azure.mgmt.reservations import AzureReservationAPI

    sig = inspect.signature(AzureReservationAPI.__init__)
    params = list(sig.parameters)

    # First positional after self must be credentials/credential.
    assert params[1] in ("credentials", "credential"), (
        f"AzureReservationAPI ctor first arg renamed: {params}. "
        f"Update reservations.py caller and this assertion together."
    )

    # base_url must exist so the helper can rely on the default (None
    # means the standard Azure endpoint).
    assert "base_url" in params, (
        f"AzureReservationAPI lost base_url kwarg: {params}. "
        f"Review reservations.py — the helper depends on the SDK default."
    )

    # subscription_id must NOT be a constructor parameter.  This SDK is
    # tenant-scoped; subscription filtering is done per-call.  If the SDK
    # ever adds subscription_id here, callers must be audited to ensure
    # they are not accidentally supplying it positionally as base_url.
    assert "subscription_id" not in params, (
        f"AzureReservationAPI ctor now takes subscription_id: {params}. "
        f"Review azure_helpers/reservations.py — passing it positionally "
        f"would silently override base_url and break list_all."
    )


# ---------------------------------------------------------------------------
# MonitorManagementClient
# ---------------------------------------------------------------------------

azure_mgmt_monitor = pytest.importorskip("azure.mgmt.monitor")


def test_monitor_management_client_ctor_signature():
    """Guard the MonitorManagementClient(credential, subscription_id) contract.

    Failure mode: the SDK reorders or renames positional args so that
    ``subscription_id`` lands in the wrong slot, causing all metrics
    queries to hit the wrong subscription or raise an auth error that is
    swallowed by the broad ``except`` in metrics.py, resulting in every
    storage account reporting 0 transactions and being incorrectly
    flagged as a cold-tier candidate.
    """
    from azure.mgmt.monitor import MonitorManagementClient

    sig = inspect.signature(MonitorManagementClient.__init__)
    params = list(sig.parameters)

    # First positional after self must be credentials/credential.
    assert params[1] in ("credentials", "credential"), (
        f"MonitorManagementClient ctor first arg renamed: {params}. "
        f"Update metrics.py callers and this assertion together."
    )

    # Second positional must be subscription_id — metrics.py passes it
    # as the second positional argument in every call site.
    assert params[2] == "subscription_id", (
        f"MonitorManagementClient ctor second arg is no longer "
        f"subscription_id: {params}. metrics.py calls "
        f"MonitorManagementClient(credential, subscription_id) — "
        f"a rename or reorder here silently queries the wrong subscription."
    )


# ---------------------------------------------------------------------------
# StorageManagementClient
# ---------------------------------------------------------------------------

azure_mgmt_storage = pytest.importorskip("azure.mgmt.storage")


def test_storage_management_client_ctor_signature():
    """Guard the StorageManagementClient(credential, subscription_id) contract.

    Failure mode: same as MonitorManagementClient — if subscription_id
    moves to a different positional slot, azure_cold_tier_candidates.py
    would list storage accounts for the wrong subscription (or none),
    and the broad ``except`` would swallow the error, producing an empty
    recommendation run with no visible failure.
    """
    from azure.mgmt.storage import StorageManagementClient

    sig = inspect.signature(StorageManagementClient.__init__)
    params = list(sig.parameters)

    # First positional after self must be credentials/credential.
    assert params[1] in ("credentials", "credential"), (
        f"StorageManagementClient ctor first arg renamed: {params}. "
        f"Update azure_cold_tier_candidates.py caller and this assertion."
    )

    # Second positional must be subscription_id.
    assert params[2] == "subscription_id", (
        f"StorageManagementClient ctor second arg is no longer "
        f"subscription_id: {params}. azure_cold_tier_candidates.py calls "
        f"StorageManagementClient(credential, subscription_id) positionally."
    )


# ---------------------------------------------------------------------------
# ClientSecretCredential
# ---------------------------------------------------------------------------

azure_identity = pytest.importorskip("azure.identity")


def test_client_secret_credential_ctor_signature():
    """Guard the ClientSecretCredential(tenant_id, client_id, client_secret) contract.

    Failure mode: if the SDK renames or reorders these keyword arguments,
    azure_helpers/credentials.py silently constructs an invalid credential
    object.  Because ClientSecretCredential does not validate eagerly, the
    error only surfaces when ``get_token`` is called inside the SDK, which
    is then caught by the broad ``except`` in each helper, making the
    entire cloud account appear to have no resources.
    """
    from azure.identity import ClientSecretCredential

    sig = inspect.signature(ClientSecretCredential.__init__)
    params = list(sig.parameters)

    assert "tenant_id" in params, (
        f"ClientSecretCredential lost tenant_id parameter: {params}. "
        f"Update credentials.py make_credentials() and this assertion."
    )
    assert "client_id" in params, (
        f"ClientSecretCredential lost client_id parameter: {params}. "
        f"Update credentials.py make_credentials() and this assertion."
    )
    assert "client_secret" in params, (
        f"ClientSecretCredential lost client_secret parameter: {params}. "
        f"Update credentials.py make_credentials() and this assertion."
    )
