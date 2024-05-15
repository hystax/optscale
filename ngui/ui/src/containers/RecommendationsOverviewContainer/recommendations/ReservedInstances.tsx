import { Link } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import FormattedMoney from "components/FormattedMoney";
import HeaderHelperCell from "components/HeaderHelperCell";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import ReservedInstancesModal from "components/SideModalManager/SideModals/recommendations/ReservedInstancesModal";
import { AWS_EC2 } from "hooks/useRecommendationServices";
import { RI_SP_COVERAGE } from "urls";
import { detectedAt, resource, resourceLocation, size } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const columns = [
  resource({
    headerDataTestId: "lbl_ri_resource"
  }),
  resourceLocation({
    headerDataTestId: "lbl_ri_location"
  }),
  size({
    headerDataTestId: "lbl_ri_size"
  }),
  detectedAt({ headerDataTestId: "lbl_ri_detected_at" }),
  {
    header: (
      <HeaderHelperCell
        titleDataTestId="lbl_ri_savings_min"
        titleMessageId="savingsWithMinimalCommitment"
        helperMessageId="cvosSavingsWithSixMonthCommitmentHelp"
      />
    ),
    accessorKey: "saving",
    defaultSort: "desc",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
    }
  },
  {
    header: (
      <HeaderHelperCell
        titleDataTestId="lbl_ri_savings_avg"
        titleMessageId="savingsWithAverageCommitment"
        helperMessageId="savingsWithAverageCommitmentHelp"
      />
    ),
    accessorKey: "average_saving",
    cell: ({ cell }) => {
      const value = cell.getValue();

      return <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />;
    }
  }
];

class ReservedInstances extends BaseRecommendation {
  type = "reserved_instances";

  name = "reservedInstances";

  title = "reservedInstancesSavingOpportunitiesTitle";

  descriptionMessageId = "reservedInstancesDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold } = this.options;
    return {
      daysThreshold,
      link: (chunks) => (
        <Link to={RI_SP_COVERAGE} component={RouterLink}>
          {chunks}
        </Link>
      )
    };
  }

  services = [AWS_EC2];

  categories = [CATEGORY_COST];

  emptyMessageId = "noReservedInstances";

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = ReservedInstancesModal;

  static resourceDescriptionMessageId = "reservedInstancesResourceRecommendation";

  get previewItems() {
    return this.items.map((item) => [
      {
        key: `${item.cloud_resource_id}-label`,
        value: <RecommendationListItemResourceLabel item={item} />
      },
      {
        key: `${item.cloud_resource_id}-flavor`,
        value: item.flavor
      },
      {
        key: `${item.cloud_resource_id}-saving`,
        value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={item.saving} />
      }
    ]);
  }

  columns = columns;
}

export default ReservedInstances;
