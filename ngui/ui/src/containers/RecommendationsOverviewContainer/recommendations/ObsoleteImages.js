import React from "react";
import { FormattedMessage } from "react-intl";
import CloudResourceId from "components/CloudResourceId";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import ObsoleteImagesModal from "components/SideModalManager/SideModals/recommendations/ObsoleteImagesModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS, AWS_EC2 } from "hooks/useRecommendationServices";
import { detectedAt, firstSeenOn, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { unixTimestampToDateTime } from "utils/datetime";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_oi_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_oi_location"
  }),
  firstSeenOn({
    headerDataTestId: "lbl_oi_created_at"
  }),
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
        <div key={snapshot.cloud_resource_id} style={{ whiteSpace: "nowrap" }}>
          <CloudResourceId resourceId={snapshot.cloud_resource_id} cloudResourceIdentifier={snapshot.cloud_cloud_resource_id} />
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

class ObsoleteImages extends BaseRecommendation {
  type = "obsolete_images";

  name = "obsoleteImages";

  title = "obsoleteImagesTitle";

  descriptionMessageId = "obsoleteImagesDescription";

  services = [AWS_EC2, ALIBABA_ECS];

  categories = [CATEGORY_COST];

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  hasSettings = true;

  settingsSidemodalClass = ObsoleteImagesModal;

  withCleanupScripts = true;

  emptyMessageId = "noObsoleteImages";

  dismissable = false;

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default ObsoleteImages;
