import React from "react";
import PropTypes from "prop-types";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import HeartLineChart from "components/HeartLineChart";
import KeyValueLabel from "components/KeyValueLabel";
import { useGoalMetColors } from "hooks/useGoalMetColors";
import { getAverage } from "utils/arrays";
import { GOALS_FILTER_TYPES } from "utils/constants";

const MlRunHistoryChart = ({ history, targetValue, tendency, width = 100, height = 40, debug = false }) => {
  const { goalMet: goalMetColor, goalNotMet: goalNotMetColor } = useGoalMetColors();

  return (
    <HeartLineChart
      values={history}
      width={width}
      height={height}
      tooltip={
        <>
          <KeyValueLabel messageId="last" value={<DynamicFractionDigitsValue value={history[history.length - 1]} />} />
          <KeyValueLabel messageId="average" value={<DynamicFractionDigitsValue value={getAverage(history)} />} />
        </>
      }
      thresholdArea={{
        start: targetValue,
        end: targetValue
      }}
      thresholdColors={
        tendency === GOALS_FILTER_TYPES.LESS_IS_BETTER
          ? {
              start: goalMetColor,
              end: goalNotMetColor
            }
          : {
              start: goalNotMetColor,
              end: goalMetColor
            }
      }
      debug={debug}
    />
  );
};

MlRunHistoryChart.propTypes = {
  history: PropTypes.array.isRequired,
  targetValue: PropTypes.number.isRequired,
  tendency: PropTypes.oneOf(Object.values(GOALS_FILTER_TYPES)).isRequired,
  width: PropTypes.number,
  height: PropTypes.number,
  debug: PropTypes.func
};

export default MlRunHistoryChart;
