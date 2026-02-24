import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import HeartLineChart from "components/HeartLineChart";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import MetricUnitLabel from "components/MetricUnitLabel";
import { useGoalMetColors } from "hooks/useGoalMetColors";
import { getAverage } from "utils/arrays";
import { GOALS_FILTER_TYPES } from "utils/constants";

const MlRunHistoryChart = ({ history, targetValue, tendency, width = 100, height = 40, debug = false, unit }) => {
  const { goalMet: goalMetColor, goalNotMet: goalNotMetColor } = useGoalMetColors();

  return (
    <HeartLineChart
      values={history}
      width={width}
      height={height}
      tooltip={
        <>
          <KeyValueLabel
            keyMessageId="last"
            value={<MetricUnitLabel label={<DynamicFractionDigitsValue value={history[history.length - 1]} />} unit={unit} />}
          />
          <KeyValueLabel
            keyMessageId="average"
            value={<MetricUnitLabel label={<DynamicFractionDigitsValue value={getAverage(history)} />} unit={unit} />}
          />
        </>
      }
      thresholdArea={{
        start: targetValue,
        end: targetValue,
      }}
      thresholdColors={
        tendency === GOALS_FILTER_TYPES.LESS_IS_BETTER
          ? {
              start: goalMetColor,
              end: goalNotMetColor,
            }
          : {
              start: goalNotMetColor,
              end: goalMetColor,
            }
      }
      debug={debug}
    />
  );
};

export default MlRunHistoryChart;
