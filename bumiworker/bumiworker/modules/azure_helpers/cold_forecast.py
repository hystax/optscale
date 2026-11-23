"""Pure-Python forecast for Azure blob tier-move savings.

No SDK calls — kept pure-function so it is unit-testable. Caller supplies
already-fetched tier breakdown (metrics.get_tier_breakdown shape) and
prices (pricing.get_storage_prices shape) plus optional payg/effective
storage rates from reservations.get_effective_storage_rate.
"""
from typing import Any, Dict, List, Optional

from bumiworker.bumiworker.modules.azure_helpers.cold_forecast_confidence import (
    Confidence, build_confidence, confidence_at_least,
)

TIER_ORDER = ("Hot", "Cool", "Cold", "Archive")

PAIRS = (("Hot", "Cold"), ("Cool", "Cold"))

# Per-pair gates. Cool->Cold uses stricter cuts because the storage delta
# is small (~$0.0064/GB-mo) and the breakeven read intensity is tight,
# inflating false-positive risk; Hot->Cold has a ~5x larger delta so a
# lower confidence floor is acceptable.
PAIR_THRESHOLDS = {
    ("Hot", "Cold"):  {"min_gb": 100, "min_saving": 1.0,
                       "min_confidence": Confidence.MEDIUM},
    ("Cool", "Cold"): {"min_gb": 500, "min_saving": 5.0,
                       "min_confidence": Confidence.HIGH},
}


def _safe_div(num, den):
    return (num / den) if den else 0.0


def _avg_blob_size_gb(gb, blob_count):
    return _safe_div(gb, blob_count) if blob_count > 0 else 0.0


def compute_tier_share(tiers, source):
    """Capacity-ratio share for `source` tier vs total across all tiers."""
    gb_total = 0.0
    for v in tiers.values():
        try:
            gb_total += float((v or {}).get("gb") or 0.0)
        except (TypeError, ValueError):
            continue
    src = tiers.get(source) or {}
    try:
        gb_src = float(src.get("gb") or 0.0)
    except (TypeError, ValueError):
        gb_src = 0.0
    return _safe_div(gb_src, gb_total)


def approximate_per_tier_transactions(account_totals, tier_capacity_share):
    """Allocate account-level read/write totals across tiers by capacity share.

    Reproduces `metrics.approximate_per_tier_transactions()` shape so
    forecast callers can stay pure-Python without importing the SDK-bearing
    metrics module. Tier-dim does not exist in Azure for Transactions so
    capacity-share is the only available approximation.
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


def forecast_tier_move(tier_data: Dict[str, Any],
                       prices: Dict[str, Dict[str, float]],
                       source: str, target: str,
                       days: int = 30,
                       payg_rate: Optional[float] = None,
                       effective_rate: Optional[float] = None) -> Dict[str, Any]:
    """Forecast monthly $ savings for moving `source` tier capacity to `target`.

    Returns the forecast row dict including confidence, gb_moved, signal_used,
    notes, and a saving_breakdown when payg_rate vs effective_rate diverge.
    """
    notes: List[str] = []
    tiers = (tier_data or {}).get("tiers") or {}
    account_totals = (tier_data or {}).get("account_totals") or {}
    src = tiers.get(source) or {}
    tgt_prices = prices.get(target)
    src_prices = prices.get(source)

    gb = float(src.get("gb") or 0.0)
    blob_count = float(src.get("blob_count") or 0.0)
    share = compute_tier_share(tiers, source)
    acct_read = float(account_totals.get("read_ops") or 0.0)
    acct_write = float(account_totals.get("write_ops") or 0.0)

    month_scale = (30.0 / float(days)) if days else 1.0
    read_ops = acct_read * share * month_scale
    write_ops = acct_write * share * month_scale

    if not src_prices or not tgt_prices:
        notes.append("cold_unsupported_in_region" if target == "Cold"
                     else "target_unsupported_in_region")
        return {
            "monthly_savings_usd": 0.0,
            "gb_moved": gb,
            "breakeven_read_intensity": 0.0,
            "current_read_intensity": _safe_div(read_ops, gb),
            "confidence": Confidence.LOW,
            "notes": notes,
            "signal_used": "fallback",
            "saving_breakdown": {"payg": 0.0, "effective": 0.0},
            "reservation_applied": False,
            "source_tier": source,
            "target_tier": target,
        }

    # Effective-rate adjustment: when the deployer holds a capacity
    # reservation against the SOURCE tier, the source $/GB-mo rate they
    # actually pay is the (lower) effective rate, which shrinks the
    # storage delta. Emit both numbers so the UI shows the methodology
    # change auditable.
    payg_src_rate = float(src_prices["storage_gb_month"])
    if payg_rate is not None:
        # Caller passed an explicit payg override (e.g. retail-prices
        # source tier rate fetched outside this helper). Trust caller.
        payg_src_rate = float(payg_rate)
    eff_src_rate = float(effective_rate) if effective_rate is not None else payg_src_rate
    reservation_applied = effective_rate is not None and eff_src_rate != payg_src_rate

    storage_delta_payg = payg_src_rate - tgt_prices["storage_gb_month"]
    storage_delta_eff = eff_src_rate - tgt_prices["storage_gb_month"]

    read_delta_per_10k = src_prices["read_op_per_10k"] - tgt_prices["read_op_per_10k"]
    write_delta_per_10k = src_prices["write_op_per_10k"] - tgt_prices["write_op_per_10k"]
    retrieval_delta = tgt_prices["retrieval_gb"] - src_prices["retrieval_gb"]

    avg_blob_gb = _avg_blob_size_gb(gb, blob_count)

    egress_total = account_totals.get("egress_gb")
    egress_signal_used = False
    egress_total_f = None
    if egress_total is not None:
        try:
            egress_total_f = float(egress_total)
        except (TypeError, ValueError):
            egress_total_f = None

    if egress_total_f is not None:
        egress_src_gb = egress_total_f * share * month_scale
        notes.append("egress_signal_used")
        egress_signal_used = True
        signal_used = "egress"
    else:
        capped_avg_blob_gb = min(avg_blob_gb, 1.0) if avg_blob_gb > 0 else 0.0
        egress_src_gb = read_ops * capped_avg_blob_gb
        notes.append("egress_unavailable_fallback")
        signal_used = "proxy"

    retrieval_term = egress_src_gb * retrieval_delta

    def _delta(storage_delta):
        return (
            gb * storage_delta
            + read_ops * read_delta_per_10k / 10000.0
            + write_ops * write_delta_per_10k / 10000.0
            - retrieval_term
        )

    delta_payg = _delta(storage_delta_payg)
    delta_eff = _delta(storage_delta_eff)
    delta_chosen = delta_eff if reservation_applied else delta_payg

    per_op = (read_delta_per_10k / 10000.0) - (avg_blob_gb * retrieval_delta)
    if per_op < 0 and gb > 0:
        write_term = write_ops * write_delta_per_10k / 10000.0
        breakeven_reads = -(gb * storage_delta_payg + write_term) / per_op
        breakeven_intensity = _safe_div(breakeven_reads, gb)
    else:
        breakeven_intensity = 0.0

    current_intensity = _safe_div(read_ops, gb)

    delta_rounded = round(delta_chosen, 2)
    confidence = build_confidence(
        egress_signal_usable=egress_signal_used,
        savings_usd=delta_rounded,
        gb=gb,
        share_of_account=share,
        reason_list=notes,
    )

    if blob_count > 0 and gb > 0:
        notes.append("mixed_access_account_averaged")

    return {
        "monthly_savings_usd": round(delta_chosen, 2),
        "gb_moved": round(gb, 2),
        "breakeven_read_intensity": round(breakeven_intensity, 4),
        "current_read_intensity": round(current_intensity, 4),
        "confidence": confidence,
        "notes": notes,
        "signal_used": signal_used,
        "monthly_reads": int(read_ops),
        "monthly_writes": int(write_ops),
        "egress_gb": round(egress_src_gb, 2),
        "payg_storage_rate": round(payg_src_rate, 6),
        "effective_storage_rate": round(eff_src_rate, 6),
        "reservation_applied": bool(reservation_applied),
        "saving_breakdown": {
            "payg": round(delta_payg, 2),
            "effective": round(delta_eff, 2),
        },
        "source_tier": source,
        "target_tier": target,
    }


def recommend(tier_breakdown, prices, days=30, thresholds=None,
              payg_rate=None, effective_rate=None):
    """Iterate Hot->Cold and Cool->Cold; apply per-pair gates."""
    thresholds = thresholds or PAIR_THRESHOLDS
    candidates = []
    for source, target in PAIRS:
        f = forecast_tier_move(
            tier_breakdown, prices, source, target, days=days,
            payg_rate=payg_rate, effective_rate=effective_rate,
        )
        candidates.append(f)

    filtered = []
    for c in candidates:
        thr = thresholds.get((c["source_tier"], c["target_tier"]))
        if not thr:
            continue
        # inclusive lower bound — plan §2.6.2
        if c["monthly_savings_usd"] < thr["min_saving"]:
            continue
        if c["gb_moved"] < thr["min_gb"]:
            continue
        if not confidence_at_least(c["confidence"], thr["min_confidence"]):
            continue
        filtered.append(c)
    filtered.sort(key=lambda c: c["monthly_savings_usd"], reverse=True)
    return filtered
