# Agent guidelines for OptScale

This file gives review agents (Codex, Claude Code, etc.) context about the codebase so they don't re-flag intentional patterns or miss class-level conventions.

## Review guidelines

### Module identity (`unique_record_keys`)

Recommendation modules under `bumiworker/bumiworker/modules/recommendations/` that can emit multiple rows per cloud resource MUST override the base class `unique_record_keys` property to include the discriminating field (e.g., tier pair, severity, time window). The override appears as a class-level `@property` returning a tuple — typical examples:

- `azure_cold_tier_candidates.py` line 49: returns `('cloud_account_id', 'cloud_resource_id', 'current_tier', 'target_tier')` — discriminates Hot→Cold vs Cool→Cold rows for the same storage account.
- The matching archive module under `bumiworker/bumiworker/modules/archive/` exposes the SAME tuple at its corresponding line.

When you see the row-emission loop and your first instinct is to flag "missing `unique_record_keys`", scan the class header (typically lines 40-60) for an `@property` with name `unique_record_keys` BEFORE flagging. Do not re-flag if the override is present and includes the discriminating fields the loop emits.

### Helper scope filtering

The `bumiworker/bumiworker/modules/azure_helpers/reservations.py` helper accepts both legacy `applied_scopes` and newer `applied_scope_properties.subscription_id` payload shapes (lines ~204-215 in current head). Single-scope reservations narrower than the subscription (e.g., resource-group scoped) are conservatively skipped because the helper has no resource-RG context. This is intentional — under-discount is safer than phantom over-savings.

### Archive module phantom fields

When an archive module reads a `meta.<field>` for state classification (e.g., RECOMMENDATION_APPLIED detection), the field MUST have a writer somewhere in `tools/cloud_adapter/clouds/*.py` or `rest_api/restapi/handlers/*` for the relevant cloud. If no writer exists, the module currently uses a conservative IRRELEVANT fallthrough plus a TODO. Do not flag the IRRELEVANT branch as "should be APPLIED" — the gap is documented and intentional pending discovery-layer changes.

## Conventions

- New recommendation modules: cloud-agnostic registration (no AWS/Hystax-specific shortcuts).
- Sibling-resource lookups: filter `employee_id != null AND pool_id != null`, sort `[("created_at", 1), ("_id", 1)]`. Null leaks crash the frontend Filters component organisation-wide.
- Azure SDK matrix: track-1 (storage/compute/monitor) uses `msrestazure.ServicePrincipalCredentials`; track-2 (network/identity) uses `azure.identity.ClientSecretCredential`. Don't cross.
- Recommendation tile: bumiworker module filename MUST equal `type` field on the ngui tile class.
- Recommendation tile dual-registration: BOTH `allRecommendations.ts` AND `useOptscaleRecommendations.ts`.
- Recommendation tile title: plain text only — `Cards.tsx` renders without a `values` prop.
