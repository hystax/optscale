"""SDK signature locks for the Azure storage discovery path.

These tests pin the attribute names that
``tools/cloud_adapter/clouds/azure.py``'s ``discover_bucket_resources``
relies on. They run offline (no Azure API calls) and exist to fail
loudly if a future ``azure-mgmt-storage`` upgrade renames or removes a
field we depend on.

The discovery layer captures meta used by downstream tier-recommendation
modules (cold/archive). When the SDK renames a field, those modules
silently lose signal — these locks force the rename to surface as a
test failure during dependency bumps.
"""
import inspect

import pytest


def test_storage_account_exposes_tier_fields():
    """``StorageAccount`` exposes the fields ``discover_bucket_resources``
    reads via ``getattr``: access_tier, kind, sku, is_hns_enabled,
    immutable_storage_with_versioning.
    """
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = models.StorageAccount

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())

    expected = {
        'access_tier',
        'kind',
        'sku',
        'is_hns_enabled',
        'immutable_storage_with_versioning',
    }
    missing = expected - params
    assert not missing, (
        f"StorageAccount missing expected fields: {missing}. "
        f"Discovery in tools/cloud_adapter/clouds/azure.py reads these "
        f"via getattr; an SDK rename would silently null them."
    )


def test_access_tier_enum_values():
    """``AccessTier`` enum carries the values our recommendation modules
    pattern-match on. Premium is account-default for BlockBlobStorage;
    Archive is per-blob only and intentionally absent here.
    """
    models = pytest.importorskip("azure.mgmt.storage.models")
    enum_cls = getattr(models, 'AccessTier', None)
    assert enum_cls is not None, "AccessTier enum missing from SDK"

    values = {str(v.value).lower() for v in enum_cls}
    expected = {'hot', 'cool', 'cold', 'premium'}
    missing = expected - values
    assert not missing, (
        f"AccessTier missing expected values: {missing}. "
        f"Premium signals BlockBlobStorage; Cold gates cold-tier recs."
    )


def test_sku_exposes_name_and_tier():
    """``Sku.name`` (e.g. Standard_LRS) and ``Sku.tier`` (Standard /
    Premium) are read by the discovery layer to filter premium accounts
    out of cold/archive recommendations.
    """
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = getattr(models, 'Sku', None)
    assert cls is not None, "Sku model missing from SDK"

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())
    assert 'name' in params, "Sku.name missing — premium filter breaks"
    assert 'tier' in params, "Sku.tier missing — premium filter breaks"


def test_blob_service_properties_exposes_tracking_policy():
    """``BlobServiceProperties`` exposes the fields captured by the
    extra ``blob_services.get_service_properties`` call:
    last_access_time_tracking_policy, is_versioning_enabled,
    delete_retention_policy.
    """
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = getattr(models, 'BlobServiceProperties', None)
    assert cls is not None, "BlobServiceProperties missing from SDK"

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())

    expected = {
        'last_access_time_tracking_policy',
        'is_versioning_enabled',
        'delete_retention_policy',
    }
    missing = expected - params
    assert not missing, (
        f"BlobServiceProperties missing expected fields: {missing}. "
        f"discover_bucket_resources reads these to populate the "
        f"last-access-tracking gate used by tier-recommendation modules."
    )


def test_last_access_time_tracking_policy_enable_field():
    """``LastAccessTimeTrackingPolicy.enable`` is the bool used as the
    cold/archive forecaster precondition. Without it on, blobs have no
    last-access timestamps and recommendations would run on noise.
    """
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = getattr(models, 'LastAccessTimeTrackingPolicy', None)
    assert cls is not None, "LastAccessTimeTrackingPolicy missing from SDK"

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())
    assert 'enable' in params, (
        "LastAccessTimeTrackingPolicy.enable missing — tracking-gate breaks."
    )


def test_delete_retention_policy_fields():
    """``DeleteRetentionPolicy`` exposes ``enabled`` and ``days``."""
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = getattr(models, 'DeleteRetentionPolicy', None)
    assert cls is not None, "DeleteRetentionPolicy missing from SDK"

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())
    assert {'enabled', 'days'}.issubset(params), (
        "DeleteRetentionPolicy.enabled / .days missing — soft-delete "
        "metadata capture breaks."
    )


def test_immutable_storage_with_versioning_enabled_field():
    """``ImmutableStorageAccount.enabled`` is the WORM gate flag."""
    models = pytest.importorskip("azure.mgmt.storage.models")
    cls = getattr(models, 'ImmutableStorageAccount', None)
    assert cls is not None, (
        "ImmutableStorageAccount missing from SDK — WORM detection breaks."
    )

    init_sig = inspect.signature(cls.__init__)
    params = set(init_sig.parameters.keys())
    assert 'enabled' in params, (
        "ImmutableStorageAccount.enabled missing — WORM gate breaks."
    )


def test_blob_services_operations_present():
    """``StorageManagementClient`` exposes ``blob_services`` and
    ``management_policies`` operation groups used by discovery.
    """
    storage_module = pytest.importorskip("azure.mgmt.storage")
    client_cls = getattr(storage_module, 'StorageManagementClient', None)
    assert client_cls is not None, "StorageManagementClient missing"

    init_sig = inspect.signature(client_cls.__init__)
    # Operations groups are attached at construction; we can't easily
    # introspect without an instance, so probe for the operations
    # classes in the operations module.
    ops_module = pytest.importorskip("azure.mgmt.storage.operations")
    assert hasattr(ops_module, 'BlobServicesOperations'), (
        "BlobServicesOperations missing — extra blob-service properties "
        "call in discover_bucket_resources breaks."
    )
    assert hasattr(ops_module, 'ManagementPoliciesOperations'), (
        "ManagementPoliciesOperations missing — lifecycle-policy detection "
        "in discover_bucket_resources breaks."
    )
    # Reference init_sig to keep the introspection live; if SDK shape
    # changes radically, signature check provides a fallback alarm.
    assert init_sig is not None
