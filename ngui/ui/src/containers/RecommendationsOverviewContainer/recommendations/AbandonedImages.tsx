import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import AbandonedImagesModal from "components/SideModalManager/SideModals/recommendations/AbandonedImagesModal";
import { NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { firstSeenOn, lastSeenUsed, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_abandoned_image_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_abandoned_image_location"
  }),
  firstSeenOn({
    headerDataTestId: "lbl_abandoned_image_first_seen"
  }),
  lastSeenUsed({
    headerDataTestId: "lbl_abandoned_image_last_used",
    headerHelperMessageId: "abandonedImageLastUsedHelp"
  }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_abandoned_image_last_used",
    defaultSort: "desc"
  })
];

class AbandonedImages extends BaseRecommendation {
  type = "abandoned_images";

  name = "abandonedImages";

  title = "abandonedImagesTitle";

  descriptionMessageId = "abandonedImagesDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noAbandonedImages";

  services = [NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  hasSettings = true;

  settingsSidemodalClass = AbandonedImagesModal;

  withExclusions = true;

  static resourceDescriptionMessageId = "abandonedImagesResourceRecommendation";

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

export default AbandonedImages;
