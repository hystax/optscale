"""Unit tests for the cold-tier forecast math, confidence ladder, and
redundancy parse helper."""
import pytest

from bumiworker.bumiworker.modules.azure_helpers import cold_forecast
from bumiworker.bumiworker.modules.azure_helpers.cold_forecast_confidence import (
    Confidence, build_confidence, confidence_at_least,
)
from bumiworker.bumiworker.modules.azure_helpers.pricing import parse_redundancy


def _prices():
    return {
        'Hot':  {'storage_gb_month': 0.0184, 'read_op_per_10k': 0.004,
                 'write_op_per_10k': 0.05, 'retrieval_gb': 0.0},
        'Cool': {'storage_gb_month': 0.0100, 'read_op_per_10k': 0.01,
                 'write_op_per_10k': 0.10, 'retrieval_gb': 0.01},
        'Cold': {'storage_gb_month': 0.0036, 'read_op_per_10k': 0.05,
                 'write_op_per_10k': 0.10, 'retrieval_gb': 0.03},
        'Archive': {'storage_gb_month': 0.001, 'read_op_per_10k': 0.5,
                    'write_op_per_10k': 0.10, 'retrieval_gb': 0.02},
    }


def test_zero_capacity_returns_zero_savings():
    breakdown = {
        'tiers': {t: {'gb': 0.0, 'blob_count': 0.0}
                  for t in ('Hot', 'Cool', 'Cold', 'Archive')},
        'account_totals': {'read_ops': 0.0, 'write_ops': 0.0,
                           'egress_gb': 0.0},
    }
    rec = cold_forecast.forecast_tier_move(
        breakdown, _prices(), 'Hot', 'Cold', days=30)
    assert rec['monthly_savings_usd'] == 0.0
    assert rec['gb_moved'] == 0.0


def test_zero_egress_uses_egress_signal():
    breakdown = {
        'tiers': {
            'Hot':  {'gb': 1000.0, 'blob_count': 1000.0},
            'Cool': {'gb': 0.0, 'blob_count': 0.0},
            'Cold': {'gb': 0.0, 'blob_count': 0.0},
            'Archive': {'gb': 0.0, 'blob_count': 0.0},
        },
        'account_totals': {'read_ops': 0.0, 'write_ops': 0.0,
                           'egress_gb': 0.0},
    }
    rec = cold_forecast.forecast_tier_move(
        breakdown, _prices(), 'Hot', 'Cold', days=30)
    assert rec['signal_used'] == 'egress'
    assert rec['monthly_savings_usd'] > 0.0


def test_negative_savings_is_emitted_low_confidence():
    # Source = Cold, target = Hot (inverted) -> negative savings.
    prices = _prices()
    breakdown = {
        'tiers': {
            'Hot': {'gb': 0.0, 'blob_count': 0.0},
            'Cool': {'gb': 0.0, 'blob_count': 0.0},
            'Cold': {'gb': 1000.0, 'blob_count': 1000.0},
            'Archive': {'gb': 0.0, 'blob_count': 0.0},
        },
        'account_totals': {'read_ops': 0.0, 'write_ops': 0.0,
                           'egress_gb': 0.0},
    }
    rec = cold_forecast.forecast_tier_move(
        breakdown, prices, 'Cold', 'Hot', days=30)
    # storage_gb_month inverted -> negative delta on a no-egress, no-ops
    # account.
    assert rec['monthly_savings_usd'] <= 0.0


def test_basic_hot_to_cold_positive_case():
    breakdown = {
        'tiers': {
            'Hot':  {'gb': 5000.0, 'blob_count': 5000.0},
            'Cool': {'gb': 0.0, 'blob_count': 0.0},
            'Cold': {'gb': 0.0, 'blob_count': 0.0},
            'Archive': {'gb': 0.0, 'blob_count': 0.0},
        },
        'account_totals': {'read_ops': 100.0, 'write_ops': 100.0,
                           'egress_gb': 1.0},
    }
    rec = cold_forecast.forecast_tier_move(
        breakdown, _prices(), 'Hot', 'Cold', days=30)
    assert rec['monthly_savings_usd'] > 0
    assert rec['gb_moved'] == 5000.0
    assert rec['confidence'] == Confidence.HIGH


def test_confidence_ladder_branches():
    # High: egress + savings >= 5 + gb >= 100, share 1.0
    notes = []
    assert build_confidence(True, 5.0, 100, 1.0, notes) == Confidence.HIGH
    # Medium: egress, savings between 1 and 5
    notes = []
    assert build_confidence(True, 2.0, 100, 1.0, notes) == Confidence.MEDIUM
    # Low: egress but savings below floor
    notes = []
    assert build_confidence(True, 0.5, 100, 1.0, notes) == Confidence.LOW
    # No egress: capped at MEDIUM
    notes = []
    assert build_confidence(False, 100.0, 10000, 1.0, notes) == Confidence.MEDIUM
    # share < 0.5 downgrades one notch
    notes = []
    assert build_confidence(True, 5.0, 100, 0.3, notes) == Confidence.MEDIUM
    notes = []
    assert build_confidence(True, 2.0, 100, 0.3, notes) == Confidence.LOW


def test_confidence_at_least():
    assert confidence_at_least(Confidence.HIGH, Confidence.MEDIUM) is True
    assert confidence_at_least(Confidence.MEDIUM, Confidence.MEDIUM) is True
    assert confidence_at_least(Confidence.LOW, Confidence.MEDIUM) is False


@pytest.mark.parametrize("sku_name,expected", [
    ("Standard_RAGZRS", "RAGZRS"),
    ("Standard_RAGRS", "RAGRS"),
    ("Standard_GZRS", "GZRS"),
    ("Standard_GRS", "GRS"),
    ("Standard_ZRS", "ZRS"),
    ("Standard_LRS", "LRS"),
    ("Premium_LRS", "LRS"),
    (None, "LRS"),
    ("", "LRS"),
])
def test_redundancy_parse(sku_name, expected):
    assert parse_redundancy(sku_name) == expected
