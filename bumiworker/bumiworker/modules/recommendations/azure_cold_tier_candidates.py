"""Native Azure cold-tier candidate forecaster.

First-class Azure module — does NOT subclass any AWS-named upstream class.
Sits beside the AWS s3_intelligent_tiering module; both run for their own
cloud_type. Replaces the overlay wrapper-override pattern under
/opt/optscale-azure-aliases/wrappers/s3_intelligent_tiering.py.

All Azure SDK calls go through the azure_helpers package; this module
itself has no direct SDK imports. See module-level helpers:
  azure_helpers.credentials       — SPN cred extraction + ClientSecretCredential factory
  azure_helpers.pricing           — Retail Prices for storage tiers
  azure_helpers.metrics           — Azure Monitor probes
  azure_helpers.cold_forecast     — pure forecast math + thresholds
  azure_helpers.reservations      — reservation rate lookup
  azure_helpers.resource_resolution — null-owner-safe sibling lookup
"""
import logging
from collections import OrderedDict

from bumiworker.bumiworker.modules.base import ModuleBase
from bumiworker.bumiworker.modules.azure_helpers import credentials as creds_helper
from bumiworker.bumiworker.modules.azure_helpers import pricing as pricing_helper
from bumiworker.bumiworker.modules.azure_helpers import metrics as metrics_helper
from bumiworker.bumiworker.modules.azure_helpers import cold_forecast
from bumiworker.bumiworker.modules.azure_helpers.cold_forecast_confidence import (
    confidence_at_least,
)
from bumiworker.bumiworker.modules.azure_helpers import reservations as reservations_helper
from bumiworker.bumiworker.modules.azure_helpers.resource_resolution import (
    resolve_or_insert_resource,
)

LOG = logging.getLogger(__name__)

DEFAULT_DAYS_THRESHOLD = 30
SUPPORTED_KINDS = {'StorageV2', 'BlobStorage'}
RESOURCE_TYPE = 'Storage Account'
CREATED_BY = 'azure_cold_tier_candidates'


class AzureColdTierCandidates(ModuleBase):
    SUPPORTED_CLOUD_TYPES = ['azure_cnr']

    # A single storage account can qualify under multiple tier-pair transitions
    # (e.g. Hot->Cold and Cool->Cold) within one run.  Including current_tier
    # and target_tier in the key prevents the two rows from colliding in
    # detection/archive/dismissal flows, which key rows by unique_record_keys.
    @property
    def unique_record_keys(self):
        return 'cloud_account_id', 'cloud_resource_id', 'current_tier', 'target_tier',

    PAIR_THRESHOLDS = {
        ('Hot', 'Cold'):  {'min_gb': 100, 'min_saving': 1.0,
                           'min_confidence': 'medium'},
        ('Cool', 'Cold'): {'min_gb': 500, 'min_saving': 5.0,
                           'min_confidence': 'high'},
    }

    def __init__(self, organization_id, config_client, created_at):
        super().__init__(organization_id, config_client, created_at)
        self.option_ordered_map = OrderedDict({
            'days_threshold': {'default': DEFAULT_DAYS_THRESHOLD},
            'excluded_pools': {
                'default': {},
                'clean_func': self.clean_excluded_pools,
            },
            'skip_cloud_accounts': {'default': []},
        })

    def _account_should_skip(self, account):
        sku = getattr(account, 'sku', None)
        sku_tier = getattr(sku, 'tier', None) if sku else None
        kind = getattr(account, 'kind', None)
        if sku_tier and str(sku_tier).lower() == 'premium':
            return 'premium_sku'
        # Smart-tier (access-tier inference) hard skip.
        access_tier_inference = getattr(
            account, 'is_access_tier_inferred', None)
        if access_tier_inference is True:
            return 'smart_tier_enabled'
        if kind not in SUPPORTED_KINDS:
            return 'unsupported_kind_%s' % kind
        return None

    def _row_for(self, cand_rec, account, ca, region, cloud_account_id,
                 detected_at, excluded_pools):
        arm_lower = (getattr(account, 'id', '') or '').lower()
        name = getattr(account, 'name', None) or arm_lower.rsplit('/', 1)[-1]
        sku = getattr(account, 'sku', None)
        redundancy = pricing_helper.parse_redundancy(
            getattr(sku, 'name', None) if sku else None)

        defaults = {
            'cloud_account_id': cloud_account_id,
            'cloud_resource_id': arm_lower,
            'name': name,
            'region': region,
            'resource_type': RESOURCE_TYPE,
            'service_name': 'microsoft.storage',
            'tags': {},
            'created_at': detected_at,
            'first_seen': detected_at,
            'last_seen': detected_at,
            'active': False,
            'meta': {'created_by': CREATED_BY},
        }
        try:
            res_id, pool_id = resolve_or_insert_resource(
                self.mongo_client.restapi.resources,
                {
                    'cloud_resource_id': arm_lower,
                    'cloud_account_id': cloud_account_id,
                    'deleted_at': 0,
                },
                defaults,
            )
        except Exception as exc:
            LOG.warning("resource resolve failed for %s: %s", arm_lower, exc)
            return None

        is_excluded = bool(excluded_pools) and pool_id in excluded_pools
        return {
            'cloud_account_id': cloud_account_id,
            'cloud_resource_id': arm_lower,
            'cloud_type': 'azure_cnr',
            'cloud_account_name': ca.get('name'),
            'resource_id': res_id,
            'resource_name': name,
            'resource_type': RESOURCE_TYPE,
            'region': region,
            'saving': round(float(cand_rec.get('monthly_savings_usd') or 0.0), 2),
            'detected_at': detected_at,
            'current_tier': cand_rec.get('source_tier'),
            'target_tier': cand_rec.get('target_tier'),
            'gb': cand_rec.get('gb_moved'),
            'monthly_reads': cand_rec.get('monthly_reads'),
            'monthly_writes': cand_rec.get('monthly_writes'),
            'egress_gb': cand_rec.get('egress_gb'),
            'confidence': cand_rec.get('confidence'),
            'confidence_reason': cand_rec.get('notes') or [],
            'signal_used': cand_rec.get('signal_used'),
            'redundancy_sku': redundancy,
            'payg_storage_rate': cand_rec.get('payg_storage_rate'),
            'effective_storage_rate': cand_rec.get('effective_storage_rate'),
            'reservation_applied': cand_rec.get('reservation_applied'),
            'saving_breakdown': cand_rec.get('saving_breakdown') or {
                'payg': 0.0, 'effective': 0.0,
            },
            'pool_id': pool_id,
            'is_excluded': is_excluded,
            'created_by': CREATED_BY,
        }

    def _scan_account(self, account, creds_dict, credential,
                      days, ca, cloud_account_id,
                      detected_at, excluded_pools):
        skip_reason = self._account_should_skip(account)
        if skip_reason:
            LOG.debug("skip %s: %s", getattr(account, 'name', None), skip_reason)
            return []

        arm_id = getattr(account, 'id', None)
        if not arm_id:
            return []
        region = getattr(account, 'location', None) or ''
        sku = getattr(account, 'sku', None)
        redundancy = pricing_helper.parse_redundancy(
            getattr(sku, 'name', None) if sku else None)

        try:
            breakdown = metrics_helper.get_tier_breakdown(
                credential, creds_dict['subscription_id'], arm_id, days=days)
        except Exception as exc:
            LOG.debug("tier breakdown failed for %s: %s", arm_id, exc)
            return []

        try:
            prices = pricing_helper.get_storage_prices(region, redundancy)
        except Exception as exc:
            LOG.debug("retail prices failed for %s/%s: %s",
                      region, redundancy, exc)
            return []

        rows = []
        for source, target in cold_forecast.PAIRS:
            payg_rate = (prices.get(source) or {}).get('storage_gb_month')
            effective_rate = reservations_helper.get_effective_storage_rate(
                credential, creds_dict['subscription_id'],
                region, redundancy, source,
            )
            rec = cold_forecast.forecast_tier_move(
                breakdown, prices, source, target, days=days,
                payg_rate=payg_rate, effective_rate=effective_rate,
            )
            thr = self.PAIR_THRESHOLDS.get((source, target))
            if not thr:
                continue
            # inclusive lower bound — plan §2.6.2
            if rec.get('monthly_savings_usd', 0.0) < thr['min_saving']:
                continue
            if rec.get('gb_moved', 0.0) < thr['min_gb']:
                continue
            if not confidence_at_least(
                    rec.get('confidence'), thr['min_confidence']):
                continue
            row = self._row_for(
                rec, account, ca, region, cloud_account_id,
                detected_at, excluded_pools,
            )
            if row:
                rows.append(row)
        return rows

    def _get(self):
        # detected_at is set ONCE at the top of _get so all rows from a
        # single bumiworker run share an instant — required by upstream
        # checklist diff logic.
        detected_at = int(self.created_at)

        options = self.get_options()
        days = int(options.get('days_threshold') or DEFAULT_DAYS_THRESHOLD)
        excluded_pools = options.get('excluded_pools') or {}
        skip_accounts = options.get('skip_cloud_accounts') or []

        # single cloud_account_list call; build both azure_cnr + azure_tenant maps from response
        _, ca_response = self.rest_client.cloud_account_list(
            self.organization_id, process_recommendations=True)
        all_accounts = ca_response.get('cloud_accounts', []) or []
        ca_map = {
            ca['id']: ca for ca in all_accounts
            if ca.get('type') in self.SUPPORTED_CLOUD_TYPES
            and ca['id'] not in (skip_accounts or [])
        }
        if not ca_map:
            return []
        # Need parent azure_tenant accounts for the SPN fallback path.
        parent_map = creds_helper.build_parent_account_map(all_accounts)

        rows = []
        for cloud_account_id, ca in ca_map.items():
            creds_dict = creds_helper.extract_cloud_account_creds(
                ca, parent_map)
            if not creds_dict:
                LOG.info("azure_cnr %s missing creds; skipping",
                         cloud_account_id)
                continue

            try:
                credential = creds_helper.make_credentials(
                    creds_dict['tenant'],
                    creds_dict['client_id'],
                    creds_dict['secret'],
                )
            except Exception as exc:
                LOG.warning("credential build failed for %s: %s",
                            cloud_account_id, exc)
                continue

            try:
                from azure.mgmt.storage import StorageManagementClient
                client = StorageManagementClient(
                    credential, creds_dict['subscription_id'])
                accounts = list(client.storage_accounts.list())
            except Exception as exc:
                LOG.warning("storage_accounts.list failed for %s: %s",
                            cloud_account_id, exc)
                continue

            for account in accounts:
                try:
                    rows.extend(self._scan_account(
                        account, creds_dict, credential,
                        days, ca, cloud_account_id, detected_at,
                        excluded_pools,
                    ))
                except Exception as exc:
                    LOG.warning(
                        "cold-tier scan failed for %s: %s",
                        getattr(account, 'name', None), exc)
                    continue

        LOG.info("azure cold-tier candidates emitted: %d", len(rows))
        return rows


def main(organization_id, config_client, created_at, **kwargs):
    return AzureColdTierCandidates(
        organization_id, config_client, created_at).get()


def get_module_email_name():
    return 'Azure cold-tier candidates'
