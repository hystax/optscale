import { useTheme } from "@mui/material/styles";
import { useIntl } from "react-intl";
import BreakdownLabel, { getBreakdownLabelText } from "components/BreakdownLabel";
import CanvasBarChart from "components/CanvasBarChart";
import { useMoneyFormatter } from "components/FormattedMoney";
import KeyValueChartTooltipBody from "components/KeyValueChartTooltipBody";
import { isEmptyArray, splitIntoTwoChunks } from "utils/arrays";
import { AXIS_FORMATS, getBreakdownChartLegendLabel, getColorsMap } from "utils/charts";
import { EXPENSES_SPLIT_PERIODS, FORMATTED_MONEY_TYPES } from "utils/constants";
import { getResourceExpensesSplits } from "utils/getResourceExpensesSplits";

const OTHER_EXPENSES_NAME = "otherExpenses";
const TOP_KEYS_COUNT = 10;

const getChartDataAndKeys = ({ breakdown, counts, split = EXPENSES_SPLIT_PERIODS.DAILY }) => {
  const countKeys = Object.entries(counts)
    .filter(([, { total }]) => total !== 0)
    .sort(([, { total: a }], [, { total: b }]) => b - a)
    .map(([key]) => key);

  const [topKeys, otherKeys] = splitIntoTwoChunks(countKeys, TOP_KEYS_COUNT);

  const chartKeys = [...(isEmptyArray(otherKeys) ? [] : [OTHER_EXPENSES_NAME]), ...topKeys.toReversed()];

  const getCostById = (data, id) => data.find((item) => item.id === id)?.cost ?? 0;

  const chartData = Object.entries(breakdown).map(([date, data]) => {
    const entry = {
      date,
      ...Object.fromEntries(topKeys.map((id) => [id, getCostById(data, id)])),
    };

    if (!isEmptyArray(otherKeys)) {
      entry[OTHER_EXPENSES_NAME] = otherKeys.reduce((sum, key) => sum + getCostById(data, key), 0);
    }

    return entry;
  });

  const totals = {
    ...Object.fromEntries(topKeys.map((key) => [key, counts[key].total])),
    ...(isEmptyArray(otherKeys)
      ? {}
      : {
          [OTHER_EXPENSES_NAME]: otherKeys.reduce((sum, key) => sum + counts[key].total, 0),
        }),
  };

  return {
    keys: chartKeys,
    data: getResourceExpensesSplits(chartData)[split],
    totals,
  };
};

const ExpensesDailyBreakdownByBarChart = ({
  chartWrapperRef,
  breakdown,
  breakdownBy,
  counts,
  split = EXPENSES_SPLIT_PERIODS.DAILY,
  isLoading = false,
  dataTestId,
  showLegend = false,
}) => {
  const theme = useTheme();

  const intl = useIntl();

  const { keys, data, totals } = getChartDataAndKeys({
    breakdown,
    counts,
    split,
  });

  const moneyFormatter = useMoneyFormatter();

  const colorsMap = getColorsMap(keys.toReversed(), theme.palette.chart);

  const legendLabel = getBreakdownChartLegendLabel({
    getLabel: (legendItem) => {
      if (legendItem.id === OTHER_EXPENSES_NAME) {
        return intl.formatMessage({ id: "other" });
      }
      return getBreakdownLabelText({
        id: legendItem.id,
        ...counts[legendItem.id],
      });
    },
    getTotalLabel: (legendItem) => moneyFormatter(FORMATTED_MONEY_TYPES.COMPACT, totals[legendItem.id]),
  });

  return (
    <CanvasBarChart
      dataTestId={dataTestId}
      wrapperRef={chartWrapperRef}
      indexBy="date"
      keys={keys}
      data={data}
      colorsMap={colorsMap}
      renderTooltipBody={(sectionData) => {
        const { value } = sectionData;

        const details = {
          id: sectionData.id,
          ...counts[sectionData.id],
        };

        const text =
          sectionData.id === OTHER_EXPENSES_NAME ? (
            intl.formatMessage({ id: "other" })
          ) : (
            <BreakdownLabel breakdownBy={breakdownBy} details={details} />
          );

        return <KeyValueChartTooltipBody value={value} text={text} />;
      }}
      isLoading={isLoading}
      axisFormat={AXIS_FORMATS.MONEY}
      withLegend={showLegend}
      legendLabel={legendLabel}
    />
  );
};

export default ExpensesDailyBreakdownByBarChart;
