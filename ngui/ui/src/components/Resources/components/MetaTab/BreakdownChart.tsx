import { useTheme } from "@mui/material/styles";
import { FormattedNumber, useIntl } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import FormattedMoney, { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import { isEmptyArray, splitIntoTwoChunks } from "utils/arrays";
import { AXIS_FORMATS, getBreakdownChartLegendLabel, getColorsMap } from "utils/charts";
import { FORMATTED_MONEY_TYPES, EMPTY_BREAKDOWN_KEY } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";
import { sum } from "utils/math";
import { getMetaFormattedValue } from "utils/metadata";
import { BREAKDOWN_FIELD_NAME, OTHER_CHART_BREAKDOWN_GROUP_NAME, OTHER_THRESHOLD } from "./constants";
import { BreakdownChartProps } from "./types";

const BreakdownChart = ({
  breakdownBy,
  breakdown,
  totals,
  field = BREAKDOWN_FIELD_NAME.COST,
  isPercentBreakdownType,
  withLegend = false,
  isLoading = false,
}: BreakdownChartProps) => {
  const intl = useIntl();
  const theme = useTheme();
  const moneyFormatter = useMoneyFormatter();

  const breakdownTotals = Object.fromEntries(Object.entries(totals).map(([key, datum]) => [key, datum[field] ?? 0]));

  const sortedKeys = Object.entries(breakdownTotals)
    .filter(([, fieldValue]) => fieldValue !== 0)
    .sort(([, valueA], [, valueB]) => valueB - valueA)
    .map(([key]) => key);

  const [topKeys, otherKeys] = splitIntoTwoChunks(sortedKeys, OTHER_THRESHOLD);

  const withOther = !isEmptyArray(otherKeys);

  const chartTotals = Object.fromEntries([
    ...topKeys.map((key) => [key, breakdownTotals[key] ?? 0]),
    ...(withOther ? [[OTHER_CHART_BREAKDOWN_GROUP_NAME, sum(otherKeys.map((key) => breakdownTotals[key] ?? 0))]] : []),
  ]);

  const dailyTotals = Object.fromEntries(
    Object.entries(breakdown).map(([date, datum]) => {
      const values = Object.values(datum).map((item) => item[field] ?? 0);
      return [date, sum(values)];
    })
  );

  const chartData = Object.entries(breakdown).map(([date, datum]) => {
    const processValue = (value: number) => {
      if (isPercentBreakdownType) {
        const total = dailyTotals[date] ?? 0;
        return total === 0 ? 0 : value / total;
      }
      return value;
    };

    const topValues = Object.fromEntries(
      topKeys.map((key) => {
        const value = processValue(datum[key]?.[field] ?? 0);
        return [key, value];
      })
    );

    const otherValue = sum(otherKeys.map((key) => processValue(datum[key]?.[field] ?? 0)));

    return {
      date: formatUTC(date, EN_FORMAT_SHORT_YEAR),
      ...topValues,
      [OTHER_CHART_BREAKDOWN_GROUP_NAME]: otherValue,
    };
  });

  const chartKeys = [...(withOther ? [OTHER_CHART_BREAKDOWN_GROUP_NAME] : []), ...topKeys.toReversed()];

  const getAxisFormat = () => {
    if (isPercentBreakdownType) {
      return AXIS_FORMATS.PERCENTAGE;
    }
    if (field === BREAKDOWN_FIELD_NAME.COST) {
      return AXIS_FORMATS.MONEY;
    }
    return AXIS_FORMATS.RAW;
  };

  const renderTooltipBody = (sectionData: { id: string; value: number }) => {
    const { id: sectionId, value: sectionValue } = sectionData;

    const getText = () => {
      if (sectionId === OTHER_CHART_BREAKDOWN_GROUP_NAME) {
        return intl.formatMessage({ id: "other" });
      }

      return sectionId;
    };

    const getValue = () => {
      if (isPercentBreakdownType) {
        return <FormattedNumber value={sectionValue} format="percentage" />;
      }

      if (field === BREAKDOWN_FIELD_NAME.COST) {
        return <FormattedMoney value={sectionValue} type={FORMATTED_MONEY_TYPES.COMMON} />;
      }

      if (field === BREAKDOWN_FIELD_NAME.COUNT) {
        return <FormattedNumber value={sectionValue} />;
      }

      return sectionValue;
    };

    return <KeyValueLabel value={getValue()} keyText={getText()} />;
  };

  const legendLabel = getBreakdownChartLegendLabel({
    getLabel: (legendItem: { id: string }) => {
      const { id: legendItemId } = legendItem;

      if (legendItemId === OTHER_CHART_BREAKDOWN_GROUP_NAME) {
        return intl.formatMessage({ id: "other" });
      }
      if (legendItemId === EMPTY_BREAKDOWN_KEY.NOT_SET) {
        return intl.formatMessage({ id: "(not set)" });
      }
      if (legendItemId === EMPTY_BREAKDOWN_KEY.NULL) {
        return "null";
      }
      return getMetaFormattedValue(breakdownBy, legendItemId);
    },
    getTotalLabel: (legendItem: { id: string }) => {
      const { id: legendItemId } = legendItem;

      if (field === BREAKDOWN_FIELD_NAME.COST) {
        return moneyFormatter(FORMATTED_MONEY_TYPES.COMPACT, chartTotals[legendItemId]);
      }

      return intl.formatNumber(chartTotals[legendItemId]);
    },
  });

  return (
    <CanvasBarChart
      indexBy="date"
      keys={chartKeys}
      data={chartData}
      colorsMap={getColorsMap(chartKeys, theme.palette.chart)}
      axisFormat={getAxisFormat()}
      palette={theme.palette.chart}
      maxValue={isPercentBreakdownType ? 1 : undefined}
      allocateAdditionalTickAboveMaxValue={isPercentBreakdownType ? false : true}
      renderTooltipBody={renderTooltipBody}
      isLoading={isLoading}
      withLegend={withLegend}
      legendLabel={legendLabel}
    />
  );
};

export default BreakdownChart;
