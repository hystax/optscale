"""Null-owner-safe sibling lookup for Azure resource resolution.

INVARIANTS (enforced in resolve_or_insert_resource):
  * find_one filter REQUIRES employee_id != null AND pool_id != null.
    Any document carrying a null employee_id or pool_id crashes the
    frontend Filters component org-wide; matching one as a sibling
    propagates the null into the new sentinel doc.
  * sort=[("created_at", 1), ("_id", 1)] for deterministic tiebreak —
    stable across runs, oldest doc wins.
  * Insert without employee_id or pool_id raises ValueError. The signature
    refuses to insert the bug, so the null-owner regression cannot be
    re-introduced at the module level.
"""
import uuid


SIBLING_SORT = [("created_at", 1), ("_id", 1)]


def resolve_or_insert_resource(resources_collection, query, defaults):
    """Find a resource matching `query` (cloud_resource_id + cloud_account_id
    typically), or insert a new sentinel doc using `defaults`.

    Returns (resource_id, pool_id).

    INVARIANTS — see module docstring. The sibling-find here MUST require
    non-null employee_id AND pool_id; otherwise the frontend Filters
    component crashes org-wide as soon as any null leaks through.

    `defaults` MUST supply employee_id and pool_id (typically copied from
    the chosen sibling). Raises ValueError otherwise.
    """
    # Direct hit: a real resource doc already exists for this cloud_resource_id.
    doc = resources_collection.find_one(
        query, {"_id": 1, "pool_id": 1, "employee_id": 1})
    if doc:
        return doc["_id"], doc.get("pool_id")

    # No direct hit — pick a sibling owned by the same cloud account so we
    # can copy employee_id+pool_id into the sentinel insert. Filter requires
    # non-null fields per the null-owner invariant.
    cloud_account_id = query.get("cloud_account_id")
    if not cloud_account_id:
        raise ValueError(
            "resolve_or_insert_resource requires cloud_account_id in query")

    sibling = resources_collection.find_one(
        {
            "cloud_account_id": cloud_account_id,
            "deleted_at": 0,
            "employee_id": {"$ne": None},
            "pool_id": {"$ne": None},
        },
        {"pool_id": 1, "employee_id": 1},
        sort=SIBLING_SORT,
    )

    employee_id = (defaults.get("employee_id")
                   or (sibling or {}).get("employee_id"))
    pool_id = (defaults.get("pool_id")
               or (sibling or {}).get("pool_id"))

    if not employee_id:
        raise ValueError(
            "refusing to insert resource without employee_id "
            "(null leak crashes frontend Filters component)")
    if not pool_id:
        raise ValueError(
            "refusing to insert resource without pool_id "
            "(null leak crashes frontend Filters component)")

    new_id = str(uuid.uuid4())
    insert_doc = dict(defaults)
    insert_doc["_id"] = new_id
    insert_doc["employee_id"] = employee_id
    insert_doc["pool_id"] = pool_id
    insert_doc.setdefault("cloud_account_id", cloud_account_id)
    insert_doc.setdefault(
        "cloud_resource_id", query.get("cloud_resource_id"))
    insert_doc.setdefault("deleted_at", 0)

    resources_collection.insert_one(insert_doc)
    return new_id, pool_id
