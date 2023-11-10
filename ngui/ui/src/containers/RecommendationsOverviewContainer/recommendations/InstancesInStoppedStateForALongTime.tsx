import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import InstancesInStoppedStateForALongTimeModal from "components/SideModalManager/SideModals/recommendations/InstancesInStoppedStateForALongTimeModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_ECS, AZURE_COMPUTE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FULL_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_ind_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_ind_location"
  }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_ind_last_active">
        <FormattedMessage id="lastSeenActive" />
      </TextWithDataTestId>
    ),
    accessorKey: "last_seen_active",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value, EN_FULL_FORMAT);
    }
  },
  detectedAt({ headerDataTestId: "lbl_ind_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_ind_cost">
        <FormattedMessage id="costInStoppedState" />
      </TextWithDataTestId>
    ),
    accessorKey: "cost_in_stopped_state",
    cell: ({ cell }) => <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={cell.getValue()} />
  },
  possibleMonthlySavings({
    headerDataTestId: "lbl_ind_savings",
    defaultSort: "desc"
  })
];

class InstancesInStoppedStateForALongTime extends BaseRecommendation {
  type = "instances_in_stopped_state_for_a_long_time";

  name = "instancesInStoppedStateForALongTime";

  title = "instancesAreStoppedButNotDeallocatedTitle";

  descriptionMessageId = "instancesInStoppedStateForALongTimeDescription";

  hasSettings = true;

  settingsSidemodalClass = InstancesInStoppedStateForALongTimeModal;

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;

    return { daysThreshold };
  }

  emptyMessageId = "noInstanceMigrationsInStoppedState";

  services = [AZURE_COMPUTE, ALIBABA_ECS];

  categories = [CATEGORY_COST];

  withExclusions = true;

  withCleanupScripts = true;

  static resourceDescriptionMessageId = "instancesInStoppedStateForALongTimeResourceRecommendation";

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

export default InstancesInStoppedStateForALongTime;
