import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import { ALIBABA_ECS, AWS_EC2, AWS_RDS, AZURE_COMPUTE } from "hooks/useRecommendationServices";
import { detectedAt, resourceLocation, resource, savings, text } from "utils/columns";
import { METADATA_FIELDS } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
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

class InstancesGenerationUpgrade extends BaseRecommendation {
  type = "instance_generation_upgrade";

  name = "instancesGenerationUpgrade";

  title = "instancesGenerationUpgradeTitle";

  descriptionMessageId = "instancesGenerationUpgradeDescription";

  emptyMessageId = "noInstancesToUpgrade";

  services = [AWS_EC2, AWS_RDS, AZURE_COMPUTE, ALIBABA_ECS];

  categories = [CATEGORY_COST];

  withExclusions = true;

  static resourceDescriptionMessageId = "instancesGenerationUpgradeResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: item.recommended_flavor
      }
    ]);
  }

  columns = columns;
}

export default InstancesGenerationUpgrade;
