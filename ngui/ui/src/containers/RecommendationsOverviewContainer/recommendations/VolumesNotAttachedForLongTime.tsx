import { FormattedMessage } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import VolumesNotAttachedForLongTimeModal from "components/SideModalManager/SideModals/recommendations/VolumesNotAttachedForLongTimeModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_EBS, AWS_EC2_EBS, AZURE_COMPUTE, GCP_COMPUTE_ENGINE, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, possibleMonthlySavings, resource, resourceLocation } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FULL_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_vna_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_vna_location"
  }),
  {
    header: (
      <HeaderHelperCell
        titleDataTestId="lbl_vna_last_time"
        titleMessageId="lastTimeAttached"
        helperMessageId="volumesNotAttachedLastTimeHelp"
      />
    ),
    accessorKey: "last_seen_in_attached_state",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return value === 0 ? <FormattedMessage id="never" /> : unixTimestampToDateTime(value, EN_FULL_FORMAT);
    }
  },
  detectedAt({ headerDataTestId: "lbl_vna_detected_at" }),
  {
    header: (
      <TextWithDataTestId dataTestId="lbl_vna_expenses">
        <FormattedMessage id="expensesWhenDetached" />
      </TextWithDataTestId>
    ),
    accessorKey: "cost_in_detached_state",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
    }
  },
  possibleMonthlySavings({
    headerDataTestId: "lbl_vna_possible_monthly_savings",
    defaultSort: "desc"
  })
];

class VolumesNotAttachedForLongTime extends BaseRecommendation {
  type = "volumes_not_attached_for_a_long_time";

  name = "volumesNotAttachedForLongTime";

  title = "volumesAreNotAttachedTitle";

  descriptionMessageId = "volumesNotAttachedForLongTimeDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return { daysThreshold };
  }

  services = [ALIBABA_EBS, AWS_EC2_EBS, AZURE_COMPUTE, GCP_COMPUTE_ENGINE, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  emptyMessageId = "noDetachedVolumes";

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = VolumesNotAttachedForLongTimeModal;

  withCleanupScripts = true;

  static resourceDescriptionMessageId = "volumesNotAttachedForLongTimeResourceRecommendation";

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

export default VolumesNotAttachedForLongTime;
