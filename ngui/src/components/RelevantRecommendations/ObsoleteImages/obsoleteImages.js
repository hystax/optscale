import React from "react";
import { FormattedMessage } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import HeaderHelperCell from "components/HeaderHelperCell";
import TextWithDataTestId from "components/TextWithDataTestId";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_OBSOLETE_IMAGES, OBSOLETE_IMAGES_TYPE } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import RecommendationFactory from "../RecommendationFactory";

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
        headerDataTestId: "lbl_oi_resource",
        accessor: "cloud_resource_id"
      }),
      resourceLocation({
        headerDataTestId: "lbl_oi_location"
      }),
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_oi_created_at">
            <FormattedMessage id="createdAt" />
          </TextWithDataTestId>
        ),
        accessor: "first_seen",
        Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
      },
      {
        Header: (
          <HeaderHelperCell
            titleDataTestId="lbl_oi_last_used"
            titleMessageId="lastUsed"
            helperMessageId="imageObsoleteLastUsedHelp"
          />
        ),
        accessor: "last_used",
        Cell: ({ cell: { value } }) => (value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value))
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_oi_snapshots">
            <FormattedMessage id="snapshots" />
          </TextWithDataTestId>
        ),
        accessor: "snapshots",
        disableSortBy: true,
        Cell: ({ cell: { value: snapshots = [] } }) =>
          snapshots.map((snapshot) => (
            <div key={snapshot.resource_id} style={{ whiteSpace: "nowrap" }}>
              <CloudResourceId resourceId={snapshot.resource_id} cloudResourceId={snapshot.cloud_resource_id} />
            </div>
          ))
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
