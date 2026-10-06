"""Azure Monitor probes for storage account capacity / transactions / egress.

Uses `azure.identity.ClientSecretCredential` (track-2). Modern Azure
Monitor SDK (`azure-mgmt-monitor>=2.0`) accepts the TokenCredential
protocol directly, so `MonitorManagementClient(credential,
subscription_id)` works without a track-1 shim.

Documented gotchas baked in:
  * BlobCapacity / BlobCount: Azure Monitor only accepts `interval='PT1H'`
    for these metrics; P1D is rejected. PT1H is hardcoded — caller cannot
    override.
  * Tier-dim queries auto-rewrite scope to `/blobServices/default`. The
    Tier dimension is published only on the blob subresource scope.
  * Transactions has NO Tier dimension. The public surface deliberately
    splits get_account_transactions() (account-level totals only) from
    approximate_per_tier_transactions() (capacity-share approximation) so
    callers can't accidentally request a Tier-split they didn't compute.
  * Egress empty timeseries returns 0.0 (real "idle account" signal); None
    is reserved for "fetch errored / metric unavailable".
"""
import logging
from datetime import datetime, timedelta, timezone

LOG = logging.getLogger(__name__)

TIERS = ("Hot", "Cool", "Cold", "Archive")
INTERVAL_PT1H = "PT1H"

_READ_APIS = {"GetBlob", "GetBlobProperties", "GetBlobMetadata"}
_WRITE_APIS = {"PutBlob", "PutBlockList", "SetBlobTier", "SetBlobMetadata"}


def _empty_tiers():
    return {t: {"gb": 0.0, "blob_count": 0.0} for t in TIERS}


def _empty_breakdown():
    return {
        "tiers": _empty_tiers(),
        "account_totals": {
            "read_ops": 0.0,
            "write_ops": 0.0,
            "egress_gb": None,
        },
    }


def _timespan(days):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return (f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
            f"{end.strftime('%Y-%m-%dT%H:%M:%SZ')}")


def _normalize_tier(raw):
    if not raw:
        return ""
    r = raw.strip()
    for t in TIERS:
        if r.lower() == t.lower():
            return t
    return ""


def _capacity_probe(monitor_client, capacity_resource_uri, days, tiers_out):
    try:
        resp = monitor_client.metrics.list(
            resource_uri=capacity_resource_uri,
            timespan=_timespan(days),
            interval=INTERVAL_PT1H,
            metricnames="BlobCapacity,BlobCount",
            aggregation="Average",
            filter="Tier eq '*'",
        )
    except Exception as exc:
        LOG.debug("capacity probe failed for %s: %s", capacity_resource_uri, exc)
        return
    for m in (resp.value or []):
        mname = getattr(m, "name", None)
        mname_val = getattr(mname, "value", None) if mname is not None else None
        for ts in (getattr(m, "timeseries", None) or []):
            tier = ""
            for md in (getattr(ts, "metadatavalues", None) or []):
                key = getattr(getattr(md, "name", None), "value", None)
                if key and key.lower() == "tier":
                    tier = _normalize_tier(getattr(md, "value", "") or "")
            if not tier:
                continue
            latest = None
            for d in (getattr(ts, "data", None) or []):
                v = getattr(d, "average", None)
                if v is not None:
                    latest = float(v)
            if latest is None:
                continue
            slot = tiers_out.setdefault(tier, {"gb": 0.0, "blob_count": 0.0})
            if mname_val == "BlobCapacity":
                slot["gb"] = latest / (1024 ** 3)
            elif mname_val == "BlobCount":
                slot["blob_count"] = latest


def get_account_transactions(credential, subscription_id, account_arm, days=30):
    """Return account-level {read_ops, write_ops}. NO Tier dimension —
    Azure Monitor's Transactions metric does not expose Tier. Callers that
    want a per-tier split must use approximate_per_tier_transactions()."""
    out = {"read_ops": 0.0, "write_ops": 0.0}
    try:
        from azure.mgmt.monitor import MonitorManagementClient
    except Exception as exc:
        LOG.warning("azure.mgmt.monitor import failed: %s", exc)
        return out
    try:
        monitor = MonitorManagementClient(credential, subscription_id)
    except Exception as exc:
        LOG.warning("MonitorManagementClient init failed: %s", exc)
        return out
    try:
        resp = monitor.metrics.list(
            resource_uri=account_arm.rstrip("/"),
            timespan=_timespan(days),
            interval=INTERVAL_PT1H,
            metricnames="Transactions",
            aggregation="Total",
            filter="ApiName eq '*' and TransactionType eq '*'",
        )
    except Exception as exc:
        LOG.debug("transactions probe failed for %s: %s", account_arm, exc)
        return out
    for m in (resp.value or []):
        for ts in (getattr(m, "timeseries", None) or []):
            api = ""
            for md in (getattr(ts, "metadatavalues", None) or []):
                key = getattr(getattr(md, "name", None), "value", "") or ""
                val = getattr(md, "value", "") or ""
                if key.lower() == "apiname":
                    api = val
            total = 0.0
            for d in (getattr(ts, "data", None) or []):
                v = getattr(d, "total", None)
                if v is not None:
                    total += float(v)
            if total <= 0:
                continue
            if api in _READ_APIS:
                out["read_ops"] += total
            elif api in _WRITE_APIS:
                out["write_ops"] += total
    return out


def approximate_per_tier_transactions(account_totals, tier_capacity_share):
    """Allocate account-level read/write totals across tiers by capacity share.

    Explicit name + signature so callers can't be confused: there is NO
    real per-tier transactions metric on Azure; this is an explicit
    capacity-ratio approximation, used by the forecaster for the per-tier
    op savings term.

    `tier_capacity_share` is a {tier: float} mapping summing to <= 1.0.
    Returns {tier: {read_ops, write_ops}}.
    """
    read = float(account_totals.get("read_ops") or 0.0)
    write = float(account_totals.get("write_ops") or 0.0)
    out = {}
    for tier, share in (tier_capacity_share or {}).items():
        try:
            s = float(share)
        except (TypeError, ValueError):
            s = 0.0
        out[tier] = {"read_ops": read * s, "write_ops": write * s}
    return out


def get_egress_gb(credential, subscription_id, account_arm, days=30):
    """Return egress GB for the storage account over `days`.

    Returns 0.0 on a successful API call with empty/zero timeseries (real
    'idle account' signal). Returns None ONLY when the API call itself
    errored — callers treat None as 'metric unavailable, fall back'.
    """
    try:
        from azure.mgmt.monitor import MonitorManagementClient
    except Exception as exc:
        LOG.warning("azure.mgmt.monitor import failed: %s", exc)
        return None
    try:
        monitor = MonitorManagementClient(credential, subscription_id)
    except Exception as exc:
        LOG.warning("MonitorManagementClient init failed: %s", exc)
        return None
    try:
        resp = monitor.metrics.list(
            resource_uri=account_arm.rstrip("/"),
            timespan=_timespan(days),
            interval=INTERVAL_PT1H,
            metricnames="Egress",
            aggregation="Total",
        )
    except Exception as exc:
        LOG.debug("egress probe failed for %s: %s", account_arm, exc)
        return None
    total_bytes = 0.0
    samples = 0
    for m in (resp.value or []):
        for ts in (getattr(m, "timeseries", None) or []):
            for d in (getattr(ts, "data", None) or []):
                v = getattr(d, "total", None)
                if v is not None:
                    total_bytes += float(v)
                    samples += 1
    if samples == 0:
        return 0.0
    return total_bytes / (1024 ** 3)


def get_tier_breakdown(credential, subscription_id, account_arm, days=30):
    """Return {tiers: {tier: {gb, blob_count}}, account_totals: {read_ops,
    write_ops, egress_gb}}.

    Note: scope rewrite — the Tier-dimension capacity probe must run
    against `/blobServices/default`, NOT the bare account ARM, or the
    Tier dimension is unpublished and the response is empty.
    """
    out = _empty_breakdown()
    try:
        from azure.mgmt.monitor import MonitorManagementClient
    except Exception as exc:
        LOG.warning("azure.mgmt.monitor import failed: %s", exc)
        return out
    try:
        monitor = MonitorManagementClient(credential, subscription_id)
    except Exception as exc:
        LOG.warning("MonitorManagementClient init failed: %s", exc)
        return out

    account_uri = account_arm.rstrip("/")
    capacity_uri = f"{account_uri}/blobServices/default"

    _capacity_probe(monitor, capacity_uri, days, out["tiers"])
    if not out["tiers"]:
        # Surfaces likely Monitoring Reader RBAC gap or Tier-dim API drift.
        LOG.info("empty tier breakdown for %s — check SPN Monitoring Reader role",
                 account_arm)

    totals = get_account_transactions(
        credential, subscription_id, account_uri, days=days)
    out["account_totals"]["read_ops"] = totals.get("read_ops", 0.0)
    out["account_totals"]["write_ops"] = totals.get("write_ops", 0.0)
    out["account_totals"]["egress_gb"] = get_egress_gb(
        credential, subscription_id, account_uri, days=days)
    return out
