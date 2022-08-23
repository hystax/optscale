import { resource, resourceLocation, poolAndOwner, possibleShutdownPeriods, savings } from "utils/columns";
import { RECOMMENDATION_INSTANCES_FOR_SHUTDOWN, INSTANCES_FOR_SHUTDOWN_TYPE } from "utils/constants";
import RecommendationFactory from "../RecommendationFactory";

class InstancesForShutdown extends RecommendationFactory {
  type = RECOMMENDATION_INSTANCES_FOR_SHUTDOWN;

  moduleName = INSTANCES_FOR_SHUTDOWN_TYPE;

  messageId = "instancesForShutdown";

  withExclusions = true;

  withThresholds = true;

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      withThresholds: this.withThresholds,
      descriptionMessageId: "instancesForShutdownDescription",
      emptyMessageId: "noInstancesForShutdown",
      dataTestIds: {
        listTestId: "sp_instances_for_shutdown",
        textTestId: "p_instances_for_shutdown",
        buttonTestIds: ["btn_instances_for_shutdown_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({ headerDataTestId: "lbl_is_resource" }),
      resourceLocation({ headerDataTestId: "lbl_is_location" }),
      poolAndOwner({ headerDataTestId: "lbl_is_pool_owner" }),
      possibleShutdownPeriods({ headerDataTestId: "lbl_is_pool_owner" }),
      savings({ headerDataTestId: "lbl_is_possible_monthly_savings", defaultSort: "desc" })
    ];
  }
}

export default new InstancesForShutdown();
