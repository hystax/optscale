"""Transitional Azure Advisor feed reader (host-snapshot mode).

TRANSITIONAL: replaced in Phase 3 by live `azure-mgmt-advisor` per-category
modules under `recommendations/azure_advisor_*.py`. Kept for parity during
Phase B parallel run; remove once live Advisor is verified for one full
week against the host-side snapshot.

Snapshot file is produced on the host by /opt/optscale-advisor/fetch_advisor.py
and shipped into the bumiworker pod under
`bumiworker/bumiworker/modules/recommendations/_hystax_upstream/...`.
"""
import json
import logging
import os
from typing import Any, Dict, Iterable, List, Optional

LOG = logging.getLogger(__name__)

POD_SNAPSHOT_PATH = (
    "/usr/src/app/bumiworker/bumiworker/modules/recommendations/"
    "_hystax_upstream/azure_advisor_snapshot.json"
)
HOST_SNAPSHOT_PATH = "/opt/optscale-advisor/snapshot.json"


def _candidate_paths():
    env = os.environ.get("AZURE_ADVISOR_SNAPSHOT")
    paths = []
    if env:
        paths.append(env)
    paths.extend([POD_SNAPSHOT_PATH, HOST_SNAPSHOT_PATH])
    return paths


def load_snapshot(path: Optional[str] = None) -> Dict[str, Any]:
    """Return parsed snapshot dict {generated_at, count, recommendations}.

    Empty snapshot on any failure — callers treat as 'no Advisor data'
    rather than raising, so a missing snapshot can never break upstream.
    """
    candidates = [path] if path else _candidate_paths()
    for p in candidates:
        if not p:
            continue
        try:
            with open(p, "r") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and "recommendations" in data:
                return data
            if isinstance(data, list):
                return {"generated_at": "", "count": len(data),
                        "recommendations": data}
        except FileNotFoundError:
            continue
        except Exception as exc:
            LOG.warning("advisor snapshot at %s unreadable: %s", p, exc)
            continue
    return {"generated_at": "", "count": 0, "recommendations": []}


def for_organization(org_id, category=None, recommendation_type_id=None,
                     snapshot=None):
    snap = snapshot if snapshot is not None else load_snapshot()
    recs = snap.get("recommendations", []) or []
    out = []
    for r in recs:
        if r.get("organization_id") != org_id:
            continue
        if category and r.get("category") != category:
            continue
        if (recommendation_type_id
                and r.get("recommendation_type_id") != recommendation_type_id):
            continue
        out.append(r)
    return out


def group_by_category(recs: Iterable[Dict[str, Any]]):
    out: Dict[str, List[Dict[str, Any]]] = {}
    for r in recs:
        out.setdefault(r.get("category", ""), []).append(r)
    return out
