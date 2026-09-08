import logging

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.azure_abandoned_storage_accounts import (
    AzureAbandonedStorageAccounts as AzureAbandonedStorageAccountsRecommendation,
    NATIVE_MARKER,
    SUPPORTED_CLOUD_TYPES,
)

LOG = logging.getLogger(__name__)

_THRESHOLD_KEYS = frozenset(
    {
        "idle_days_window",
        "idle_transactions_threshold",
        "min_account_age_days",
        "min_used_capacity_gb",
    }
)


class AzureAbandonedStorageAccounts(
    ArchiveBase, AzureAbandonedStorageAccountsRecommendation
):
    """Archive module for azure_abandoned_storage_accounts recommendations.

    Reads sentinel ``deleted_at`` state written by per-run reconciliation in
    the recommendation module.  No fresh Azure SDK call is made here.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            "Storage account deleted or no longer idle"
        )
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            "Storage account no longer meets idle criteria"
        )

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map):
        result = []

        # Batch-fetch sentinel docs for all optimizations in one query.
        resource_ids = [
            opt["resource_id"]
            for opt in optimizations
            if opt.get("resource_id")
        ]
        docs_by_id = {}
        if resource_ids:
            coll = self.mongo_client.restapi.resources
            for d in coll.find(
                {"_id": {"$in": resource_ids}},
                {
                    "_id": 1,
                    "deleted_at": 1,
                    "cloud_account_id": 1,
                    "meta.created_by": 1,
                },
            ):
                docs_by_id[d["_id"]] = d

        for opt in optimizations:
            ca_id = opt.get("cloud_account_id")
            res_id = opt.get("resource_id")

            if ca_id not in cloud_accounts_map:
                self._set_reason_properties(
                    opt, ArchiveReason.CLOUD_ACCOUNT_DELETED
                )
                result.append(opt)
                continue

            # Check whether any of the four threshold options changed.
            # Compare against CURRENT persisted values (not hardcoded defaults)
            # so that an org which keeps a stable non-default threshold (e.g.
            # idle_days_window=14) does not get OPTIONS_CHANGED on every run.
            current_options_values = self.get_options_values()
            current_options = dict(
                zip(
                    [
                        "idle_days_window",
                        "idle_transactions_threshold",
                        "min_account_age_days",
                        "min_used_capacity_gb",
                        "excluded_pools",
                        "skip_cloud_accounts",
                    ],
                    current_options_values,
                )
            )
            options_changed = any(
                previous_options[k] != current_options.get(k)
                for k in _THRESHOLD_KEYS
                if k in previous_options
            )
            if options_changed:
                self._set_reason_properties(opt, ArchiveReason.OPTIONS_CHANGED)
                result.append(opt)
                continue

            doc = docs_by_id.get(res_id) if res_id else None
            if doc is None:
                LOG.info(
                    "sentinel doc absent for resource_id=%s account=%s;"
                    " archiving as RESOURCE_DELETED",
                    res_id,
                    ca_id,
                )
                self._set_reason_properties(opt, ArchiveReason.RESOURCE_DELETED)
                result.append(opt)
                continue

            if doc.get("deleted_at", 0) != 0:
                self._set_reason_properties(
                    opt, ArchiveReason.RECOMMENDATION_APPLIED
                )
                result.append(opt)
                continue

            # Invariant violation: optimization left the current scan but
            # sentinel still has deleted_at=0.  Log loudly; mark irrelevant.
            LOG.error(
                "azure_abandoned_storage_accounts archive invariant violation:"
                " optimization %s left current scan but sentinel still has"
                " deleted_at=0; marking IRRELEVANT — reconciliation likely failed",
                res_id,
            )
            self._set_reason_properties(
                opt, ArchiveReason.RECOMMENDATION_IRRELEVANT
            )
            result.append(opt)

        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AzureAbandonedStorageAccounts(
        organization_id, config_client, created_at
    ).get()
