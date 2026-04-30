# OPTSCALE_AZURE_NATIVE module v1
"""Azure abandoned (idle) storage account detection recommendation module.

Detects Azure Storage Accounts that have existed for at least
``min_account_age_days`` days but generated fewer than
``idle_transactions_threshold`` transactions in the last
``idle_days_window`` days.  Only accounts whose ``used_capacity_gb``
is non-None and whose estimated saving is positive are emitted on the
healthy path.

Sentinel documents (``meta.created_by == "azure_abandoned_storage_accounts_native"``)
are inserted for accounts that OptScale's cloud adapter has not yet ingested.
This value is intentionally distinct from the overlay sentinel
``"azure_alias_wrapper"`` so both systems coexist safely during the Phase B
overlap window where the overlay still emits the same data into the
AWS-branded "Abandoned S3 Buckets" tile.

Per-run reconciliation:
  At the end of each scan, any sentinel whose ARM ID is absent from the
  current Azure response has its ``deleted_at`` field set to the run
  timestamp.  The companion archive module reads this field to decide
  archival reason without making a fresh SDK call.

Resource resolution (per account):
  1. Exact match on ``cloud_resource_id`` (lowercased ARM ID) scoped to real
     cloud-adapter docs OR our own sentinels; overlay sentinels
     (``created_by="azure_alias_wrapper"``) are excluded.
  2. No existing doc: sibling lookup then sentinel insert.  The sibling
     query MUST require both ``employee_id != null`` and ``pool_id != null``
     to prevent the null-leak that crashes the frontend Filters component
     org-wide (see optscale_azure_aliases_null_owner.md).

Saving estimate:
  retail price per GB/month (via Azure Retail Prices API) * used_capacity_gb.
  Retail price is fetched once per (subscription, region, sku, kind,
  access_tier) tuple and cached for the lifetime of the run.  A
  ``threading.Lock`` guards the shared cache dict because ThreadPoolExecutor
  worker threads run ``_scan_one_account`` concurrently.
"""
import json
import logging
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple

from azure.core.exceptions import AzureError, HttpResponseError, ServiceRequestError
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.storage import StorageManagementClient
from pymongo import UpdateOne
from pymongo.errors import DuplicateKeyError, PyMongoError

from bumiworker.bumiworker.modules.base import ModuleBase


LOG = logging.getLogger(__name__)

for _noisy in (
    "azure",
    "azure.identity",
    "azure.core",
    "azure.core.pipeline.policies.http_logging_policy",
):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

SUPPORTED_CLOUD_TYPES = ["azure_cnr"]
NATIVE_MARKER = "azure_abandoned_storage_accounts_native"
DEFAULT_IDLE_DAYS_WINDOW = 7
DEFAULT_IDLE_TRANSACTIONS_THRESHOLD = 100
DEFAULT_MIN_ACCOUNT_AGE_DAYS = 30
DEFAULT_MIN_USED_CAPACITY_GB = 1.0
PROBE_BUDGET_SECS = 120
RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"
RETAIL_PRICES_API_VERSION = "2023-01-01-preview"
HTTP_TIMEOUT_SECS = 30


class StorageAccountInfo(NamedTuple):
    arm_id: str
    name: str
    location: Optional[str]
    age_days: Optional[int]
    transactions: float
    used_capacity_gb: Optional[float]
    saving: float
    sku_name: Optional[str]
    kind: Optional[str]
    access_tier: Optional[str]


class ScanResult(NamedTuple):
    """Return type of _scan_one_account.

    ``authoritative`` is True only when the list+probe pipeline ran without
    per-account probe failures dominating (failure rate < 50%) and the
    deadline did not trip before the sweep completed.  A non-authoritative
    result means callers must NOT reconcile-delete sentinels — doing so would
    cause mass false archival of still-idle accounts.
    """

    accounts: List[StorageAccountInfo]
    authoritative: bool


# ---------------------------------------------------------------------------
# Inline helpers
# ---------------------------------------------------------------------------


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


def _account_age_days(creation_time) -> Optional[int]:
    """Days since storage account creation.  None if unparseable."""
    if creation_time is None:
        return None
    try:
        if isinstance(creation_time, datetime):
            ct = creation_time
        else:
            ct = datetime.fromisoformat(str(creation_time).replace("Z", "+00:00"))
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return int((now - ct).total_seconds() // 86400)
    except Exception as exc:
        LOG.warning("could not parse creation_time %r: %s", creation_time, exc)
        return None


def _is_service_managed(acct) -> bool:
    """Return True if the account is platform-managed and should be skipped.

    Checks (in order):
    1. ``kind == "FileStorage"`` — Azure Files premium shares; billed to the
       owning service, not the data team.
    2. Premium redundancy (``sku.name`` in {Premium_LRS, Premium_ZRS}) AND
       ``kind`` in {Storage, StorageV2} — legacy premium blob accounts
       created by Azure services.
    3. Tag ``ms-resource-usage`` present — explicit service-managed marker.
    4. Name contains 'diag' (case-insensitive) AND any tag key starts with
       ``'hidden-link:'`` — diagnostic/linked accounts.
    All attribute access is defensive (getattr with default) to survive SDK
    changes without raising AttributeError.
    """
    kind = getattr(acct, "kind", None)
    sku_name = getattr(getattr(acct, "sku", None), "name", None)
    tags = getattr(acct, "tags", None) or {}
    name = (getattr(acct, "name", None) or "").lower()

    if kind == "FileStorage":
        LOG.debug(
            "_is_service_managed: skipping %s (kind=FileStorage)", getattr(acct, "name", "?")
        )
        return True

    if sku_name in {"Premium_LRS", "Premium_ZRS"} and kind in {"Storage", "StorageV2"}:
        LOG.debug(
            "_is_service_managed: skipping %s (premium sku=%s kind=%s)",
            getattr(acct, "name", "?"),
            sku_name,
            kind,
        )
        return True

    if "ms-resource-usage" in tags:
        LOG.debug(
            "_is_service_managed: skipping %s (ms-resource-usage tag present)",
            getattr(acct, "name", "?"),
        )
        return True

    if "diag" in name and any(str(k).startswith("hidden-link:") for k in tags):
        LOG.debug(
            "_is_service_managed: skipping %s (diag name + hidden-link tag)",
            getattr(acct, "name", "?"),
        )
        return True

    return False


def _probe_transactions(
    monitor_client,
    arm_id: str,
    days: int,
) -> Optional[float]:
    """Sum 'Transactions' metric over ``days`` for the storage account.

    Returns None on exception (probe failed — do not claim idle without
    evidence).  Returns 0.0 when the call succeeds but the timeseries is
    empty (confirmed idle with no recorded transactions).
    """
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        timespan = (
            f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
            f"{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        resp = monitor_client.metrics.list(
            resource_uri=arm_id,
            timespan=timespan,
            interval="P1D",
            metricnames="Transactions",
            aggregation="Total",
        )
        total = 0.0
        for m in resp.value or []:
            for ts in m.timeseries or []:
                for d in ts.data or []:
                    v = getattr(d, "total", None)
                    if v is not None:
                        total += float(v)
        return total
    except (HttpResponseError, ServiceRequestError, AzureError) as exc:
        LOG.warning("transactions probe failed for %s: %s", arm_id, exc, exc_info=True)
        return None


def _probe_used_capacity_gb(
    monitor_client,
    arm_id: str,
) -> Optional[float]:
    """Most-recent 'UsedCapacity' Average over a 48-hour window, in GB.

    Returns 0.0 when the call succeeds but the timeseries is empty (genuine
    "no capacity reported" — account exists but Azure Monitor has no data yet).
    Returns None ONLY on exception (probe failed — treat as transient error).

    This mirrors the ``_probe_transactions`` convention: 0.0 means confirmed
    empty, None means error.  Callers must count None toward probe_failures;
    0.0 is a legitimate data point and must not increment the failure counter.
    """
    try:
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=48)
        timespan = (
            f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
            f"{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        )
        resp = monitor_client.metrics.list(
            resource_uri=arm_id,
            timespan=timespan,
            interval="PT1H",
            metricnames="UsedCapacity",
            aggregation="Average",
        )
        latest: Optional[float] = None
        for m in resp.value or []:
            for ts in m.timeseries or []:
                for d in ts.data or []:
                    v = getattr(d, "average", None)
                    if v is not None:
                        latest = float(v)
        return (latest / (1024 ** 3)) if latest is not None else 0.0
    except (HttpResponseError, ServiceRequestError, AzureError) as exc:
        LOG.warning("used capacity probe failed for %s: %s", arm_id, exc, exc_info=True)
        return None


def _meter_name_for(
    sku_name: Optional[str],
    kind: Optional[str],
    access_tier: Optional[str],
) -> Optional[str]:
    """Derive Retail Prices API meter name substring for the account's data storage meter.

    Premium BlockBlobStorage accounts use a single-tier meter regardless of
    access_tier.  For all other accounts the redundancy suffix is derived from
    ``sku_name`` with a longest-prefix-first scan to avoid ``Standard_RAGZRS``
    matching a shorter suffix earlier in the list.

    Returns None when no meter can be derived (unrecognised sku/kind combo).
    """
    sku = sku_name or ""
    tier = access_tier or "Hot"

    # Premium BlockBlobStorage — single undivided meter name.
    if kind == "BlockBlobStorage" and sku in {"Premium_LRS", "Premium_ZRS"}:
        return "Premium Block Blob"

    # Derive redundancy label from sku_name.  Iterate longest-prefix-first so
    # Standard_RAGZRS matches "RAGZRS" before "GRS" or "ZRS".
    redundancy_order = ("RAGZRS", "RAGRS", "GZRS", "GRS", "ZRS", "LRS")
    redundancy: Optional[str] = None
    for suffix in redundancy_order:
        if suffix in sku.upper():
            redundancy = suffix
            break

    if redundancy is None:
        return None

    # RAGRS is exposed in the Retail API as "RA-GRS".
    display_redundancy = {
        "RAGZRS": "RA-GZRS",
        "RAGRS": "RA-GRS",
        "GZRS": "GZRS",
        "GRS": "GRS",
        "ZRS": "ZRS",
        "LRS": "LRS",
    }.get(redundancy, redundancy)

    if tier == "Cool":
        return f"Cool {display_redundancy} Data Stored"
    if tier == "Cold":
        return f"Cold {display_redundancy} Data Stored"
    # Hot or unrecognised — fall through to Hot.
    return f"Hot {display_redundancy} Data Stored"


RETAIL_PRICES_MAX_PAGES = 20


def _get_retail_price_per_gb(
    subscription_id: str,
    region: str,
    sku_name: Optional[str],
    kind: Optional[str],
    access_tier: Optional[str],
    cache: Dict,
    lock: threading.Lock,
) -> Tuple[Optional[float], bool]:
    """Return ``(price_per_gb, transient_error)`` for this account type.

    Uses the Azure Retail Prices API (no auth required).  Results are cached
    per ``(subscription_id, region, sku_name, kind, access_tier)`` tuple for
    the lifetime of the run.  The ``lock`` must be passed by the caller to
    guard concurrent dict access across ThreadPoolExecutor workers.

    Pagination: the API returns results across multiple pages via
    ``NextPageLink``.  All pages are iterated until the meter is found or all
    pages are exhausted.  A defensive cap of ``RETAIL_PRICES_MAX_PAGES`` pages
    prevents runaway pagination.

    ``transient_error=True`` iff an HTTP/network exception was raised during a
    pagination request — the result is NOT cached so the next run retries.
    ``transient_error=False`` on cache hit, missing required fields, unknown
    meter, or pagination cap reached — these are all legitimate non-error
    outcomes.  Callers must increment ``probe_failures`` only when
    ``transient_error=True``; doing so for legitimate no-meter cases would
    misrepresent the scan quality and suppress valid archival decisions.
    """
    if not region or not sku_name or not kind:
        return (None, False)
    tier_key = access_tier or "Hot"
    cache_key = (subscription_id, region, sku_name, kind, tier_key)
    with lock:
        if cache_key in cache:
            # Cache hit: value may be None (legitimate "no such meter") or a
            # float.  Either way, not a transient error.
            return (cache[cache_key], False)

    meter_substr = _meter_name_for(sku_name, kind, access_tier)
    if meter_substr is None:
        with lock:
            cache[cache_key] = None
        return (None, False)

    filter_expr = (
        f"serviceName eq 'Storage' and armRegionName eq '{region}' "
        f"and priceType eq 'Consumption'"
    )
    params = urllib.parse.urlencode(
        {
            "api-version": RETAIL_PRICES_API_VERSION,
            "$filter": filter_expr,
        }
    )
    url: Optional[str] = f"{RETAIL_PRICES_URL}?{params}"
    pages = 0

    while url and pages < RETAIL_PRICES_MAX_PAGES:
        try:
            with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SECS) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, ValueError) as exc:
            LOG.warning(
                "retail prices API request failed for %s %s (page %d): %s",
                region,
                meter_substr,
                pages + 1,
                exc,
                exc_info=True,
            )
            # Transient error mid-pagination — do not cache so next run retries.
            return (None, True)

        for item in payload.get("Items", []):
            meter_name = item.get("meterName") or ""
            if meter_substr.lower() in meter_name.lower():
                price = float(item["retailPrice"])
                with lock:
                    cache[cache_key] = price
                return (price, False)

        url = payload.get("NextPageLink") or None
        pages += 1

    if pages >= RETAIL_PRICES_MAX_PAGES and url:
        LOG.warning(
            "retail prices pagination cap (%d pages) reached for %s %s; "
            "meter not found — caching None",
            RETAIL_PRICES_MAX_PAGES,
            region,
            meter_substr,
        )

    # All pages exhausted without finding the meter.  Cache None as a
    # legitimate "no such meter" result so we do not hammer the API repeatedly.
    with lock:
        cache[cache_key] = None
    return (None, False)


def _scan_one_account(
    creds: Dict,
    idle_days_window: int,
    idle_transactions_threshold: int,
    min_account_age_days: int,
    min_used_capacity_gb: float,
    deadline: float,
    price_cache: Dict,
    price_lock: threading.Lock,
) -> ScanResult:
    """Scan one Azure subscription for idle storage accounts.

    Uses Track-2 SDK ctors: ``ClientSecretCredential`` from
    ``azure.identity``, ``StorageManagementClient`` and
    ``MonitorManagementClient`` from the respective azure-mgmt packages.
    msrestazure is intentionally NOT used here (track-2-only path).

    Returns a ``ScanResult`` NamedTuple.  ``authoritative`` is True only
    when the list+probe pipeline ran without per-account probe failures
    dominating (failure rate < 50%) and the deadline did not trip.  Callers
    must NOT reconcile-delete sentinels when ``authoritative=False``.
    """
    cred = ClientSecretCredential(
        creds["tenant"], creds["client_id"], creds["secret"]
    )
    sub_id = creds["subscription_id"]
    storage_client = StorageManagementClient(cred, sub_id)
    monitor_client = MonitorManagementClient(cred, sub_id)

    try:
        accounts = list(storage_client.storage_accounts.list())
    except (HttpResponseError, ServiceRequestError, AzureError) as exc:
        LOG.warning(
            "storage_accounts.list failed for sub=%s: %s", sub_id, exc, exc_info=True
        )
        return ScanResult(accounts=[], authoritative=False)

    out: List[StorageAccountInfo] = []
    skipped_age = 0
    skipped_service = 0
    skipped_budget = 0
    skipped_active = 0
    skipped_no_probe = 0
    skipped_capacity = 0
    skipped_no_price = 0
    probe_attempts = 0
    probe_failures = 0
    deadline_tripped = False

    for acct in accounts:
        if time.time() > deadline:
            skipped_budget += 1
            deadline_tripped = True
            continue

        if _is_service_managed(acct):
            skipped_service += 1
            continue

        arm_id = (getattr(acct, "id", "") or "").lower()
        if not arm_id:
            continue

        age = _account_age_days(getattr(acct, "creation_time", None))
        if age is not None and age < min_account_age_days:
            skipped_age += 1
            continue

        sku_name: Optional[str] = getattr(
            getattr(acct, "sku", None), "name", None
        )
        kind: Optional[str] = getattr(acct, "kind", None)
        access_tier: Optional[str] = getattr(acct, "access_tier", None)
        region: Optional[str] = getattr(acct, "location", None)

        probe_attempts += 1
        transactions = _probe_transactions(monitor_client, arm_id, idle_days_window)
        if transactions is None:
            probe_failures += 1
            skipped_no_probe += 1
            continue

        if transactions >= idle_transactions_threshold:
            skipped_active += 1
            continue

        used_capacity_gb = _probe_used_capacity_gb(monitor_client, arm_id)

        if used_capacity_gb is None:
            # Probe error (exception in SDK call) — count toward failure rate
            # so transient Azure Monitor outages trip the non-authoritative
            # fallback rather than dropping every account silently.
            probe_failures += 1
            skipped_no_probe += 1
            continue

        if used_capacity_gb < min_used_capacity_gb:
            # Genuine empty timeseries (0.0) or real capacity below threshold —
            # neither is a probe failure.
            skipped_capacity += 1
            continue

        price_per_gb: Optional[float] = None
        price_transient = False
        if region:
            price_per_gb, price_transient = _get_retail_price_per_gb(
                sub_id,
                region,
                sku_name,
                kind,
                access_tier,
                price_cache,
                price_lock,
            )

        if price_per_gb is None:
            if price_transient:
                # HTTP/network failure fetching the pricing API — count as a
                # probe failure so a Retail Prices outage trips the
                # non-authoritative guard and _reconcile_deleted is skipped.
                probe_failures += 1
            skipped_no_price += 1
            continue

        saving = round(price_per_gb * used_capacity_gb, 6)

        if saving <= 0:
            continue

        out.append(
            StorageAccountInfo(
                arm_id=arm_id,
                name=getattr(acct, "name", None) or arm_id.rsplit("/", 1)[-1],
                location=region,
                age_days=age,
                transactions=transactions,
                used_capacity_gb=used_capacity_gb,
                saving=saving,
                sku_name=sku_name,
                kind=kind,
                access_tier=access_tier,
            )
        )

    # Authoritative iff: deadline did not trip AND per-account probe failure
    # rate is below 50% of probed accounts (allow some legitimate transients).
    high_failure_rate = probe_attempts > 0 and (
        probe_failures / probe_attempts
    ) >= 0.5
    authoritative = not deadline_tripped and not high_failure_rate

    LOG.info(
        "azure storage scan sub=%s: total=%d idle_candidates=%d "
        "skipped_service=%d skipped_age=%d skipped_active=%d "
        "skipped_no_probe=%d skipped_capacity=%d skipped_no_price=%d "
        "skipped_budget=%d probe_attempts=%d probe_failures=%d authoritative=%s",
        sub_id,
        len(accounts),
        len(out),
        skipped_service,
        skipped_age,
        skipped_active,
        skipped_no_probe,
        skipped_capacity,
        skipped_no_price,
        skipped_budget,
        probe_attempts,
        probe_failures,
        authoritative,
    )
    return ScanResult(accounts=out, authoritative=authoritative)


def _resolve_or_insert_resource(
    coll,
    ca_id: str,
    arm_id_lower: str,
    name: str,
    region: Optional[str],
    now_ts: int,
) -> Tuple[str, Optional[str]]:
    """Return ``(resource_id, pool_id)``.  Inserts a sentinel doc when absent.

    Step 1: exact match scoped to real cloud-adapter docs (no meta.created_by)
    OR our own sentinels; overlay sentinels (created_by="azure_alias_wrapper")
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
            "cloud_account_id": ca_id,
            "deleted_at": 0,
            "$or": [
                {"meta.created_by": {"$exists": False}},
                {"meta.created_by": NATIVE_MARKER},
            ],
        },
        {"_id": 1, "pool_id": 1},
    )
    if doc:
        return doc["_id"], doc.get("pool_id")

    sibling = coll.find_one(
        {
            "cloud_account_id": ca_id,
            "deleted_at": 0,
            "employee_id": {"$ne": None},
            "pool_id": {"$ne": None},
        },
        {"pool_id": 1, "employee_id": 1},
        sort=[("created_at", 1), ("_id", 1)],
    )
    if sibling is None:
        raise RuntimeError(f"no qualifying sibling for cloud_account_id={ca_id}")

    doc_id = str(uuid.uuid4())
    now_dt = datetime.utcfromtimestamp(now_ts).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    sentinel = {
        "_id": doc_id,
        "cloud_account_id": ca_id,
        "cloud_resource_id": arm_id_lower,
        "name": name,
        "region": region,
        "resource_type": "Storage Account",
        "service_name": "microsoft.storage",
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
        "meta": {"created_by": NATIVE_MARKER},
    }
    try:
        coll.insert_one(sentinel)
    except DuplicateKeyError:
        # Another thread inserted concurrently — re-find with the same
        # overlay-scoped filter as step 1 above.
        doc = coll.find_one(
            {
                "cloud_resource_id": arm_id_lower,
                "cloud_account_id": ca_id,
                "deleted_at": 0,
                "$or": [
                    {"meta.created_by": {"$exists": False}},
                    {"meta.created_by": NATIVE_MARKER},
                ],
            },
            {"_id": 1, "pool_id": 1},
        )
        if doc:
            return doc["_id"], doc.get("pool_id")
        raise  # truly unrecoverable
    return doc_id, sibling["pool_id"]


def _reconcile_deleted(
    coll,
    ca_id: str,
    current_arm_ids: Set[str],
    now_ts: int,
) -> int:
    """Mark sentinels absent from the current scan as deleted.

    Returns the count of docs updated.
    """
    sentinels = coll.find(
        {
            "cloud_account_id": ca_id,
            "deleted_at": 0,
            "meta.created_by": NATIVE_MARKER,
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


def _emit_rows_from_existing_sentinels(
    coll,
    ca_id: str,
    ca_name: Optional[str],
    excluded_pools: Dict,
) -> List[Dict[str, Any]]:
    """Re-emit recommendation rows from live native sentinels.

    Used as a safe fallback when an account's live Azure scan fails so that
    ArchiveBase.get_archive_candidates does not treat them as disappeared and
    trigger false RECOMMENDATION_IRRELEVANT archival of still-idle accounts.

    Fallback rows carry ``saving=0.0``, ``transactions=0.0``, and
    ``used_capacity_gb=0.0``.  The healthy scan path filters out any account
    with ``saving <= 0`` (see ``_scan_one_account``), so a zero saving can
    never appear on a real healthy row for this module.  Zero-valued fallback
    rows are therefore uniquely identifiable without resorting to ``None``,
    which would break the rest_api optimization controller: the controller
    pops the ``saving`` key when it encounters ``saving is None``, causing a
    ``KeyError`` on the next numeric row, and ``limit_optimization_data``
    sorts by ``-x.get('saving', 0)`` which raises ``TypeError`` when the
    value is ``None`` rather than missing.

    The ``data_source="preserved_sentinel"`` discriminator is preserved for
    tooling and observability.  Because this module is NOT listed in
    ``modules_with_possible_zero_saving``, ``resource_recommendations.py``
    will drop these rows from per-resource dismiss/reactivate flows, which
    is correct — fallback rows belong only in the checklist for archive
    protection.
    """
    rows: List[Dict[str, Any]] = []
    sentinels = coll.find(
        {
            "cloud_account_id": ca_id,
            "deleted_at": 0,
            "meta.created_by": NATIVE_MARKER,
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
                "cloud_account_id": ca_id,
                "cloud_type": "azure_cnr",
                "cloud_account_name": ca_name,
                "saving": 0.0,
                "region": s.get("region"),
                "is_excluded": (
                    (pool_id in excluded_pools)
                    if (excluded_pools and pool_id)
                    else False
                ),
                "folder_id": None,
                "zone_id": None,
                "used_capacity_gb": 0.0,
                "transactions": 0.0,
                "age_days": None,
                "detected_at": None,
                "data_source": "preserved_sentinel",
            }
        )
    return rows


def _touch_resource(coll, doc_id: str, now_ts: int) -> None:
    """Update ``last_seen`` / ``_last_seen_date`` on our own sentinel docs only.

    The ``meta.created_by`` guard prevents accidental writes to real
    cloud-adapter documents that happen to share the same ``_id``.
    """
    coll.update_one(
        {"_id": doc_id, "meta.created_by": NATIVE_MARKER},
        {
            "$set": {
                "last_seen": now_ts,
                "_last_seen_date": datetime.utcfromtimestamp(now_ts).replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            }
        },
    )


# ---------------------------------------------------------------------------
# Module class
# ---------------------------------------------------------------------------


class AzureAbandonedStorageAccounts(ModuleBase):
    """Recommendation module: Azure Storage Accounts idle for extended periods."""

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict(
            {
                "idle_days_window": {"default": DEFAULT_IDLE_DAYS_WINDOW},
                "idle_transactions_threshold": {
                    "default": DEFAULT_IDLE_TRANSACTIONS_THRESHOLD
                },
                "min_account_age_days": {"default": DEFAULT_MIN_ACCOUNT_AGE_DAYS},
                "min_used_capacity_gb": {"default": DEFAULT_MIN_USED_CAPACITY_GB},
                "excluded_pools": {
                    "default": {},
                    "clean_func": self.clean_excluded_pools,
                },
                "skip_cloud_accounts": {"default": []},
            }
        )

    def _get(self) -> List[Dict[str, Any]]:
        detected_at = int(self.created_at)

        (
            idle_days_window,
            idle_transactions_threshold,
            min_account_age_days,
            min_used_capacity_gb,
            excluded_pools,
            skip_cloud_accounts,
        ) = self.get_options_values()

        ca_map = self.get_cloud_accounts(SUPPORTED_CLOUD_TYPES, skip_cloud_accounts)
        if not ca_map:
            return []

        # Credential resolution failure is org-wide (REST client / auth bug),
        # not per-tenant.  Re-raise so it surfaces as a real error on the
        # checklist rather than masquerading as "no idle accounts".
        creds_by_ca = _get_azure_creds(self.rest_client, self.organization_id)

        coll = self.mongo_client.restapi.resources
        price_cache: Dict = {}
        price_lock = threading.Lock()
        deadline = time.time() + PROBE_BUDGET_SECS

        rows: List[Dict[str, Any]] = []

        max_workers = min(8, len(ca_map))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures: Dict = {}
            for ca_id, ca in ca_map.items():
                creds = creds_by_ca.get(ca_id)
                if not creds:
                    LOG.warning(
                        "no credentials for cloud_account_id=%s; preserving sentinels",
                        ca_id,
                    )
                    try:
                        rows.extend(
                            _emit_rows_from_existing_sentinels(
                                coll, ca_id, ca.get("name"), excluded_pools
                            )
                        )
                    except Exception:
                        LOG.exception(
                            "fallback sentinel-emit failed for ca=%s during"
                            " creds lookup",
                            ca_id,
                        )
                    continue
                fut = executor.submit(
                    _scan_one_account,
                    creds,
                    idle_days_window,
                    idle_transactions_threshold,
                    min_account_age_days,
                    min_used_capacity_gb,
                    deadline,
                    price_cache,
                    price_lock,
                )
                futures[fut] = (ca_id, ca)

            for fut in as_completed(futures):
                ca_id, ca = futures[fut]
                ca_name = ca.get("name")

                try:
                    result: ScanResult = fut.result()
                except Exception:
                    LOG.exception(
                        "storage account scan failed for cloud_account_id=%s;"
                        " preserving previous-run rows to avoid mass false archival",
                        ca_id,
                    )
                    try:
                        rows.extend(
                            _emit_rows_from_existing_sentinels(
                                coll, ca_id, ca_name, excluded_pools
                            )
                        )
                    except Exception:
                        LOG.exception(
                            "fallback sentinel-emit also failed for"
                            " cloud_account_id=%s",
                            ca_id,
                        )
                    continue

                if not result.authoritative:
                    LOG.warning(
                        "non-authoritative scan for ca=%s (probe failures or"
                        " deadline tripped); preserving sentinels to avoid mass"
                        " false archival",
                        ca_id,
                    )
                    try:
                        rows.extend(
                            _emit_rows_from_existing_sentinels(
                                coll, ca_id, ca_name, excluded_pools
                            )
                        )
                    except Exception:
                        LOG.exception(
                            "fallback sentinel-emit also failed for"
                            " cloud_account_id=%s",
                            ca_id,
                        )
                    continue

                accounts: List[StorageAccountInfo] = result.accounts
                current_arm_ids: Set[str] = {a.arm_id for a in accounts}
                try:
                    _reconcile_deleted(coll, ca_id, current_arm_ids, detected_at)
                except PyMongoError:
                    LOG.exception(
                        "reconciliation failed for cloud_account_id=%s;"
                        " preserving previous-run rows to avoid mass false archival",
                        ca_id,
                    )
                    try:
                        rows.extend(
                            _emit_rows_from_existing_sentinels(
                                coll, ca_id, ca_name, excluded_pools
                            )
                        )
                    except Exception:
                        LOG.exception(
                            "fallback sentinel-emit also failed for"
                            " cloud_account_id=%s",
                            ca_id,
                        )
                    continue

                mongo_failure = False
                ca_rows: List[Dict[str, Any]] = []

                for acct in accounts:
                    try:
                        res_id, pool_id = _resolve_or_insert_resource(
                            coll,
                            ca_id,
                            acct.arm_id,
                            acct.name,
                            acct.location,
                            detected_at,
                        )
                        _touch_resource(coll, res_id, detected_at)
                    except RuntimeError:
                        LOG.warning(
                            "cannot resolve sibling for storage account %s in"
                            " account %s; skipping",
                            acct.arm_id,
                            ca_id,
                        )
                        continue
                    except PyMongoError:
                        LOG.exception(
                            "mongo failure during resource-resolve for account=%s"
                            " ca=%s; abandoning ca",
                            acct.arm_id,
                            ca_id,
                        )
                        mongo_failure = True
                        break

                    ca_rows.append(
                        {
                            "cloud_resource_id": acct.arm_id,
                            "resource_name": acct.name,
                            "resource_id": res_id,
                            "cloud_account_id": ca_id,
                            "cloud_type": "azure_cnr",
                            "cloud_account_name": ca_name,
                            "saving": acct.saving,
                            "region": acct.location,
                            "is_excluded": (
                                (pool_id in excluded_pools)
                                if (excluded_pools and pool_id)
                                else False
                            ),
                            "folder_id": None,
                            "zone_id": None,
                            "used_capacity_gb": acct.used_capacity_gb,
                            "transactions": acct.transactions,
                            "age_days": acct.age_days,
                            "detected_at": detected_at,
                            "data_source": "live_scan",
                        }
                    )

                if mongo_failure:
                    try:
                        rows.extend(
                            _emit_rows_from_existing_sentinels(
                                coll, ca_id, ca_name, excluded_pools
                            )
                        )
                    except Exception:
                        LOG.exception(
                            "fallback sentinel-emit failed after partial-mongo"
                            " failure for cloud_account_id=%s",
                            ca_id,
                        )
                else:
                    rows.extend(ca_rows)

        return rows


def main(organization_id, config_client, created_at, **kwargs):
    return AzureAbandonedStorageAccounts(
        organization_id, config_client, created_at
    ).get()


def get_module_email_name() -> str:
    return "Azure abandoned storage accounts"
