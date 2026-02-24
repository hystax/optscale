import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import InstancesForShutdownModal from "components/SideModalManager/SideModals/recommendations/InstancesForShutdownModal";
import {
  ALIBABA_ECS,
  AWS_EC2,
  AWS_RDS,
  AZURE_COMPUTE,
  GCP_COMPUTE_ENGINE,
  NEBIUS_SERVICE,
} from "hooks/useRecommendationServices";
import { resource, resourceLocation, poolAndOwner, possibleShutdownPeriods, savings } from "utils/columns";
import { ALIBABA_CNR, AWS_CNR, AZURE_CNR, FORMATTED_MONEY_TYPES, GCP_CNR, NEBIUS } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource({ headerDataTestId: "lbl_is_resource" }),
  resourceLocation({ headerDataTestId: "lbl_is_location" }),
  poolAndOwner({ headerDataTestId: "lbl_is_pool_owner" }),
  possibleShutdownPeriods({ headerDataTestId: "lbl_is_pool_owner" }),
  savings({ headerDataTestId: "lbl_is_possible_monthly_savings", defaultSort: "desc" }),
];

class InstancesForShutdown extends BaseRecommendation {
  type = "instances_for_shutdown";

  name = "instancesForShutdown";

  title = "instancesForShutdown";

  descriptionMessageId = "instancesForShutdownDescription";

  get descriptionMessageValues() {
    const {
      cpu_percent_threshold: cpuPercentThreshold,
      network_bps_threshold: networkBpsThreshold,
      days_threshold: daysThreshold,
    } = this.options;

    return { cpuPercentThreshold, networkBpsThreshold, daysThreshold };
  }

  emptyMessageId = "noInstancesForShutdown";

  services = [AWS_EC2, AWS_RDS, AZURE_COMPUTE, GCP_COMPUTE_ENGINE, ALIBABA_ECS, NEBIUS_SERVICE];

  appliedDataSources = [ALIBABA_CNR, AWS_CNR, AZURE_CNR, NEBIUS, GCP_CNR];

  categories = [CATEGORY.COST];

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = InstancesForShutdownModal;

  static resourceDescriptionMessageId = "instancesForShutdownResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />,
      },
    ]);
  }

  columns = columns;
}

export default InstancesForShutdown;
