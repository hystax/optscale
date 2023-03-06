import React from "react";
import PropTypes from "prop-types";
import GoalLabel from "components/GoalLabel";

const RunGoals = ({ goals, runData = {} }) =>
  goals.map(({ key, name, tendency, target_value: targetValue }) => {
    const goalValue = runData[key];
    return (
      <div key={key}>
        <GoalLabel name={name} tendency={tendency} goalValue={goalValue} targetGoalValue={targetValue} />
      </div>
    );
  });

RunGoals.propTypes = {
  goals: PropTypes.array,
  runData: PropTypes.object
};

export default RunGoals;
