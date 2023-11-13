import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import ObsoleteSnapshotsModal from "components/SideModalManager/SideModals/recommendations/ObsoleteSnapshotsModal";
import { AWS_EC2, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, firstSeenOn, lastSeenUsed, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_os_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_os_location"
  }),
  firstSeenOn({
    headerDataTestId: "lbl_os_first_seen"
  }),
  lastSeenUsed({
    headerDataTestId: "lbl_os_last_used",
    headerHelperMessageId: "snapshotObsoleteLastUsedHelp"
  }),
  detectedAt({ headerDataTestId: "lbl_os_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_os_possible_monthly_savings",
    defaultSort: "desc"
  })
];

class ObsoleteSnapshots extends BaseRecommendation {
  type = "obsolete_snapshots";

  name = "obsoleteSnapshots";

  title = "obsoleteSnapshotsTitle";

  descriptionMessageId = "obsoleteSnapshotsDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  services = [AWS_EC2, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  emptyMessageId = "noObsoleteSnapshots";

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = ObsoleteSnapshotsModal;

  withCleanupScripts = true;

  static resourceDescriptionMessageId = "obsoleteSnapshotsResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default ObsoleteSnapshots;
