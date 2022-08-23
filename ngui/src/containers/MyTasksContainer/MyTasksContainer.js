import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { getMyTasks } from "api";
import { GET_MY_TASKS } from "api/restapi/actionTypes";
import MyTasks from "components/MyTasks";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInitialMount } from "hooks/useInitialMount";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import {
  TASK_INCOMING_ASSIGNMENT_REQUESTS,
  TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  TASK_EXCEEDED_POOLS,
  TASK_EXCEEDED_POOL_FORECASTS,
  TASK_VIOLATED_RESOURCE_CONSTRAINTS,
  TASK_VIOLATED_ORGANIZATION_CONSTRAINTS,
  TASK_DIVERGENT_CONSTRAINTS,
  MAP_MY_TASKS_TYPES
} from "utils/constants";
import { getPathname, setQueryParams, getQueryParams, getStringUrl } from "utils/network";
import { isEmpty as isEmptyObject } from "utils/objects";

const updateTaskQueryParams = (taskName, currentUrl) => {
  const search = taskName ? getStringUrl({ task: taskName }) : currentUrl;
  setQueryParams(search);
};

const MyTasksContainer = () => {
  const { organizationId } = useOrganizationInfo();
  const currentUrl = getPathname();
  const queryParams = getQueryParams();
  const hasTaskTypeInUrl = !!queryParams?.task;
  const task = hasTaskTypeInUrl ? queryParams.task : "";

  const dispatch = useDispatch();

  const {
    apiData: { myTasks = {} }
  } = useApiData(GET_MY_TASKS);

  const [expanded, setExpanded] = useState({
    [TASK_INCOMING_ASSIGNMENT_REQUESTS]: false,
    [TASK_OUTGOING_ASSIGNMENT_REQUESTS]: false,
    [TASK_EXCEEDED_POOLS]: false,
    [TASK_EXCEEDED_POOL_FORECASTS]: false,
    [TASK_VIOLATED_RESOURCE_CONSTRAINTS]: false,
    [TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]: false,
    [TASK_DIVERGENT_CONSTRAINTS]: false
  });
  const { isLoading } = useApiState(GET_MY_TASKS);

  const { isInitialMount, setIsInitialMount } = useInitialMount();

  const updateExpanded = (taskName) => {
    setExpanded((prevState) => ({
      ...{
        ...prevState,
        ...{
          [TASK_INCOMING_ASSIGNMENT_REQUESTS]: false,
          [TASK_OUTGOING_ASSIGNMENT_REQUESTS]: false,
          [TASK_EXCEEDED_POOLS]: false,
          [TASK_EXCEEDED_POOL_FORECASTS]: false,
          [TASK_VIOLATED_RESOURCE_CONSTRAINTS]: false,
          [TASK_VIOLATED_ORGANIZATION_CONSTRAINTS]: false,
          [TASK_DIVERGENT_CONSTRAINTS]: false
        },
        [taskName]: !prevState[taskName]
      }
    }));
  };

  useEffect(() => {
    if (isInitialMount && !hasTaskTypeInUrl) {
      dispatch(getMyTasks({ organizationId }));
    }
    if (isInitialMount && hasTaskTypeInUrl) {
      updateExpanded(task);
      dispatch(getMyTasks({ organizationId, type: MAP_MY_TASKS_TYPES[task] }));
    }
    setIsInitialMount(false);
  }, [dispatch, organizationId, hasTaskTypeInUrl, isInitialMount, setIsInitialMount, task]);

  const handleChange = (taskName) => {
    updateTaskQueryParams(taskName, currentUrl);
    updateExpanded(taskName);
    if (taskName) {
      dispatch(getMyTasks({ organizationId, type: MAP_MY_TASKS_TYPES[taskName] }));
    }
  };

  return (
    <MyTasks
      isLoading={isLoading}
      isEmpty={isEmptyObject(myTasks)}
      data={myTasks}
      expanded={expanded}
      hasTaskTypeInUrl={hasTaskTypeInUrl}
      handleChange={handleChange}
    />
  );
};

export default MyTasksContainer;
