import { getLast30DaysRange } from "utils/datetime";
import { percentXofY } from "utils/math";
import { useRiSpBreakdowns } from "./useRiSpBreakdowns";

export const useRiSpExpensesSummary = (dataSourceIds) => {
  const { startDate, endDate } = getLast30DaysRange();

  const { isLoading, expensesBreakdown } = useRiSpBreakdowns({
    startDate,
    endDate,
    dataSourceIds
  });

  const summary = Object.values(expensesBreakdown)
    .flatMap((breakdownDatum) => breakdownDatum)
    .reduce(
      (acc, { total: { cost_with_offer: costWithOffer, cost_without_offer: costWithoutOffer }, ri, sp }) => {
        const totalCostWithOffer = acc.totalCostWithOffer + costWithOffer;

        const totalSaving = acc.totalSaving + (costWithoutOffer - costWithOffer);

        const computeExpensesCoveredWithCommitments =
          acc.computeExpensesCoveredWithCommitments + ri.cost_with_offer + sp.cost_with_offer;

        return { totalCostWithOffer, totalSaving, computeExpensesCoveredWithCommitments };
      },
      { totalCostWithOffer: 0, totalSaving: 0, computeExpensesCoveredWithCommitments: 0 }
    );

  return {
    isLoading,
    summary: {
      ...summary,
      computeExpensesCoveredWithCommitments: percentXofY(
        summary.computeExpensesCoveredWithCommitments,
        summary.totalCostWithOffer
      )
    }
  };
};
