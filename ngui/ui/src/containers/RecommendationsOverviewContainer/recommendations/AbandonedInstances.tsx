import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedInstancesModal from "components/SideModalManager/SideModals/recommendations/AbandonedInstancesModal";
import { ALIBABA_ECS, AWS_EC2, AWS_RDS, AZURE_COMPUTE, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_ai_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_ai_location",
    typeAccessor: "cloud_type"
  }),
  poolOwner({
    headerDataTestId: "lbl_ai_pool_owner",
    id: "pool/owner"
  }),
  detectedAt({ headerDataTestId: "lbl_ai_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_ai_possible_monthly_savings",
    defaultSort: "desc"
  })
];

class AbandonedInstances extends BaseRecommendation {
  type = "abandoned_instances";

  name = "abandonedInstances";

  title = "abandonedInstancesTitle";

  descriptionMessageId = "abandonedInstancesDescription";

  get descriptionMessageValues() {
    const {
      days_threshold: daysThreshold,
      cpu_percent_threshold: cpuPercentThreshold,
      network_bps_threshold: networkBpsThreshold
    } = this.options;

    return { cpuPercentThreshold, networkBpsThreshold, daysThreshold };
  }

  emptyMessageId = "noAbandonedInstances";

  services = [ALIBABA_ECS, AZURE_COMPUTE, AWS_EC2, AWS_RDS, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedInstancesModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedInstancesResourceRecommendation";

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

export default AbandonedInstances;
