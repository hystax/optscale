import logging

from bumiworker.bumiworker.consts import ArchiveReason
from bumiworker.bumiworker.modules.base import ArchiveBase
from bumiworker.bumiworker.modules.recommendations.azure_orphan_nics import (
    AzureOrphanNics as AzureOrphanNicsRecommendation,
    SUPPORTED_CLOUD_TYPES,
)

LOG = logging.getLogger(__name__)


class AzureOrphanNics(ArchiveBase, AzureOrphanNicsRecommendation):
    """Archive module for azure_orphan_nics recommendations.

    Reads sentinel ``deleted_at`` state written by per-run reconciliation in
    the recommendation module.  No fresh Azure SDK call is made here.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reason_description_map[ArchiveReason.RECOMMENDATION_APPLIED] = (
            "NIC deleted or attached to VM"
        )
        self.reason_description_map[ArchiveReason.RECOMMENDATION_IRRELEVANT] = (
            "NIC re-attached to VM"
        )

    @property
    def supported_cloud_types(self):
        return SUPPORTED_CLOUD_TYPES

    def _get(self, previous_options, optimizations, cloud_accounts_map):
        result = []
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
                self._set_reason_properties(opt, ArchiveReason.CLOUD_ACCOUNT_DELETED)
                result.append(opt)
                continue

            doc = docs_by_id.get(res_id) if res_id else None
            if doc is None:
                # Sentinel doc gone entirely.  This is the expected path when
                # the recommendation row's resource was hard-deleted from the
                # restapi.resources collection (e.g. operator cleanup).  Log
                # so an unexpectedly-high RESOURCE_DELETED rate is visible
                # without surfacing as a real error.
                LOG.info(
                    "sentinel doc absent for resource_id=%s account=%s; archiving"
                    " as RESOURCE_DELETED",
                    res_id,
                    ca_id,
                )
                self._set_reason_properties(opt, ArchiveReason.RESOURCE_DELETED)
                result.append(opt)
                continue

            if doc.get("deleted_at", 0) != 0:
                self._set_reason_properties(opt, ArchiveReason.RECOMMENDATION_APPLIED)
                result.append(opt)
                continue

            # By construction, get_archive_candidates only feeds rows that
            # left the current scan, so reconciliation should already have
            # set deleted_at.  Reaching this branch means an invariant was
            # violated (e.g. reconciliation crashed for this account between
            # runs).  Log loudly rather than silently mislabel.
            LOG.error(
                "azure_orphan_nics archive invariant violation: optimization"
                " %s left current scan but sentinel doc still has deleted_at=0;"
                " marking IRRELEVANT but reconciliation likely failed",
                res_id,
            )
            self._set_reason_properties(opt, ArchiveReason.RECOMMENDATION_IRRELEVANT)
            result.append(opt)

        return result


def main(organization_id, config_client, created_at, **kwargs):
    return AzureOrphanNics(organization_id, config_client, created_at).get()
