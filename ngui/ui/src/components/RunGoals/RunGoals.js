import React from "react";
import PropTypes from "prop-types";
import GoalLabel from "components/GoalLabel";

const RunGoals = ({ goals = {} }) =>
  Object.entries(goals).map(([key, { name, value, target_value: targetValue, reached }]) => (
    <div key={key}>
      <GoalLabel name={name} goalValue={value} targetGoalValue={targetValue} reached={reached} />
    </div>
  ));

RunGoals.propTypes = {
  goals: PropTypes.array
};

export default RunGoals;
