import React from "react";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS, OBSOLETE_SNAPSHOT_CHAINS_TYPE } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "../RecommendationFactory";

class ObsoleteSnapshotChainsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_OBSOLETE_SNAPSHOT_CHAINS;

  moduleName = OBSOLETE_SNAPSHOT_CHAINS_TYPE;

  withExclusions = true;

  messageId = "obsoleteSnapshotChainsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "obsoleteSnapshotChainsDescription",
      emptyMessageId: "noObsoleteSnapshotChains",
      dataTestIds: {
        listTestId: "sp_obsolete_snapshot_chains",
        textTestId: "p_obsolete_snapshot_chains",
        buttonTestIds: ["btn_osch_download", "btn_osch_cleanup_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_osch_resource",
        accessor: "cloud_resource_id"
      }),
      resourceLocation({
        headerDataTestId: "lbl_osch_location"
      }),
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_osch_first_seen">
            <FormattedMessage id="firstSeenOn" />
          </TextWithDataTestId>
        ),
        accessor: "first_seen",
        Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
      },
      {
        Header: (
          <HeaderHelperCell
            titleDataTestId="lbl_osch_last_used"
            titleMessageId="lastSeenUsed"
            helperMessageId="snapshotObsoleteLastUsedHelp"
          />
        ),
        accessor: "last_used",
        Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
      },
      detectedAt({ headerDataTestId: "lbl_osch_detected_at" }),
      possibleMonthlySavings({
        headerDataTestId: "lbl_osch_possible_savings_per_month",
        defaultSort: "desc"
      })
    ];
  }
}

export default new ObsoleteSnapshotChainsRecommendation();
