import { detectedAt, resourceLocation, resource, savings, text } from "utils/columns";
import {
  INSTANCES_GENERATION_UPGRADE_TYPE,
  METADATA_FIELDS,
  RECOMMENDATION_INSTANCES_GENERATION_UPGRADE
} from "utils/constants";
import RecommendationFactory from "utils/recommendations";

class InstancesGenerationUpgradeRecommendation extends RecommendationFactory {
  type = RECOMMENDATION_INSTANCES_GENERATION_UPGRADE;

  moduleName = INSTANCES_GENERATION_UPGRADE_TYPE;

  messageId = "instancesGenerationUpgradeTitle";

  withExclusions = true;

  configure() {
    return {
      type: this.type,
      moduleName: this.moduleName,
      withExclusions: this.withExclusions,
      descriptionMessageId: "instancesGenerationUpgradeDescription",
      emptyMessageId: "noInstancesToUpgrade",
      dataTestIds: {
        listTestId: "sp_instances_generation_upgrade",
        textTestId: "p_instances_generation_upgrade",
        buttonTestIds: ["btn_igu_download"]
      }
    };
  }

  static configureColumns() {
    return [
      resource({ headerDataTestId: "lbl_igu_resource" }),
      resourceLocation({ headerDataTestId: "lbl_igu_location" }),
      text({ headerMessageId: METADATA_FIELDS.SIZE, headerDataTestId: "lbl_igu_flavor", accessorKey: "flavor" }),
      text({
        headerMessageId: "recommendedSize",
        headerDataTestId: "lbl_igu_recommended_flavor",
        accessorKey: "recommended_flavor"
      }),
      detectedAt({ headerDataTestId: "lbl_igu_detected_at" }),
      savings({ headerDataTestId: "lbl_igu_possible_monthly_savings", options: { defaultSort: "desc" } })
    ];
  }
}

export default new InstancesGenerationUpgradeRecommendation();
