import React from "react";
import Grid from "@mui/material/Grid";
import PropTypes from "prop-types";
import LineChart from "components/LineChart";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { EN_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import MetricChartTooltip from "../MetricChartTooltip";
import MetricLegend from "../MetricLegend";

const MetricChart = ({ lines, formatYAxis, emptyMessageId, legend, yFormat, isLoading, marginLeft = 60, dataTestId }) => (
  <Grid container spacing={SPACING_2}>
    <Grid item xs={12}>
      {isLoading || !isEmptyArray(legend) ? <MetricLegend legend={legend} isLoading={isLoading} /> : null}
    </Grid>
    <Grid item xs={12}>
      <LineChart
        data={lines}
        style={{
          height: 25,
          margin: {
            left: marginLeft,
            top: 5,
            bottom: 20,
            right: 32
          }
        }}
        axisLeft={{
          format: formatYAxis
        }}
        colors={({ color }) => color}
        pointSize={1}
        shouldRenderOnlyFirstAndLastBottomTickValues
        renderTooltipBody={({ slice }) => <MetricChartTooltip slice={slice} />}
        axisBottom={{
          format: (value) => unixTimestampToDateTime(value, EN_FORMAT)
        }}
        isLoading={isLoading}
        yFormat={yFormat}
        dataTestId={dataTestId}
        emptyMessageId={emptyMessageId}
      />
    </Grid>
  </Grid>
);

MetricChart.propTypes = {
  lines: PropTypes.array.isRequired,
  legend: PropTypes.array,
  formatYAxis: PropTypes.func,
  isLoading: PropTypes.bool,
  marginLeft: PropTypes.number,
  yFormat: PropTypes.func,
  dataTestId: PropTypes.string,
  emptyMessageId: PropTypes.string
};

export default MetricChart;
