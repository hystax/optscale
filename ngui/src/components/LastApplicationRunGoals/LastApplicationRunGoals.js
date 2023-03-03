import React from "react";
import PropTypes from "prop-types";
import GoalLabel from "components/GoalLabel";
import HeartLineChart from "components/HeartLineChart";
import { isEmpty as isEmptyArray } from "utils/arrays";

const History = ({ history }) => <HeartLineChart values={history} redZoneValue={0} width={100} height={20} />;

const LastApplicationRunGoals = ({ applicationGoals, lastRunGoals, withHistory = false }) =>
  applicationGoals.map(({ name, tendency, target_value: targetValue, id }) => {
    const { last_run_value: lastRunValue, history } = lastRunGoals.find(({ id: lastRunGoalId }) => lastRunGoalId === id) ?? {};

    const hasHistory = !isEmptyArray(history);

    const shouldRenderHistory = withHistory && hasHistory;

    return (
      <div
        key={name}
        style={{
          display: "flex",
          alignItems: "center",
          height: withHistory ? "30px" : undefined
        }}
      >
        <div
          style={{
            marginRight: shouldRenderHistory ? "8px" : undefined
          }}
        >
          <GoalLabel name={name} tendency={tendency} goalValue={lastRunValue} targetGoalValue={targetValue} />
        </div>
        {shouldRenderHistory ? <History history={history} /> : null}
      </div>
    );
  });

LastApplicationRunGoals.propTypes = {
  applicationGoals: PropTypes.array.isRequired,
  lastRunGoals: PropTypes.array.isRequired,
  withHistory: PropTypes.bool
};

export default LastApplicationRunGoals;
