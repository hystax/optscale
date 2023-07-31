import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import CircleLabel from "components/CircleLabel";
import KeyValueLabelsList from "components/KeyValueLabelsList";
import { RI_SP_CHART_PALETTE } from "theme";
import { AXIS_FORMATS } from "utils/charts";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";
import { percentXofY } from "utils/math";

const getChartData = (breakdown) =>
  Object.entries(breakdown).reduce((data, [key, value]) => {
    const temp = value.reduce(
      (result, item) => {
        const { sp_usage_hrs: itemSpUsageHrs, ri_usage_hrs: itemRiUsageHrs, total_usage_hrs: itemTotalUsageHrs } = item;
        const { sp_usage_hrs: spUsageHrs, ri_usage_hrs: riUsageHrs, total_usage_hrs: totalUsageHrs } = result;

        const spUsageHrsAggregated = spUsageHrs + itemSpUsageHrs;
        const riUsageHrsAggregated = riUsageHrs + itemRiUsageHrs;
        const totalUsageHrsAggregated = totalUsageHrs + itemTotalUsageHrs;

        return {
          ...result,
          ...{
            sp_usage_hrs: spUsageHrsAggregated,
            ri_usage_hrs: riUsageHrsAggregated,
            total_usage_hrs: totalUsageHrsAggregated
          }
        };
      },
      {
        ri_usage_hrs: 0,
        sp_usage_hrs: 0,
        total_usage_hrs: 0
      }
    );

    const { sp_usage_hrs: tempSpUsageHrs, ri_usage_hrs: tempRiUsageHrs, total_usage_hrs: tempTotalUsageHrs } = temp;

    const spUsagePercent = percentXofY(tempSpUsageHrs, tempTotalUsageHrs);
    const riUsagePercent = percentXofY(tempRiUsageHrs, tempTotalUsageHrs);

    const finalItem = {
      ...temp,
      date: formatUTC(key, EN_FORMAT_SHORT_YEAR),
      sp_usage_percent: spUsagePercent,
      ri_usage_percent: riUsagePercent,
      // intPercentXofY works not as expected when working with floating numbers
      // When is it essential to have 100% as a sum of all the addends
      uncovered_usage_percent: 1 - spUsagePercent - riUsagePercent
    };

    return [...data, finalItem];
  }, []);

const getTooltipItem = (id, paletteColorIndex, value) => ({
  itemKey: id,
  renderKey: () => (
    <CircleLabel figureColor={RI_SP_CHART_PALETTE[paletteColorIndex]} label={<FormattedMessage id={id} />} textFirst={false} />
  ),
  value: <FormattedNumber value={value} format="percentage" />
});

export const RI_SP_COVERAGE_COLOR_INDEXES = {
  SP_USAGE: 0,
  RI_USAGE: 1,
  UNCOVERED_USAGE: 2
};

const getRenderTooltipBody = (sectionData) => {
  const {
    data: {
      sp_usage_percent: spUsagePercent = 0,
      ri_usage_percent: riUsagePercent = 0,
      uncovered_usage_percent: uncoveredUsagePercent = 0
    }
  } = sectionData;

  const items = [
    getTooltipItem("uncoveredUsage", RI_SP_COVERAGE_COLOR_INDEXES.UNCOVERED_USAGE, uncoveredUsagePercent),
    getTooltipItem("riUsage", RI_SP_COVERAGE_COLOR_INDEXES.RI_USAGE, riUsagePercent),
    getTooltipItem("spUsage", RI_SP_COVERAGE_COLOR_INDEXES.SP_USAGE, spUsagePercent)
  ];

  return <KeyValueLabelsList items={items} />;
};

const RiSpCoverageBarChart = ({ breakdown, isLoading = false }) => {
  const data = useMemo(() => getChartData(breakdown), [breakdown]);

  const hasUsage = data.some((datum) => datum.total_usage_hrs && datum.total_usage_hrs !== 0);

  return (
    <CanvasBarChart
      dataTestId="ri_sp_coverage_breakdown_chart"
      indexBy="date"
      data={hasUsage ? data : []}
      emptyMessageId="noUsage"
      keys={["sp_usage_percent", "ri_usage_percent", "uncovered_usage_percent"]}
      renderTooltipBody={getRenderTooltipBody}
      minMaxTicksEqualToMinMaxValues
      margin={{ top: 30, right: 0, bottom: 30, left: 40 }}
      axisFormat={AXIS_FORMATS.PERCENTAGE}
      isLoading={isLoading}
      palette={RI_SP_CHART_PALETTE}
    />
  );
};

RiSpCoverageBarChart.propTypes = {
  breakdown: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default RiSpCoverageBarChart;
