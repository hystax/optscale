import React from "react";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_OBSOLETE_SNAPSHOTS, OBSOLETE_SNAPSHOTS_TYPE } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "utils/recommendations";

class ObsoleteSnapshotsRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_OBSOLETE_SNAPSHOTS;

  moduleName = OBSOLETE_SNAPSHOTS_TYPE;

  withExclusions = true;

  withThresholds = true;

  messageId = "obsoleteSnapshotsTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withThresholds: this.withThresholds,
      descriptionMessageId: "obsoleteSnapshotsDescription",
      emptyMessageId: "noObsoleteSnapshots",
      dataTestIds: {
        listTestId: "sp_obsolete_snapshots",
        textTestId: "p_obsolete_snapshots",
        buttonTestIds: ["btn_os_download", "btn_os_cleanup_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_os_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_os_location"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_os_first_seen">
            <FormattedMessage id="firstSeenOn" />
          </TextWithDataTestId>
        ),
        accessorKey: "first_seen",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
        }
      },
      {
        header: (
          <HeaderHelperCell
            titleDataTestId="lbl_os_last_used"
            titleMessageId="lastSeenUsed"
            helperMessageId="snapshotObsoleteLastUsedHelp"
          />
        ),
        accessorKey: "last_used",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
        }
      },
      detectedAt({ headerDataTestId: "lbl_os_detected_at" }),
      possibleMonthlySavings({
        headerDataTestId: "lbl_os_possible_monthly_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new ObsoleteSnapshotsRecommendation();
