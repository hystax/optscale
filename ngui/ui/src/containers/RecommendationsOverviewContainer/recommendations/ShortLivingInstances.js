import React from "react";
import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS, AWS_EC2, AZURE_COMPUTE, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_si_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_si_location"
  }),
  detectedAt({ headerDataTestId: "lbl_si_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_si_expenses">
        <FormattedMessage id="expenses" />
      </TextWithDataTestId>
    ),
    accessorKey: "total_cost",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMMON} />;
    }
  },
  possibleMonthlySavings({
    headerDataTestId: "lbl_si_savings",
    defaultSort: "desc"
  })
];

class ShortLivingInstances extends BaseRecommendation {
  type = "short_living_instances";

  name = "shortLivingInstances";

  title = "possibleSavingsWithSpotInstancesTitle";

  descriptionMessageId = "shortLivingInstancesDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  services = [AWS_EC2, AZURE_COMPUTE, ALIBABA_ECS, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  emptyMessageId = "noNonSpotInstances";

  withExclusions = true;

  dismissable = false;

  static resourceDescriptionMessageId = "shortLivingInstancesResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default ShortLivingInstances;
