# OPTSCALE_AZURE_NATIVE module v1
"""Azure orphan NIC detection recommendation module.

Detects Azure Network Interface Cards that exist in a subscription but are
not attached to any virtual machine.  Because OptScale's cloud adapter does
not ingest NICs (they carry no direct cost), this module inserts minimal
sentinel resource documents into restapi.resources so each orphan NIC can be
surfaced in the recommendation tile and tracked over time.

Sentinel documents are distinguished by ``meta.created_by ==
"azure_orphan_nics_native"``.  This value intentionally differs from the
overlay sentinel ``"azure_alias_wrapper"`` so both systems can coexist safely
during the Phase B overlap window.

Per-run reconciliation:
  At the end of each scan, any sentinel whose ARM ID is absent from the
  current Azure response has its ``deleted_at`` field set to the run
  timestamp.  The companion archive module reads this field to decide
  archival reason without making a fresh SDK call.

Resource resolution (per NIC):
  1. Exact match on ``cloud_resource_id`` (lowercased ARM ID) + live doc.
     Use existing ``_id`` and ``pool_id``.
  2. No existing doc: insert sentinel.  Borrow ``pool_id`` / ``employee_id``
     from the oldest qualifying sibling in the same cloud account.  Sibling
     query MUST require ``employee_id != null`` and ``pool_id != null`` to
     avoid the null-leak that crashes the frontend Filters component.
"""
import logging
import uuid
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple

from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from pymongo import UpdateOne
from pymongo.errors import PyMongoError

from bumiworker.bumiworker.modules.base import ModuleBase


class OrphanNic(NamedTuple):
    arm_id: str
    name: str
    location: Optional[str]


# Azure SDK + Mongo errors are kept distinct from generic Exception to make
# silent-failure surfaces explicit.  ImportError from the Azure SDK is
# intentionally NOT caught here — a missing SDK is a structural deployment
# bug that should crash the module at import time, not be logged per-account
# as if it were a tenant-specific transient failure.

LOG = logging.getLogger(__name__)

for _noisy in (
    "azure",
    "azure.identity",
    "azure.core",
    "azure.core.pipeline.policies.http_logging_policy",
):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

SUPPORTED_CLOUD_TYPES = ["azure_cnr"]


def _get_azure_creds(rest_client, organization_id: str) -> Dict[str, Dict]:
    """Return ``{cloud_account_id: {subscription_id, tenant, client_id, secret, name, parent_id}}``.

    Joins each ``azure_cnr`` cloud account with its ``azure_tenant`` parent to
    obtain service-principal credentials.  Standalone ``azure_cnr`` accounts
    (no parent) store credentials directly on themselves.
    """
    _, response = rest_client.cloud_account_list(
        organization_id, process_recommendations=True
    )
    accounts = response.get("cloud_accounts", [])
    parents: Dict[str, Dict] = {}
    for ca in accounts:
        if ca.get("type") == "azure_tenant":
            parents[ca["id"]] = ca.get("config", {})
    out: Dict[str, Dict] = {}
    for ca in accounts:
        if ca.get("type") != "azure_cnr":
            continue
        cfg = ca.get("config", {})
        sub_id = cfg.get("subscription_id")
        parent_cfg = parents.get(ca.get("parent_id") or "", {})
        creds = parent_cfg if parent_cfg else cfg
        if not sub_id or not all(
            k in creds for k in ("tenant", "client_id", "secret")
        ):
            continue
        out[ca["id"]] = {
            "subscription_id": sub_id,
            "tenant": creds["tenant"],
            "client_id": creds["client_id"],
            "secret": creds["secret"],
            "name": ca.get("name"),
            "parent_id": ca.get("parent_id"),
        }
    return out


def _list_orphan_nics(creds: Dict) -> List[OrphanNic]:
    """Return list of OrphanNic tuples for NICs with no VM attachment.

    Excludes NICs that are service-managed and not user-deletable as orphan
    cleanup targets:

    - ``virtual_machine``: standard VM attachment (SDK-native attribute).
    - ``virtual_machine_scale_set``: VMSS instance NIC — VMSS orchestration
      mode attaches NICs to scale-set instances without populating
      ``virtual_machine``, so this field is checked separately.
    - ``private_endpoint``: NIC is the backing interface for a
      ``Microsoft.Network/privateEndpoints`` resource.  Deleting it would
      break private DNS resolution and connectivity to the target service.
    - ``private_link_service``: NIC is the backing interface for a
      ``Microsoft.Network/privateLinkServices`` resource.

    Defensive ``getattr`` is used for the three service-managed fields so
    that a future SDK rename surfaces as a clean "field absent → None" path
    rather than an ``AttributeError``; the runtime contract relies on
    ``getattr`` with default, not on ``_attribute_map`` presence.  SDK
    signature locks are covered by
    ``TestStorageAccountAttributeMapLocked.test_required_fields_present``.
    """
    cred = ClientSecretCredential(
        creds["tenant"], creds["client_id"], creds["secret"]
    )
    client = NetworkManagementClient(cred, creds["subscription_id"])
    out: List[OrphanNic] = []
    for nic in client.network_interfaces.list_all():
        if nic.virtual_machine is not None:
            continue
        if getattr(nic, "virtual_machine_scale_set", None) is not None:
            continue
        if getattr(nic, "private_endpoint", None) is not None:
            continue
        if getattr(nic, "private_link_service", None) is not None:
            continue
        out.append(
            OrphanNic(
                arm_id=nic.id.lower(),
                name=nic.name,
                location=nic.location,
            )
        )
    return out


def _resolve_or_insert_resource(
    coll,
    cloud_account_id: str,
    arm_id_lower: str,
    name: str,
    region: Optional[str],
    now_ts: int,
) -> Tuple[str, Optional[str]]:
    """Return ``(resource_id, pool_id)``.  Inserts a sentinel doc when absent.

    Step 1: exact match scoped to real cloud-adapter docs (no meta.created_by)
    OR our own sentinels — overlay sentinels (created_by="azure_alias_wrapper")
    are explicitly excluded so the two systems do not share lifecycle state
    during the Phase B overlap window.

    Step 2: if absent, borrow ``pool_id``/``employee_id`` from the oldest
    qualifying sibling in the same account.  The sibling filter MUST require
    both fields to be non-null — null values propagate to the recommendation
    row and crash the frontend Filters component org-wide.
    """
    doc = coll.find_one(
        {
            "cloud_resource_id": arm_id_lower,
            "cloud_account_id": cloud_account_id,
            "deleted_at": 0,
            "$or": [
                {"meta.created_by": {"$exists": False}},
                {"meta.created_by": "azure_orphan_nics_native"},
            ],
        },
        {"_id": 1, "pool_id": 1},
    )
    if doc:
        return doc["_id"], doc.get("pool_id")

    sibling = coll.find_one(
        {
            "cloud_account_id": cloud_account_id,
            "deleted_at": 0,
            "employee_id": {"$ne": None},
            "pool_id": {"$ne": None},
        },
        {"pool_id": 1, "employee_id": 1},
        sort=[("created_at", 1), ("_id", 1)],
    )
    if sibling is None:
        raise RuntimeError(
            f"no qualifying sibling for {cloud_account_id}"
        )

    doc_id = str(uuid.uuid4())
    now_dt = datetime.utcfromtimestamp(now_ts).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    doc = {
        "_id": doc_id,
        "cloud_account_id": cloud_account_id,
        "cloud_resource_id": arm_id_lower,
        "name": name,
        "region": region,
        "resource_type": "Network Interface",
        "service_name": "microsoft.network",
        "tags": {},
        "created_at": now_ts,
        "deleted_at": 0,
        "first_seen": now_ts,
        "last_seen": now_ts,
        "_first_seen_date": now_dt,
        "_last_seen_date": now_dt,
        "active": False,
        "pool_id": sibling["pool_id"],
        "employee_id": sibling["employee_id"],
        "meta": {"created_by": "azure_orphan_nics_native"},
    }
    coll.insert_one(doc)
    return doc_id, sibling["pool_id"]


def _touch_resource(coll, doc_id: str, now_ts: int) -> None:
    """Update ``last_seen`` / ``_last_seen_date`` on our own sentinel docs only.

    The ``meta.created_by`` guard prevents accidental writes to real
    cloud-adapter documents that happen to share the same ``_id``.
    """
    coll.update_one(
        {"_id": doc_id, "meta.created_by": "azure_orphan_nics_native"},
        {
            "$set": {
                "last_seen": now_ts,
                "_last_seen_date": datetime.utcfromtimestamp(now_ts).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            }
        },
    )


def _emit_rows_from_existing_sentinels(
    coll,
    cloud_account_id: str,
    cloud_account_name: Optional[str],
    excluded_pools: Dict,
) -> List[Dict[str, Any]]:
    """Re-emit recommendation rows from live native sentinels.

    Used as a safe fallback when an account's live Azure scan fails — the
    previous run's findings are preserved in the checklist so
    ArchiveBase.get_archive_candidates does not flag them as disappeared,
    which would trigger false RECOMMENDATION_IRRELEVANT archival of NICs
    that are still genuinely orphan.

    Reads the same sentinel docs the recommendation module wrote on a
    healthy run.  No fresh Azure SDK call.  Skipped sentinels (deleted_at
    != 0) are excluded so resolved NICs don't reappear.
    """
    rows: List[Dict[str, Any]] = []
    sentinels = coll.find(
        {
            "cloud_account_id": cloud_account_id,
            "deleted_at": 0,
            "meta.created_by": "azure_orphan_nics_native",
        },
        {
            "_id": 1,
            "cloud_resource_id": 1,
            "name": 1,
            "region": 1,
            "pool_id": 1,
        },
    )
    for s in sentinels:
        pool_id = s.get("pool_id")
        rows.append(
            {
                "cloud_resource_id": s["cloud_resource_id"],
                "resource_name": s.get("name"),
                "resource_id": s["_id"],
                "cloud_account_id": cloud_account_id,
                "cloud_type": "azure_cnr",
                "cloud_account_name": cloud_account_name,
                "saving": 0.0,
                "region": s.get("region"),
                "is_excluded": (
                    (pool_id in excluded_pools)
                    if (excluded_pools and pool_id)
                    else False
                ),
                "folder_id": None,
                "zone_id": None,
            }
        )
    return rows


def _reconcile_deleted(
    coll,
    cloud_account_id: str,
    current_arm_ids: Set[str],
    now_ts: int,
) -> int:
    """Mark sentinels absent from the current scan as deleted.

    Returns the number of docs updated.
    """
    sentinels = coll.find(
        {
            "cloud_account_id": cloud_account_id,
            "deleted_at": 0,
            "meta.created_by": "azure_orphan_nics_native",
        },
        {"_id": 1, "cloud_resource_id": 1},
    )
    ops = []
    for s in sentinels:
        if s["cloud_resource_id"] not in current_arm_ids:
            ops.append(
                UpdateOne({"_id": s["_id"]}, {"$set": {"deleted_at": now_ts}})
            )
    if ops:
        coll.bulk_write(ops, ordered=False)
    return len(ops)


class AzureOrphanNics(ModuleBase):
    """Recommendation module: Azure Network Interfaces not attached to any VM."""

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict(
            {
                "excluded_pools": {
                    "default": {},
                    "clean_func": self.clean_excluded_pools,
                },
                "skip_cloud_accounts": {"default": []},
            }
        )

    def _get(self) -> List[Dict[str, Any]]:
        (excluded_pools, skip_cloud_accounts) = self.get_options_values()
        ca_map = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        if not ca_map:
            return []

        # Credential resolution failure is org-wide (REST client / auth bug),
        # not per-tenant.  Re-raise so it surfaces as a real error on the
        # checklist rather than masquerading as "no orphan NICs".
        creds_by_ca = _get_azure_creds(self.rest_client, self.organization_id)

        coll = self.mongo_client.restapi.resources
        now_ts = int(self.created_at)
        rows: List[Dict[str, Any]] = []

        for ca_id, ca in ca_map.items():
            creds = creds_by_ca.get(ca_id)
            if not creds:
                LOG.warning("no credentials for cloud_account_id=%s", ca_id)
                continue

            try:
                nics = _list_orphan_nics(creds)
            except Exception:
                LOG.exception(
                    "orphan-NIC enumeration failed for cloud_account_id=%s;"
                    " preserving previous-run rows from live sentinels to"
                    " avoid mass false archival",
                    ca_id,
                )
                try:
                    rows.extend(_emit_rows_from_existing_sentinels(
                        coll, ca_id, ca.get("name"), excluded_pools,
                    ))
                except Exception:
                    LOG.exception(
                        "fallback sentinel-emit also failed for cloud_account_id=%s;"
                        " rows for this account will be missing this cycle and may"
                        " trigger false archival downstream",
                        ca_id,
                    )
                continue

            current_arm_ids = {n.arm_id for n in nics}
            try:
                _reconcile_deleted(coll, ca_id, current_arm_ids, now_ts)
            except PyMongoError:
                LOG.exception(
                    "reconciliation failed for cloud_account_id=%s;"
                    " preserving previous-run rows to avoid mass false archival",
                    ca_id,
                )
                try:
                    rows.extend(_emit_rows_from_existing_sentinels(
                        coll, ca_id, ca.get("name"), excluded_pools,
                    ))
                except Exception:
                    LOG.exception(
                        "fallback sentinel-emit also failed for cloud_account_id=%s",
                        ca_id,
                    )
                continue

            mongo_failure = False
            for nic in nics:
                try:
                    res_id, pool_id = _resolve_or_insert_resource(
                        coll, ca_id, nic.arm_id, nic.name, nic.location, now_ts,
                    )
                    _touch_resource(coll, res_id, now_ts)
                except RuntimeError:
                    LOG.warning(
                        "cannot resolve sibling for orphan NIC %s in account %s;"
                        " skipping",
                        nic.arm_id,
                        ca_id,
                    )
                    continue
                except PyMongoError:
                    # A pymongo error here means partial data has already been
                    # written this cycle; rather than silently emit a partial
                    # set, abandon the rest of this account's NICs and let the
                    # next run pick up the slack.
                    LOG.exception(
                        "mongo failure during resource-resolve for nic=%s account=%s;"
                        " abandoning account",
                        nic.arm_id, ca_id,
                    )
                    mongo_failure = True
                    break

                rows.append(
                    {
                        "cloud_resource_id": nic.arm_id,
                        "resource_name": nic.name,
                        "resource_id": res_id,
                        "cloud_account_id": ca_id,
                        "cloud_type": "azure_cnr",
                        "cloud_account_name": ca.get("name"),
                        "saving": 0.0,
                        "region": nic.location,
                        "is_excluded": (
                            (pool_id in excluded_pools)
                            if (excluded_pools and pool_id)
                            else False
                        ),
                        "folder_id": None,
                        "zone_id": None,
                    }
                )
            if mongo_failure:
                # Drop partial rows from this account, replace with full
                # sentinel-derived set so archive does not see disappearance.
                rows = [r for r in rows if r["cloud_account_id"] != ca_id]
                try:
                    rows.extend(_emit_rows_from_existing_sentinels(
                        coll, ca_id, ca.get("name"), excluded_pools,
                    ))
                except Exception:
                    LOG.exception(
                        "fallback sentinel-emit failed after partial-mongo failure"
                        " for cloud_account_id=%s",
                        ca_id,
                    )

        return rows


def main(organization_id, config_client, created_at, **kwargs):
    return AzureOrphanNics(organization_id, config_client, created_at).get()


def get_module_email_name():
    return "Azure Orphan NICs"
