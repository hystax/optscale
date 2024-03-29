import GoalLabel from "components/GoalLabel";
import MlRunHistoryChart from "components/MlRunHistoryChart";
import { isEmpty as isEmptyArray } from "utils/arrays";

const LastTaskRunGoals = ({ lastRunMetrics, taskReachedGoals }) =>
  Object.entries(taskReachedGoals).map(([key, { id, name, tendency, value, target_value: targetValue, reached }]) => {
    const { history } = lastRunMetrics.find(({ id: lastRunMetricId }) => lastRunMetricId === id) ?? {};

    const hasHistory = !isEmptyArray(history);

    const shouldRenderHistory = hasHistory && history.length > 1;

    return (
      <div
        key={key}
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          minHeight: "30px"
        }}
      >
        <div
          style={{
            marginRight: shouldRenderHistory ? "8px" : undefined
          }}
        >
          <GoalLabel name={name} goalValue={value} targetGoalValue={targetValue} reached={reached} />
        </div>
        {shouldRenderHistory ? <MlRunHistoryChart history={history} targetValue={targetValue} tendency={tendency} /> : null}
      </div>
    );
  });

export default LastTaskRunGoals;
