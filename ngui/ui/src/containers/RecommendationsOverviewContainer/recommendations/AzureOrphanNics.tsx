import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import { AZURE_NETWORK } from "hooks/useRecommendationServices";
import { detectedAt, resource, resourceLocation } from "utils/columns";
import { AZURE_CNR } from "utils/constants";
import BaseRecommendation, { CATEGORY } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_orphan_nics_resource",
  }),
  resourceLocation({
    headerDataTestId: "lbl_orphan_nics_location",
  }),
  detectedAt({ headerDataTestId: "lbl_orphan_nics_detected_at" }),
];

class AzureOrphanNics extends BaseRecommendation {
  type = "azure_orphan_nics";

  name = "azureOrphanNics";

  title = "azureOrphanNicsTitle";

  descriptionMessageId = "azureOrphanNicsDescription";

  emptyMessageId = "noOrphanNics";

  services = [AZURE_NETWORK];

  appliedDataSources = [AZURE_CNR];

  categories = [CATEGORY.CRITICAL];

  withExclusions = true;

  hasSettings = false;

  dismissible = true;

  static resourceDescriptionMessageId = "azureOrphanNicsResourceRecommendation";

  get hasSaving() {
    return false;
  }

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />,
      },
      {
        key: `${item.cloud_resource_id}-region`,
        value: item.region ?? "—",
      },
    ]);
  }

  columns = columns;
}

export default AzureOrphanNics;
