import { useMemo } from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import CircleLabel from "components/CircleLabel";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { RI_SP_CHART_PALETTE } from "theme";
import { AXIS_FORMATS } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";

const getChartData = (breakdown) =>
  Object.entries(breakdown).reduce((data, [key, value]) => {
    const temp = value.reduce(
      (result, item) => {
        const {
          sp: { cost_with_offer: itemSpCostWithOffer },
          ri: { cost_with_offer: itemRiCostWithOffer },
          total: { cost_with_offer: itemTotalCostWithOffer, cost_without_offer: itemTotalCostWithoutOffer }
        } = item;

        const {
          sp_cost_with_offer: spCostWithOffer,
          ri_cost_with_offer: riCostWithOffer,
          total_cost_with_offer: totalCostWithOffer,
          total_cost_without_offer: totalCostWithoutOffer
        } = result;

        const spCostHrsAggregated = spCostWithOffer + itemSpCostWithOffer;
        const riCostHrsAggregated = riCostWithOffer + itemRiCostWithOffer;
        const totalCostWithHrsAggregated = totalCostWithOffer + itemTotalCostWithOffer;
        const totalCostWithoutHrsAggregated = totalCostWithoutOffer + itemTotalCostWithoutOffer;

        return {
          ...result,
          ...{
            sp_cost_with_offer: spCostHrsAggregated,
            ri_cost_with_offer: riCostHrsAggregated,
            total_cost_with_offer: totalCostWithHrsAggregated,
            total_cost_without_offer: totalCostWithoutHrsAggregated
          }
        };
      },
      {
        ri_cost_with_offer: 0,
        sp_cost_with_offer: 0,
        total_cost_with_offer: 0,
        total_cost_without_offer: 0
      }
    );

    const {
      sp_cost_with_offer: tempSpCostWithOffer,
      ri_cost_with_offer: tempRiCostWithOffer,
      total_cost_with_offer: tempTotalCostWithOffer,
      total_cost_without_offer: tempTotalCostWithoutOffer
    } = temp;

    const finalItem = {
      ...temp,
      date: formatUTC(key, EN_FORMAT_SHORT_YEAR),
      sp_expenses: tempSpCostWithOffer,
      ri_expenses: tempRiCostWithOffer,
      total_expenses: tempTotalCostWithOffer,
      total_savings: tempTotalCostWithoutOffer - tempTotalCostWithOffer,
      uncovered_expenses: tempTotalCostWithOffer - tempSpCostWithOffer - tempRiCostWithOffer
    };

    return [...data, finalItem];
  }, []);

const getTooltipItem = (id, paletteColorIndex, value) => ({
  itemKey: id,
  keyText:
    paletteColorIndex === null ? (
      <FormattedMessage id={id} />
    ) : (
      <CircleLabel
        figureColor={RI_SP_CHART_PALETTE[paletteColorIndex]}
        label={<FormattedMessage id={id} />}
        textFirst={false}
      />
    ),
  value: <FormattedMoney type={FORMATTED_MONEY_TYPES.COMMON} value={value} />
});

export const RI_SP_EXPENSES_COLOR_INDEXES = {
  SP_EXPENSES: 0,
  RI_EXPENSES: 1,
  UNCOVERED_EXPENSES: 2,
  SAVINGS: 3
};

const getRenderTooltipBody = (sectionData, showSavings) => {
  const {
    data: {
      date,
      sp_cost_with_offer: spCostWithOffer = 0,
      ri_cost_with_offer: riCostWithOffer = 0,
      total_cost_with_offer: totalCostWithOffer = 0,
      total_cost_without_offer: totalCostWithoutOffer = 0,
      uncovered_expenses: uncoveredExpenses = 0
    }
  } = sectionData;

  const items = [
    getTooltipItem("totalExpenses", null, uncoveredExpenses + spCostWithOffer + riCostWithOffer),
    showSavings && getTooltipItem("savings", RI_SP_EXPENSES_COLOR_INDEXES.SAVINGS, totalCostWithoutOffer - totalCostWithOffer),
    getTooltipItem("uncoveredExpenses", RI_SP_EXPENSES_COLOR_INDEXES.UNCOVERED_EXPENSES, uncoveredExpenses),
    getTooltipItem("riExpenses", RI_SP_EXPENSES_COLOR_INDEXES.RI_EXPENSES, riCostWithOffer),
    getTooltipItem("spExpenses", RI_SP_EXPENSES_COLOR_INDEXES.SP_EXPENSES, spCostWithOffer)
  ].filter(Boolean);

  return (
    <div>
      <Typography gutterBottom>{date}</Typography>
      {items.map(({ key, keyText, value }) => (
        <KeyValueLabel key={key} keyText={keyText} value={value} />
      ))}
    </div>
  );
};

const RiSpExpensesBarChart = ({ breakdown, isLoading = false, showSavings = false }) => {
  const data = useMemo(() => getChartData(breakdown), [breakdown]);

  const chartKeys = ["sp_expenses", "ri_expenses", "uncovered_expenses", showSavings && "total_savings"].filter(Boolean);

  const hasExpenses = data.some((datum) => chartKeys.some((key) => datum[key] && datum[key] !== 0));

  return (
    <CanvasBarChart
      dataTestId="ri_sp_expenses_breakdown_chart"
      indexBy="date"
      data={hasExpenses ? data : []}
      keys={chartKeys}
      emptyMessageId="noExpenses"
      renderTooltipBody={(sectionData) => getRenderTooltipBody(sectionData, showSavings)}
      margin={{ top: 30, right: 10, bottom: 30, left: 40 }}
      axisFormat={AXIS_FORMATS.MONEY}
      isLoading={isLoading}
      palette={RI_SP_CHART_PALETTE}
    />
  );
};

export default RiSpExpensesBarChart;
