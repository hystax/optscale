import React from "react";
import { FormattedMessage } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_OBSOLETE_IMAGES, OBSOLETE_IMAGES_TYPE } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "utils/recommendations";

class ObsoleteImagesRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_OBSOLETE_IMAGES;

  moduleName = OBSOLETE_IMAGES_TYPE;

  withThresholds = true;

  messageId = "obsoleteImagesTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withThresholds: this.withThresholds,
      descriptionMessageId: "obsoleteImagesDescription",
      emptyMessageId: "noObsoleteImages",
      dataTestIds: {
        listTestId: "sp_obsolete_images",
        textTestId: "p_obsolete_images",
        buttonTestIds: ["btn_oi_download", "btn_oi_cleanup_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_oi_resource"
      }),
      resourceLocation({
        headerDataTestId: "lbl_oi_location"
      }),
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_oi_created_at">
            <FormattedMessage id="createdAt" />
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
            titleDataTestId="lbl_oi_last_used"
            titleMessageId="lastUsed"
            helperMessageId="imageObsoleteLastUsedHelp"
          />
        ),
        accessorKey: "last_used",
        cell: ({ cell }) => {
          const value = cell.getValue();

          return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value);
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_oi_snapshots">
            <FormattedMessage id="snapshots" />
          </TextWithDataTestId>
        ),
        accessorKey: "snapshots",
        enableSorting: false,
        cell: ({ cell }) => {
          const snapshots = cell.getValue();

          return snapshots.map((snapshot) => (
            <div key={snapshot.resource_id} style={{ whiteSpace: "nowrap" }}>
              <CloudResourceId resourceId={snapshot.resource_id} cloudResourceIdentifier={snapshot.cloud_resource_id} />
            </div>
          ));
        }
      },
      detectedAt({ headerDataTestId: "lbl_oi_detected_at" }),
      possibleMonthlySavings({
        headerDataTestId: "lbl_oi_savings",
        defaultSort: "desc"
      })
    ];
  }
}

export default new ObsoleteImagesRecommendation();
