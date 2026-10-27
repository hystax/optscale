import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedLoadBalancersModal from "components/SideModalManager/SideModals/recommendations/AbandonedLoadBalancersModal";
import { ALIBABA_SLB, AWS_EC2, AZURE_NETWORK } from "hooks/useRecommendationServices";
import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES, AZURE_CNR, AWS_CNR, ALIBABA_CNR } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_abandoned_load_balancers_resource",
  }),
  resourceLocation({
    headerDataTestId: "lbl_abandoned_load_balancers_location",
    typeAccessor: "cloud_type",
  }),
  poolOwner({
    headerDataTestId: "lbl_abandoned_load_balancers_pool_owner",
    id: "pool/owner",
  }),
  detectedAt({ headerDataTestId: "lbl_abandoned_load_balancers_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_abandoned_load_balancers_possible_monthly_savings",
    defaultSort: "desc",
  }),
];

class AbandonedLoadBalancers extends BaseRecommendation {
  type = "abandoned_load_balancers";

  name = "abandonedLoadBalancers";

  title = "abandonedLoadBalancersTitle";

  descriptionMessageId = "abandonedLoadBalancersDescription";

  get descriptionMessageValues() {
    const {
      days_threshold: daysThreshold,
      bytes_sent_threshold: bytesSentThreshold,
      packets_sent_threshold: packetsSendThreshold,
      requests_threshold: requestsThreshold,
    } = this.options;

    return { bytesSentThreshold, packetsSendThreshold, daysThreshold, requestsThreshold };
  }

  emptyMessageId = "noAbandonedLoadBalancers";

  services = [AZURE_NETWORK, AWS_EC2, ALIBABA_SLB];

  appliedDataSources = [AZURE_CNR, AWS_CNR, ALIBABA_CNR];

  categories = [CATEGORY.COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedLoadBalancersModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedLoadBalancersResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-${item.resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />,
      },
    ]);
  }

  columns = columns;
}

export default AbandonedLoadBalancers;
