import { Typography } from "@mui/material";
import CircleLabel from "components/CircleLabel";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LineChart from "components/LineChart";
import { useMlBreakdownLines } from "hooks/useMlBreakdownLines";
import { formatRunFullName, formatRunNumber } from "utils/ml";

const CHART_MARGIN_STYLES = Object.freeze({ top: 20, right: 60, left: 60, bottom: 50 });

const Chart = ({ runs = [], breakdownConfig = [], selectedBreakdowns = [], isLoading, getRunNameByNumber, colors }) => {
  const breakdownLines = useMlBreakdownLines({
    breakdown: Object.fromEntries(runs.map((run) => [run.number, run])),
    breakdownConfig,
    selectedBreakdowns
  });

  return (
    <LineChart
      isLoading={isLoading}
      data={breakdownLines}
      xScale={{
        type: "linear",
        min: "auto"
      }}
      renderTooltipBody={({ slice: { points = [] } = {} }) => {
        const { x: runNumber } = points[0]?.data ?? {};

        return (
          <div>
            <Typography fontWeight="bold" gutterBottom>
              {formatRunFullName(runNumber, getRunNameByNumber(runNumber))}
            </Typography>
            {points.map((point) => (
              <KeyValueLabel
                key={point.id}
                keyText={<CircleLabel figureColor={point.serieColor} label={point.data.formattedLineName} textFirst={false} />}
                value={point.data.formattedY}
                gutterBottom
              />
            ))}
          </div>
        );
      }}
      colors={colors}
      style={{
        margin: CHART_MARGIN_STYLES
      }}
      axisLeft={
        [1, 2].includes(breakdownLines.length)
          ? {
              format: breakdownLines[0].formatAxis
            }
          : null
      }
      axisRight={
        breakdownLines.length === 2
          ? {
              format: breakdownLines[1].formatAxis
            }
          : null
      }
      animate={false}
      axisBottom={{
        format: (runNumber) => formatRunNumber(runNumber),
        formatString: (runNumber) => formatRunNumber(runNumber)
      }}
    />
  );
};

export default Chart;
