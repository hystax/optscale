import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import LineChart from "components/LineChart";
import { EN_FORMAT_SHORT_YEAR, formatUTC } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";

const getBreakdownLine = (breakdown) =>
  Object.entries(breakdown).map(([key, value]) => ({ x: formatUTC(key, EN_FORMAT_SHORT_YEAR), y: value }));

const MlExecutorsBreakdownLineChart = ({ breakdown, isLoading }) => (
  <LineChart
    data={isEmptyObject(breakdown) ? [] : [{ id: "executor_count", data: getBreakdownLine(breakdown) }]}
    renderTooltipBody={({ slice }) => <KeyValueLabel keyMessageId="count" value={slice.points[0].data.y} />}
    isLoading={isLoading}
    style={{ margin: { top: 25, right: 25, left: 70, bottom: 50 } }}
    axisLeft={{
      format: (value) => value
    }}
  />
);

export default MlExecutorsBreakdownLineChart;
