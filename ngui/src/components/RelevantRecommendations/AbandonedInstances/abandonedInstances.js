import { detectedAt, poolOwner, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { RECOMMENDATION_ABANDONED_INSTANCES, ABANDONED_INSTANCES_TYPE } from "utils/constants";
import RecommendationFactory from "../RecommendationFactory";

class AbandonedInstancesRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_ABANDONED_INSTANCES;

  moduleName = ABANDONED_INSTANCES_TYPE;

  withExclusions = true;

  withThresholds = true;

  messageId = "abandonedInstancesTitle";

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withThresholds: this.withThresholds,
      descriptionMessageId: "abandonedInstancesDescription",
      emptyMessageId: "noAbandonedInstances",
      dataTestIds: {
        listTestId: "sp_abandoned_instances",
        textTestId: "p_abandoned_instances",
        buttonTestIds: ["btn_abandoned_instances_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({
        headerDataTestId: "lbl_ai_resource",
        accessor: "cloud_resource_id"
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
  }
}

export default new AbandonedInstancesRecommendation();
