"""Azure Retail Prices API client for blob storage tiers.

Pure stdlib (urllib) so no extra pip deps. 24h in-memory cache keyed by
(region, redundancy). Public surface used by the cold-tier forecaster:
    get_storage_prices(region, redundancy) -> per-tier rate dict
    get_egress_rate(region) -> Decimal $/GB
"""
import json
import logging
import time
import urllib.parse
import urllib.request
from decimal import Decimal
from typing import Dict, Optional, Tuple

LOG = logging.getLogger(__name__)

RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"
TIERS = ("Hot", "Cool", "Cold", "Archive")
CACHE_TTL_SECS = 24 * 3600

# Longest-prefix-first redundancy parse. Order matters: naive substring
# matching lets 'GZRS' match inside 'RAGZRS' and produces the wrong
# pricing axis. Iterate longest -> shortest, first hit wins.
REDUNDANCY_PREFIXES = ("RAGZRS", "RAGRS", "GZRS", "GRS", "ZRS", "LRS")

_CACHE: Dict[Tuple[str, str], Tuple[float, Dict]] = {}
_EGRESS_CACHE: Dict[str, Tuple[float, Decimal]] = {}


def parse_redundancy(sku_name):
    """Pull redundancy token out of an Azure storage SKU name.

    Defaults to 'LRS' when nothing matches.
    """
    if not sku_name:
        return "LRS"
    sn = str(sku_name).upper()
    for r in REDUNDANCY_PREFIXES:
        if r in sn:
            return r
    return "LRS"


def _http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _classify_meter(sku_name, meter_name, redundancy):
    sku = (sku_name or "").strip()
    meter = (meter_name or "").strip()
    if not sku or not meter:
        return None
    sku_parts = sku.split()
    if len(sku_parts) < 2:
        return None
    tier = sku_parts[0]
    sku_red = sku_parts[1]
    if tier not in TIERS:
        return None
    if sku_red.upper() != redundancy.upper():
        return None
    ml = meter.lower()
    if "data stored" in ml:
        return tier, "storage_gb_month"
    if "read operations" in ml:
        return tier, "read_op_per_10k"
    if "write operations" in ml:
        return tier, "write_op_per_10k"
    if "data retrieval" in ml:
        return tier, "retrieval_gb"
    return None


def _fetch_storage(region, redundancy):
    flt = (
        f"serviceName eq 'Storage' and armRegionName eq '{region}' "
        f"and priceType eq 'Consumption'"
    )
    params = {"$filter": flt, "api-version": "2023-01-01-preview"}
    url = RETAIL_PRICES_URL + "?" + urllib.parse.urlencode(params)
    out: Dict[str, Dict[str, float]] = {t: {} for t in TIERS}
    pages = 0
    max_pages = 50
    while url and pages < max_pages:
        try:
            data = _http_get_json(url)
        except Exception as exc:
            LOG.warning("retail prices fetch failed (%s): %s", url, exc)
            break
        for it in (data.get("Items") or []):
            cls = _classify_meter(
                it.get("skuName") or "",
                it.get("meterName") or "",
                redundancy,
            )
            if not cls:
                continue
            tier, kind = cls
            try:
                price = float(it.get("retailPrice") or 0.0)
            except (TypeError, ValueError):
                continue
            out[tier].setdefault(kind, price)
        url = data.get("NextPageLink")
        pages += 1

    result: Dict[str, Dict[str, float]] = {}
    for tier in TIERS:
        d = out.get(tier) or {}
        if not d:
            LOG.info("retail prices: tier %s missing for region=%s redundancy=%s",
                     tier, region, redundancy)
            continue
        result[tier] = {
            "storage_gb_month": d.get("storage_gb_month", 0.0),
            "read_op_per_10k": d.get("read_op_per_10k", 0.0),
            "write_op_per_10k": d.get("write_op_per_10k", 0.0),
            "retrieval_gb": d.get("retrieval_gb", 0.0),
        }
    return result


def get_storage_prices(region, redundancy="LRS"):
    """Return {tier: {storage_gb_month, read_op_per_10k, write_op_per_10k,
    retrieval_gb}} for the given region+redundancy. 24h cached."""
    key = ((region or "").lower(), (redundancy or "LRS").upper())
    now = time.monotonic()
    cached = _CACHE.get(key)
    if cached and (now - cached[0]) < CACHE_TTL_SECS:
        return cached[1]
    prices = _fetch_storage(region, redundancy)
    _CACHE[key] = (now, prices)
    return prices


def _fetch_egress(region) -> Optional[Decimal]:
    flt = (
        f"serviceName eq 'Bandwidth' and armRegionName eq '{region}' "
        f"and priceType eq 'Consumption'"
    )
    params = {"$filter": flt, "api-version": "2023-01-01-preview"}
    url = RETAIL_PRICES_URL + "?" + urllib.parse.urlencode(params)
    try:
        data = _http_get_json(url)
    except Exception as exc:
        LOG.warning("retail egress fetch failed: %s", exc)
        return None
    for it in (data.get("Items") or []):
        meter = (it.get("meterName") or "").lower()
        if "data transfer out" in meter or "egress" in meter:
            try:
                return Decimal(str(it.get("retailPrice") or 0))
            except Exception:
                continue
    return None


def get_egress_rate(region) -> Decimal:
    """Return $/GB egress rate as Decimal (0 fallback). 24h cached."""
    key = (region or "").lower()
    now = time.monotonic()
    cached = _EGRESS_CACHE.get(key)
    if cached and (now - cached[0]) < CACHE_TTL_SECS:
        return cached[1]
    rate = _fetch_egress(region) or Decimal("0")
    _EGRESS_CACHE[key] = (now, rate)
    return rate
