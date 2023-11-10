import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import { ALIBABA_ECS } from "hooks/useRecommendationServices";
import { detectedAt, firstSeenOn, lastSeenUsed, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_osch_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_osch_location"
  }),
  firstSeenOn({
    headerDataTestId: "lbl_osch_first_seen"
  }),
  lastSeenUsed({
    headerDataTestId: "lbl_osch_last_used",
    headerHelperMessageId: "snapshotObsoleteLastUsedHelp"
  }),
  detectedAt({ headerDataTestId: "lbl_osch_detected_at" }),
  possibleMonthlySavings({
    headerDataTestId: "lbl_osch_possible_savings_per_month",
    defaultSort: "desc"
  })
];

class ObsoleteSnapshotChains extends BaseRecommendation {
  type = "obsolete_snapshot_chains";

  name = "obsoleteSnapshotChains";

  title = "obsoleteSnapshotChainsTitle";

  descriptionMessageId = "obsoleteSnapshotChainsDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  services = [ALIBABA_ECS];

  categories = [CATEGORY_COST];

  emptyMessageId = "noObsoleteSnapshotChains";

  withExclusions = true;

  withCleanupScripts = true;

  static resourceDescriptionMessageId = "obsoleteSnapshotChainsResourceRecommendation";

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

export default ObsoleteSnapshotChains;
