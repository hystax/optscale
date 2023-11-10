import { useMemo } from "react";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import { dataSource, riExpenses, riUsage, savings, spExpenses, spUsage, totalExpenses, totalUsage } from "./columns";

const getData = (breakdown) => {
  const tableData = Object.values(breakdown).reduce((res, item) => {
    const index = res.findIndex((dataItem) => dataItem.cloud_account_id === item.cloud_account_id);
    if (index !== -1) {
      const {
        sp_usage_hrs: spUsageHrs = 0,
        ri_usage_hrs: riUsageHours = 0,
        total_usage_hrs: totalUsageHrs = 0,
        sp_cost_with_offer: spCostWithOffer = 0,
        ri_cost_with_offer: riCostWithOffer = 0,
        total_cost_with_offer: totalCostWithOffer = 0,
        total_cost_without_offer: totalCostWithoutOffer = 0
      } = res[index];

      const {
        sp_usage_hrs: itemSpUsageHrs = 0,
        ri_usage_hrs: itemRiUsageHours = 0,
        total_usage_hrs: itemTotalUsageHrs = 0,
        sp: { cost_with_offer: itemSpCostWithOffer = 0 } = {},
        ri: { cost_with_offer: itemRiCostWithOffer = 0 } = {},
        total: { cost_with_offer: itemTotalCostWithOffer = 0, cost_without_offer: itemTotalCostWithoutOffer = 0 } = {}
      } = item;

      res[index] = {
        ...res[index],
        sp_usage_hrs: spUsageHrs + itemSpUsageHrs,
        ri_usage_hrs: riUsageHours + itemRiUsageHours,
        total_usage_hrs: totalUsageHrs + itemTotalUsageHrs,
        sp_cost_with_offer: spCostWithOffer + itemSpCostWithOffer,
        ri_cost_with_offer: riCostWithOffer + itemRiCostWithOffer,
        total_cost_with_offer: totalCostWithOffer + itemTotalCostWithOffer,
        total_cost_without_offer: totalCostWithoutOffer + itemTotalCostWithoutOffer
      };

      return res;
    }

    return [...res, item];
  }, []);

  const totals = tableData.reduce(
    (acc, datum) => ({
      total_sp_usage_hrs: acc.total_sp_usage_hrs + datum.sp_usage_hrs ?? 0,
      total_ri_usage_hrs: acc.total_ri_usage_hrs + datum.ri_usage_hrs ?? 0,
      total_total_usage_hrs: acc.total_total_usage_hrs + datum.total_usage_hrs ?? 0,
      total_sp_cost_with_offer: acc.total_sp_cost_with_offer + datum.sp_cost_with_offer ?? 0,
      total_ri_cost_with_offer: acc.total_ri_cost_with_offer + datum.ri_cost_with_offer ?? 0,
      total_total_cost_with_offer: acc.total_total_cost_with_offer + datum.total_cost_with_offer ?? 0,
      total_total_cost_without_offer: acc.total_total_cost_without_offer + datum.total_cost_without_offer ?? 0
    }),
    {
      total_sp_usage_hrs: 0,
      total_ri_usage_hrs: 0,
      total_total_usage_hrs: 0,
      total_sp_cost_with_offer: 0,
      total_ri_cost_with_offer: 0,
      total_total_cost_with_offer: 0,
      total_total_cost_without_offer: 0
    }
  );

  return {
    tableData,
    totals
  };
};

const RiSpCoverageTable = ({ breakdown, isLoading = false }) => {
  const { tableData, totals } = useMemo(() => getData(breakdown), [breakdown]);

  const columns = useMemo(
    () => [
      dataSource(),
      spUsage({
        totalSpUsageHrs: totals.total_sp_usage_hrs,
        totalTotalUsageHrs: totals.total_total_usage_hrs
      }),
      riUsage({
        totalRiUsageHrs: totals.total_ri_usage_hrs,
        totalTotalUsageHrs: totals.total_total_usage_hrs
      }),
      totalUsage({
        totalTotalUsageHrs: totals.total_total_usage_hrs
      }),
      spExpenses({
        totalSpCostWithOffer: totals.total_sp_cost_with_offer,
        totalTotalCostWithOffer: totals.total_total_cost_with_offer
      }),
      riExpenses({
        totalRiCostWithOffer: totals.total_ri_cost_with_offer,
        totalTotalCostWithOffer: totals.total_total_cost_with_offer
      }),
      savings({
        totalTotalCostWithoutOffer: totals.total_total_cost_without_offer,
        totalTotalCostWithOffer: totals.total_total_cost_with_offer
      }),
      totalExpenses({
        totalTotalCostWithOffer: totals.total_total_cost_with_offer
      })
    ],
    [totals]
  );

  return isLoading ? (
    <TableLoader showHeader />
  ) : (
    <>
      <Table
        data={tableData}
        withFooter
        localization={{
          emptyMessageId: "noRiSpUsageData"
        }}
        columns={columns}
        dataTestIds={{
          container: "table_ri_sp_usage"
        }}
      />
    </>
  );
};

export default RiSpCoverageTable;
