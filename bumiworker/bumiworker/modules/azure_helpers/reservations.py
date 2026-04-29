"""Azure capacity-reservation rate lookup for blob storage.

Uses `azure.identity.ClientSecretCredential` +
`azure.mgmt.reservations.AzureReservationAPI`. Replaces the originally-
planned `azure-mgmt-costmanagement` reservation surface (no synchronous
list API in 4.0.1 — see plan § 9 decision #9).

Two-hop flow:
  (1) AzureReservationAPI.reservation.list_all() returns active blob
      reservations on the tenant. The reservation object carries no
      $/GB-month field; only sku name + scope + provisioning state.
  (2) Public Azure Retail Prices API (no auth) resolves the SKU to a
      reservation unitPrice; we divide by capacity_gb / months_in_term to
      get $/GB-month.

RBAC: SPN must hold the built-in `Reservations Reader` role on the tenant
(or the specific reservation orders) for the list_all call to return
results. Without it the call yields a 403 AuthorizationFailed; this is a
silent under-discount (safe), never an over-discount.

The whole helper is wrapped to NEVER throw — empty list, 403, schema
drift, network errors all degrade silently to None so the caller falls
back to the PAYG meter.
"""
import json
import logging
import re
import time
import urllib.parse
import urllib.request
from typing import Optional

LOG = logging.getLogger(__name__)

RETAIL_PRICES_URL = "https://prices.azure.com/api/retail/prices"
CACHE_TTL_SECS = 24 * 3600
GB_PER_TIB = 1024
GB_PER_PIB = 1024 * 1024

# Microsoft has changed this naming format in the past; defensive regex
# tested against the documented current shape:
#   Blob_Storage_Reserved_Capacity_<redundancy>_<tier>_<size>
# Allowed redundancy tokens: RA-GZRS, RAGZRS, RA-GRS, RAGRS, GZRS, GRS,
#   ZRS, LRS. Tier in {Hot, Cool, Archive}. Size in {100TB, 1PB}.
SKU_PATTERN = re.compile(
    r"^Blob_Storage_Reserved_Capacity_"
    r"(?P<redundancy>RA-?GZRS|RA-?GRS|GZRS|GRS|ZRS|LRS)_"
    r"(?P<tier>Hot|Cool|Archive)_"
    r"(?P<size>100TB|1PB)$"
)

_CACHE = {}


def _capacity_gb(size_token):
    if size_token == "100TB":
        return 100 * GB_PER_TIB
    if size_token == "1PB":
        return 1 * GB_PER_PIB
    return None


def _months_in_term(term_str):
    if not term_str:
        return None
    s = term_str.lower().replace(" ", "")
    if s.startswith("1year") or s == "p1y":
        return 12
    if s.startswith("3year") or s == "p3y":
        return 36
    return None


def _http_get_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_retail_reservation_rate(region, sku_name, term):
    """Resolve a reservation SKU to $/GB-month via Retail Prices.

    Public endpoint, no auth. Returns None on any failure.
    """
    flt = (
        f"serviceName eq 'Storage' and priceType eq 'Reservation' "
        f"and armRegionName eq '{region}' and skuName eq '{sku_name}' "
        f"and reservationTerm eq '{term}'"
    )
    params = {"$filter": flt, "api-version": "2023-01-01-preview"}
    url = RETAIL_PRICES_URL + "?" + urllib.parse.urlencode(params)
    try:
        data = _http_get_json(url)
    except Exception as exc:
        LOG.debug("retail reservation fetch failed: %s", exc)
        return None
    items = data.get("Items") or []
    if not items:
        return None
    # Parse SKU to recover capacity tier (100TB or 1PB) for the divisor.
    m = SKU_PATTERN.match(sku_name)
    if not m:
        return None
    capacity_gb = _capacity_gb(m.group("size"))
    months = _months_in_term(term)
    if not capacity_gb or not months:
        return None
    for it in items:
        try:
            unit_price = float(it.get("unitPrice") or 0.0)
        except (TypeError, ValueError):
            continue
        if unit_price <= 0:
            continue
        return unit_price / capacity_gb / months
    return None


def get_effective_storage_rate(credential, subscription_id, region,
                               redundancy, tier) -> Optional[float]:
    """Return the per-GB-month effective storage rate for an active blob
    capacity reservation matching `(region, redundancy, tier)`, or None
    when no matching reservation is found / the SPN lacks the
    `Reservations Reader` role / any other failure.

    NEVER raises. Failure modes are all under-discount (safe); we never
    over-discount the forecast.
    """
    # cache key is (region, redundancy, tier) not (region, sku, term):
    # helper resolves a single $/GB-month per (region, redundancy, tier) regardless of
    # reservation size (100TB vs 1PB SKUs share the rate at GB-month granularity).
    cache_key = ((region or "").lower(), (redundancy or "").upper(), tier)
    now = time.monotonic()
    cached = _CACHE.get(cache_key)
    if cached and (now - cached[0]) < CACHE_TTL_SECS:
        return cached[1]

    rate: Optional[float] = None
    try:
        from azure.mgmt.reservations import AzureReservationAPI
        from azure.core.exceptions import HttpResponseError  # noqa: F401
    except Exception as exc:
        LOG.debug("azure-mgmt-reservations import failed: %s", exc)
        _CACHE[cache_key] = (now, None)
        return None

    try:
        client = AzureReservationAPI(credential, subscription_id)
    except Exception as exc:
        LOG.debug("AzureReservationAPI init failed: %s", exc)
        _CACHE[cache_key] = (now, None)
        return None

    try:
        reservations = client.reservation.list_all(
            filter=("properties/reservedResourceType eq 'BlockBlob' and "
                    "properties/provisioningState eq 'Succeeded'"),
        )
    except Exception as exc:
        LOG.debug("reservation list_all failed: %s", exc)
        _CACHE[cache_key] = (now, None)
        return None

    norm_red = (redundancy or "").upper().replace("-", "")
    try:
        for r in reservations:
            sku = getattr(getattr(r, "sku", None), "name", None) or ""
            props = getattr(r, "properties", None)
            term = getattr(props, "term", None) if props else None
            # `applied_scopes` is a list of subscription IDs; we don't
            # filter on it here since list_all is already tenant-wide.
            m = SKU_PATTERN.match(sku)
            if not m:
                continue
            r_red = m.group("redundancy").upper().replace("-", "")
            r_tier = m.group("tier")
            if r_red != norm_red or r_tier != tier:
                continue
            term_str = term or "1 Year"
            rate = _fetch_retail_reservation_rate(region, sku, term_str)
            if rate is not None:
                break
    except Exception as exc:
        LOG.debug("reservation iteration failed: %s", exc)
        rate = None

    _CACHE[cache_key] = (now, rate)
    return rate
