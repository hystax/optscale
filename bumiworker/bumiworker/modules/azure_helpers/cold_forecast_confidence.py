"""Standardised confidence ladder for native Azure modules.

Every Azure module emits the same 'high' / 'medium' / 'low' string values
so the ngui tile can render confidence badges uniformly.
"""


class Confidence(object):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'


_RANK = {Confidence.LOW: 0, Confidence.MEDIUM: 1, Confidence.HIGH: 2}
_DOWNGRADE = {
    Confidence.HIGH: Confidence.MEDIUM,
    Confidence.MEDIUM: Confidence.LOW,
    Confidence.LOW: Confidence.LOW,
}


def confidence_at_least(actual, threshold):
    return _RANK.get(actual, -1) >= _RANK.get(threshold, 99)


def build_confidence(egress_signal_usable, savings_usd, gb,
                     share_of_account, reason_list):
    """Branch the cold-tier confidence ladder.

      with egress AND savings >= $5 AND gb >= 100 -> HIGH
      with egress AND savings >= $1               -> MEDIUM
      with egress AND below savings floor         -> LOW
      no egress signal                            -> capped at MEDIUM
      share_of_account < 0.5                      -> downgrade one notch
    """
    if egress_signal_usable:
        if savings_usd >= 5.0 and gb >= 100:
            confidence = Confidence.HIGH
        elif savings_usd >= 1.0:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW
    else:
        # No real egress data -> capped at MEDIUM, regardless of magnitude.
        confidence = Confidence.MEDIUM
        reason_list.append('confidence_capped_no_egress')

    if share_of_account < 0.5:
        confidence = _DOWNGRADE.get(confidence, confidence)
        reason_list.append(
            'mixed_account_share_%d%%' % int(round(share_of_account * 100)))

    return confidence
