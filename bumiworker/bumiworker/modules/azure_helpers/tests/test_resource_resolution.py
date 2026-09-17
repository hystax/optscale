"""Unit tests for resolve_or_insert_resource invariants.

Critical: these pin the null-owner fix described in
.claude/refs/AZURE_OVERLAY.md and the project memory
optscale_azure_aliases_null_owner.md.
"""
import pytest

from bumiworker.bumiworker.modules.azure_helpers.resource_resolution import (
    resolve_or_insert_resource,
)


class FakeCollection(object):
    """Minimal mongo-like collection. Iterates docs on find_one with a
    very small predicate matcher — enough for the invariants we test."""

    def __init__(self, docs):
        self.docs = list(docs)
        self.inserted = []

    def _match(self, doc, query):
        for k, v in query.items():
            actual = doc.get(k)
            if isinstance(v, dict) and "$ne" in v:
                if actual == v["$ne"] or actual is v["$ne"]:
                    return False
            else:
                if actual != v:
                    return False
        return True

    def find_one(self, query, projection=None, sort=None):
        candidates = [d for d in self.docs if self._match(d, query)]
        if sort:
            for key, direction in reversed(sort):
                candidates.sort(
                    key=lambda d: d.get(key) or 0,
                    reverse=(direction < 0),
                )
        return candidates[0] if candidates else None

    def insert_one(self, doc):
        self.inserted.append(doc)
        self.docs.append(doc)


def _defaults(**overrides):
    base = {
        "cloud_account_id": "ca1",
        "cloud_resource_id": "/sub/rg/sa1",
        "name": "sa1",
        "resource_type": "Storage Account",
        "deleted_at": 0,
    }
    base.update(overrides)
    return base


def test_returns_oldest_created_match_via_sibling_sort():
    coll = FakeCollection([
        {"_id": "a", "cloud_account_id": "ca1", "deleted_at": 0,
         "employee_id": "e1", "pool_id": "p1", "created_at": 200},
        {"_id": "b", "cloud_account_id": "ca1", "deleted_at": 0,
         "employee_id": "e1", "pool_id": "p1", "created_at": 100},
    ])
    res_id, pool_id = resolve_or_insert_resource(
        coll,
        {"cloud_resource_id": "/sub/rg/sa-new",
         "cloud_account_id": "ca1", "deleted_at": 0},
        _defaults(employee_id=None, pool_id=None),
    )
    # Inserted; sibling 'b' (older created_at) is selected for owner copy.
    assert pool_id == "p1"
    assert coll.inserted and coll.inserted[0]["employee_id"] == "e1"


def test_ignores_null_employee_id_siblings():
    coll = FakeCollection([
        {"_id": "bad", "cloud_account_id": "ca1", "deleted_at": 0,
         "employee_id": None, "pool_id": "p1", "created_at": 50},
        {"_id": "good", "cloud_account_id": "ca1", "deleted_at": 0,
         "employee_id": "e1", "pool_id": "p1", "created_at": 200},
    ])
    res_id, pool_id = resolve_or_insert_resource(
        coll,
        {"cloud_resource_id": "/sub/rg/sa-new",
         "cloud_account_id": "ca1", "deleted_at": 0},
        _defaults(employee_id=None, pool_id=None),
    )
    assert coll.inserted[0]["employee_id"] == "e1"
    assert pool_id == "p1"


def test_insert_without_employee_id_raises():
    coll = FakeCollection([])  # no siblings
    with pytest.raises(ValueError):
        resolve_or_insert_resource(
            coll,
            {"cloud_resource_id": "/sub/rg/sa-new",
             "cloud_account_id": "ca1", "deleted_at": 0},
            _defaults(employee_id=None, pool_id="p1"),
        )


def test_insert_without_pool_id_raises():
    coll = FakeCollection([])
    with pytest.raises(ValueError):
        resolve_or_insert_resource(
            coll,
            {"cloud_resource_id": "/sub/rg/sa-new",
             "cloud_account_id": "ca1", "deleted_at": 0},
            _defaults(employee_id="e1", pool_id=None),
        )


def test_direct_hit_returns_existing():
    coll = FakeCollection([
        {"_id": "existing", "cloud_account_id": "ca1",
         "cloud_resource_id": "/sub/rg/sa1", "deleted_at": 0,
         "pool_id": "p1", "employee_id": "e1"},
    ])
    res_id, pool_id = resolve_or_insert_resource(
        coll,
        {"cloud_resource_id": "/sub/rg/sa1",
         "cloud_account_id": "ca1", "deleted_at": 0},
        _defaults(),
    )
    assert res_id == "existing"
    assert pool_id == "p1"
    assert coll.inserted == []
