import RiSpService from "services/RiSpService";

const BREAKDOWN_TYPES = Object.freeze({
  USAGE: "usage",
  COST: "cost"
});

type BreakdownType = (typeof BREAKDOWN_TYPES)[keyof typeof BREAKDOWN_TYPES];

const getBreakdown = ({ riBreakdown, spBreakdown, breakdownType }: { breakdownType: BreakdownType }) => {
  if (!riBreakdown.breakdown || !spBreakdown.breakdown) {
    return {};
  }

  const breakdownDates = Object.keys(spBreakdown.breakdown);

  const dataSourceIds =
    Object.values(spBreakdown.breakdown)?.[0].map((breakdownDatum) => breakdownDatum.cloud_account_id) ?? [];

  return Object.fromEntries(
    breakdownDates.map((date) => [
      date,
      dataSourceIds.map((dataSourceId) => {
        const spCloudAccountBreakdown = spBreakdown.breakdown[date]?.find(
          (breakdown) => breakdown.cloud_account_id === dataSourceId
        );
        const riCloudAccountBreakdown = riBreakdown.breakdown[date]?.find(
          (breakdown) => breakdown.cloud_account_id === dataSourceId
        );

        return {
          cloud_account_id: dataSourceId,
          cloud_account_type: spCloudAccountBreakdown?.cloud_account_type,
          cloud_account_name: spCloudAccountBreakdown?.cloud_account_name,
          ...(breakdownType === BREAKDOWN_TYPES.USAGE && {
            total_usage_hrs: spCloudAccountBreakdown?.total_usage_hrs ?? 0,
            ri_usage_hrs: spCloudAccountBreakdown?.sp_usage_hrs ?? 0,
            sp_usage_hrs: riCloudAccountBreakdown?.ri_usage_hrs ?? 0
          }),
          ...(breakdownType === BREAKDOWN_TYPES.COST && {
            ri: {
              cost_with_offer: riCloudAccountBreakdown?.ri_cost_with_offer ?? 0,
              cost_without_offer: riCloudAccountBreakdown?.ri_cost_without_offer ?? 0
            },
            sp: {
              cost_with_offer: spCloudAccountBreakdown?.sp_cost_with_offer ?? 0,
              cost_without_offer: spCloudAccountBreakdown?.sp_cost_without_offer ?? 0
            },
            total: {
              cost_with_offer: spCloudAccountBreakdown?.cost_with_offer ?? 0,
              cost_without_offer: spCloudAccountBreakdown?.cost_without_offer ?? 0
            }
          })
        };
      })
    ])
  );
};

export const useRiSpBreakdowns = ({
  startDate,
  endDate,
  dataSourceIds
}: {
  startDate: number;
  endDate: number;
  dataSourceIds: string[];
}) => {
  const { useGetSavingPlansBreakdown, useGetReservedInstancesBreakdown } = RiSpService();

  const { isLoading: isGetReservedInstancesBreakdown, breakdown: rightSizingInstancesBreakdown } =
    useGetReservedInstancesBreakdown(startDate, endDate, dataSourceIds);

  const { isLoading: isGetSavingPlansBreakdown, breakdown: savingPlansBreakdown } = useGetSavingPlansBreakdown(
    startDate,
    endDate,
    dataSourceIds
  );

  const usageBreakdown = getBreakdown({
    riBreakdown: rightSizingInstancesBreakdown,
    spBreakdown: savingPlansBreakdown,
    breakdownType: BREAKDOWN_TYPES.USAGE
  });

  const expensesBreakdown = getBreakdown({
    riBreakdown: rightSizingInstancesBreakdown,
    spBreakdown: savingPlansBreakdown,
    breakdownType: BREAKDOWN_TYPES.COST
  });

  return {
    isLoading: isGetReservedInstancesBreakdown || isGetSavingPlansBreakdown,
    expensesBreakdown,
    usageBreakdown
  };
};
