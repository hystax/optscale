import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setTaskRunsDashboardId } from "./actionCreator";
import { TASK_RUNS_DASHBOARD } from "./reducer";

export const useTaskRunsDashboardState = (taskId) => {
  const dispatch = useDispatch();

  const dashboardId = useSelector((state) => {
    const storeData = state[TASK_RUNS_DASHBOARD]?.[taskId] ?? "default";

    return storeData;
  });

  const setDashboardId = useCallback(
    (newDashboardId) => {
      dispatch(
        setTaskRunsDashboardId({
          taskId,
          dashboardId: newDashboardId
        })
      );
    },
    [dispatch, taskId]
  );

  return {
    dashboardId,
    setDashboardId
  };
};
