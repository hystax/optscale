import React from "react";
import { FormattedMessage } from "react-intl";
import CloudTypeIcon from "components/CloudTypeIcon";
import FormattedMoney from "components/FormattedMoney";
import IconLabel from "components/IconLabel";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS, AWS_EC2, AWS_RDS } from "hooks/useRecommendationServices";
import { detectedAt, size, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_im_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_im_location",
    locationAccessors: {
      region: "current_region"
    }
  }),
  size({
    headerDataTestId: "lbl_im_size"
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_im_recomm_region">
        <FormattedMessage id="recommendedRegion" />
      </TextWithDataTestId>
    ),
    accessorKey: "recommended_region",
    cell: ({ row: { original } }) => (
      <IconLabel icon={<CloudTypeIcon fontSize="small" type={original.cloud_type} />} label={original.recommended_region} />
    )
  },
  detectedAt({ headerDataTestId: "lbl_im_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_im_possible_monthly_savings",
    defaultSort: "desc"
  })
];

class InstancesMigration extends BaseRecommendation {
  type = "instance_migration";

  name = "instanceMigration";

  title = "instanceMigrationTitle";

  descriptionMessageId = "instanceMigrationDescription";

  emptyMessageId = "noInstanceMigrations";

  services = [AWS_EC2, AWS_RDS, ALIBABA_ECS];

  categories = [CATEGORY_COST];

  withExclusions = true;

  static resourceDescriptionMessageId = "instanceMigrationResourceRecommendation";

  static getResourceDescriptionMessageValues(backendInfo) {
    const { recommended_flavor: flavor, recommended_region: regionName } = backendInfo;
    return { size: flavor, regionName };
  }

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-region`,
        value: <IconLabel icon={<CloudTypeIcon fontSize="small" type={item.cloud_type} />} label={item.recommended_region} />
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default InstancesMigration;
