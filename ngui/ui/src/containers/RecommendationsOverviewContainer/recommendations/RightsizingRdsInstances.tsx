import { Stack } from "@mui/material";
import { FormattedMessage, FormattedNumber } from "react-intl";
import FormattedMoney from "components/FormattedMoney";
import RecommendationListItemResourceLabel from "components/RecommendationListItemResourceLabel";
import RightsizingCpuUsageHeaderCell from "components/RightsizingCpuUsageHeaderCell";
import RightsizingStrategyModal from "components/SideModalManager/SideModals/recommendations/RightsizingStrategyModal";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ALIBABA_RDS, NEBIUS_SERVICE } from "hooks/useRecommendationServices";
import { detectedAt, recommendedRightsizingSize, resource, resourceLocation, rightsizingSize } from "utils/columns";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import BaseRecommendation, { CATEGORY_COST } from "./BaseRecommendation";

const RightsizingCpuUsageCell = ({ currentUsage, projectedUsage }) => (
  <Stack spacing={1}>
    <div>
      <FormattedMessage
        id="rightsizingCPUUsageProperties"
        values={{
          type: "current",
          average: <FormattedNumber value={currentUsage.cpuUsage / 100} format="percentage2" />,
          max: <FormattedNumber value={currentUsage.cpuPeak / 100} format="percentage2" />,
          q50: <FormattedNumber value={currentUsage.cpuQuantile50 / 100} format="percentage2" />,
          q99: <FormattedNumber value={currentUsage.cpuQuantile99 / 100} format="percentage2" />
        }}
      />
    </div>
    <div>
      <FormattedMessage
        id="rightsizingCPUUsageProperties"
        values={{
          type: "projected",
          average: <FormattedNumber value={projectedUsage.cpuUsage / 100} format="percentage2" />,
          max: <FormattedNumber value={projectedUsage.cpuPeak / 100} format="percentage2" />,
          q50: <FormattedNumber value={projectedUsage.cpuQuantile50 / 100} format="percentage2" />,
          q99: <FormattedNumber value={projectedUsage.cpuQuantile99 / 100} format="percentage2" />
        }}
      />
    </div>
  </Stack>
);

const RightsizingPossibleSavingCell = ({ possibleSaving, possibleSavingPercent }) => {
  const formattedPossibleSaving = <FormattedMoney value={possibleSaving} type={FORMATTED_MONEY_TYPES.COMMON} />;
  const formattedPossibleSavingPercent = <FormattedNumber value={possibleSavingPercent / 100} format="percentage" />;

  return (
    <>
      {formattedPossibleSaving} ({formattedPossibleSavingPercent})
    </>
  );
};

class RightsizingRdsInstances extends BaseRecommendation {
  type = "rightsizing_rds";

  name = "rightsizingRdsInstances";

  title = "rightsizingRdsInstancesRecommendationTitle";

  descriptionMessageId = "rightsizingRdsInstancesRecommendationDescription";

  get descriptionMessageValues() {
    const { days_threshold: daysThreshold, metric: { limit: metricLimit, type: metricType } = {} } = this.options;
    return { daysThreshold, metricLimit, metricType };
  }

  services = [ALIBABA_RDS, NEBIUS_SERVICE];

  categories = [CATEGORY_COST];

  emptyMessageId = "noRightsizingRdsInstances";

  withExclusions = true;

  hasSettings = true;

  settingsSidemodalClass = RightsizingStrategyModal;

  withCleanupScripts = true;

  static resourceDescriptionMessageId = "rightsizingRdsInstancesResourceRecommendation";

  static getResourceDescriptionMessageValues(backendInfo) {
    const { recommended_flavor: flavor } = backendInfo;

    return { size: flavor };
  }

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

  columns = [
    resource({
      headerDataTestId: "lbl_rightsizing_rds_resource"
    }),
    resourceLocation({
      headerDataTestId: "lbl_rightsizing_rds_instance_cloud"
    }),
    rightsizingSize({
      headerDataTestId: "lbl_rightsizing_rds_instance_size"
    }),
    recommendedRightsizingSize({
      messageId: "recommendedSize",
      headerDataTestId: "lbl_rightsizing_rds_instance_recommended_flavor"
    }),
    {
      header: <RightsizingCpuUsageHeaderCell options={this.options} />,
      id: "cpuUsage",
      enableSorting: false,
      cell: ({ row: { original } }) => (
        <RightsizingCpuUsageCell
          currentUsage={{
            cpuUsage: original.cpu_usage,
            cpuPeak: original.cpu_peak,
            cpuQuantile50: original.cpu_quantile_50,
            cpuQuantile99: original.cpu_quantile_99
          }}
          projectedUsage={{
            cpuUsage: original.project_cpu_avg,
            cpuPeak: original.project_cpu_peak,
            cpuQuantile50: original.projected_cpu_qtl_50,
            cpuQuantile99: original.projected_cpu_qtl_99
          }}
        />
      )
    },
    detectedAt({ headerDataTestId: "lbl_rightsizing_rds_instance_detected_at" }),
    {
      header: (
        <TextWithDataTestId dataTestId="lbl_rightsizing_rds_instance_possible_savings">
          <FormattedMessage id="possibleMonthlySavings" />
        </TextWithDataTestId>
      ),
      accessorKey: "saving",
      defaultSort: "desc",
      cell: ({ row: { original } }) => (
        <RightsizingPossibleSavingCell possibleSaving={original.saving} possibleSavingPercent={original.saving_percent} />
      )
    }
  ];
}

export default RightsizingRdsInstances;
