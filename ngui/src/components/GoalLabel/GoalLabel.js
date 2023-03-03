import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import KeyValueLabel from "components/KeyValueLabel";
import { GOALS_FILTER_TYPES, GOAL_STATUS } from "utils/constants";
import { intPercentXofY } from "utils/math";

const getGoalStatusByGoalType = (percent = 0, tendency) => {
  if (percent < 100) {
    return tendency === GOALS_FILTER_TYPES.MORE_IS_BETTER ? GOAL_STATUS.NOT_MET : GOAL_STATUS.MET;
  }
  return tendency === GOALS_FILTER_TYPES.MORE_IS_BETTER ? GOAL_STATUS.MET : GOAL_STATUS.NOT_MET;
};

const GoalLabel = ({ name, tendency, goalValue, targetGoalValue }) => {
  const percent = intPercentXofY(goalValue, targetGoalValue);
  const goalStatus = getGoalStatusByGoalType(percent, tendency);

  return (
    <KeyValueLabel
      text={name}
      value={
        goalValue !== undefined ? (
          <CircleLabel
            figureColor={goalStatus === GOAL_STATUS.MET ? "success" : "warning"}
            label={
              <FormattedMessage
                id="{value}OutOf{defaultValue}"
                values={{
                  value: <DynamicFractionDigitsValue value={goalValue} />,
                  defaultValue: <DynamicFractionDigitsValue value={targetGoalValue} />
                }}
              />
            }
            tooltip={{ show: true, messageId: goalStatus }}
            textFirst={false}
          />
        ) : undefined
      }
    />
  );
};

GoalLabel.propTypes = {
  name: PropTypes.string,
  tendency: PropTypes.string,
  goalValue: PropTypes.number,
  targetGoalValue: PropTypes.number
};

export default GoalLabel;
