import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS } from "hooks/useRecommendationServices";
import { detectedAt, size, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_is_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_is_location"
  }),
  size({
    headerDataTestId: "lbl_is_size"
  }),
  detectedAt({ headerDataTestId: "lbl_is_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_is_monthly_saving">
        <FormattedMessage id="monthlySavingsWithOneMonthSubscription" />
      </TextWithDataTestId>
    ),
    accessorKey: "monthly_saving",
    defaultSort: "desc",
    cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
  },
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_is_annually_monthly_saving">
        <FormattedMessage id="monthlySavingsWithAnnualSubscription" />
      </TextWithDataTestId>
    ),
    accessorKey: "annually_monthly_saving",
    cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
  }
];

class InstanceSubscription extends BaseRecommendation {
  type = "instance_subscription";

  name = "instanceSubscription";

  title = "instanceSubscriptionSavingOpportunitiesTitle";

  descriptionMessageId = "instanceSubscriptionDescription";

  emptyMessageId = "noInstanceSubscription";

  services = [ALIBABA_ECS];

  categories = [CATEGORY_COST];

  withExclusions = true;

  static resourceDescriptionMessageId = "instanceSubscriptionResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-flavor`,
        value: item.flavor
      }
    ]);
  }

  columns = columns;
}

export default InstanceSubscription;
