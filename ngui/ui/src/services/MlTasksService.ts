import { useEffect } from "react";
import { useDispatch } from "react-redux";
import {
  getMlTasks,
  RESTAPI,
  getResourceAllowedActions,
  createMlTask,
  deleteMlTask,
  getMlTask,
  getMlTaskRecommendationDetails,
  getMlTaskRuns,
  updateMlTask,
  getMlTaskRecommendations,
  getMlRunDetails,
  getMlRunDetailsBreakdown,
  getMlTaskRunsBulk,
  getMlTaskModelVersions,
  getMlTaskTags
} from "api";
import {
  GET_ML_TASKS,
  CREATE_ML_TASK,
  GET_ML_TASK,
  UPDATE_ML_TASK,
  DELETE_ML_TASK,
  GET_ML_TASK_RUNS,
  GET_ML_RUN_DETAILS,
  GET_ML_RUN_DETAILS_BREAKDOWN,
  GET_ML_OPTIMIZATION_DETAILS,
  GET_ML_TASK_RECOMMENDATIONS,
  GET_ML_TASK_RUNS_BULK,
  GET_ML_TASK_MODEL_VERSIONS,
  GET_ML_TASK_TAGS
} from "api/restapi/actionTypes";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { isEmpty } from "utils/arrays";
import { ModelVersionWithModel } from "./MlModelsService";

const useGetAll = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { tasks = [] }
  } = useApiData(GET_ML_TASKS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_TASKS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTasks(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, tasks };
};

const useGetTaskRecommendations = (taskId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_TASK_RECOMMENDATIONS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_TASK_RECOMMENDATIONS, {
    organizationId,
    taskId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTaskRecommendations(organizationId, taskId));
    }
  }, [shouldInvoke, dispatch, organizationId, taskId]);

  return { isLoading, recommendations: apiData };
};

const useGetTaskRecommendation = ({ taskId, type, status }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: data } = useApiData(GET_ML_OPTIMIZATION_DETAILS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ML_OPTIMIZATION_DETAILS, {
    organizationId,
    taskId,
    type,
    status
  });

  const allRecommendations = useAllRecommendations();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getMlTaskRecommendationDetails(organizationId, taskId, { type, status })).then(() => {
          const newOptimizations = getState()?.[RESTAPI]?.[GET_ML_OPTIMIZATION_DETAILS] ?? {};
          const recommendation = new allRecommendations[type](status, newOptimizations);

          if (!recommendation.dismissable) {
            return;
          }
          const ids = recommendation.items.map(({ resource_id: resourceId }) => resourceId).filter(Boolean);
          if (!isEmpty(ids)) {
            dispatch(getResourceAllowedActions(ids));
          }
        });
      });
    }
  }, [shouldInvoke, dispatch, organizationId, status, type, taskId, allRecommendations]);

  return { isLoading, data };
};

const useCreateTask = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_TASK);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlTask(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_TASK, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateTask = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_TASK);

  const onUpdate = (taskId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlTask(organizationId, taskId, params)).then(() => {
          if (!isError(UPDATE_ML_TASK, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteTask = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_TASK);

  const onDelete = (taskId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlTask(organizationId, taskId)).then(() => {
          if (!isError(DELETE_ML_TASK, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

const useGetOne = (taskId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_TASK);

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_ML_TASK, { organizationId, taskId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTask(organizationId, taskId));
    }
  }, [taskId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, isDataReady, task: apiData };
};

const useGetTaskRunsList = (taskId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_TASK_RUNS, {
    organizationId,
    taskId
  });

  const {
    apiData: { runs = [] }
  } = useApiData(GET_ML_TASK_RUNS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTaskRuns(organizationId, taskId));
    }
  }, [taskId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, isDataReady, runs };
};

const useGetTaskModelVersions = (
  taskId: string
): {
  isLoading: boolean;
  modelVersions: ModelVersionWithModel[];
} => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ML_TASK_MODEL_VERSIONS, {
    organizationId,
    taskId
  });

  const {
    apiData: { model_versions: modelVersions = [] }
  } = useApiData(GET_ML_TASK_MODEL_VERSIONS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTaskModelVersions(organizationId, taskId));
    }
  }, [taskId, dispatch, organizationId, shouldInvoke]);

  return {
    isLoading,
    modelVersions
  };
};

const useGetTaskRunsBulk = (taskId, runIds) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_TASK_RUNS_BULK, {
    organizationId,
    taskId,
    runIds
  });

  const { apiData: runs } = useApiData(GET_ML_TASK_RUNS_BULK, []);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTaskRunsBulk(organizationId, taskId, runIds));
    }
  }, [taskId, dispatch, organizationId, shouldInvoke, runIds]);

  return { isLoading, isDataReady, runs };
};

const useGetTaskRun = (runId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_RUN_DETAILS, { organizationId, runId });

  const { apiData } = useApiData(GET_ML_RUN_DETAILS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunDetails(organizationId, runId));
    }
  }, [dispatch, organizationId, runId, shouldInvoke]);

  return { isLoading, isDataReady, run: apiData };
};

const useGetTaskTags = (taskId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ML_TASK_TAGS, { organizationId, taskId });

  const {
    apiData: { tags = [] }
  } = useApiData(GET_ML_TASK_TAGS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlTaskTags(organizationId, taskId));
    }
  }, [dispatch, organizationId, shouldInvoke, taskId]);

  return { isLoading, tags };
};

const useGetRunBreakdown = (runId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_RUN_DETAILS_BREAKDOWN, {
    organizationId,
    runId
  });

  const {
    apiData: { breakdown = {}, stages = [], milestones = [] }
  } = useApiData(GET_ML_RUN_DETAILS_BREAKDOWN);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunDetailsBreakdown(organizationId, runId));
    }
  }, [dispatch, organizationId, runId, shouldInvoke]);

  return { isLoading, isDataReady, breakdown, stages, milestones };
};

function MlTasksService() {
  return {
    useGetAll,
    useCreateTask,
    useUpdateTask,
    useDeleteTask,
    useGetTaskRecommendation,
    useGetTaskRecommendations,
    useGetTaskRun,
    useGetTaskTags,
    useGetRunBreakdown,
    useGetOne,
    useGetTaskRunsList,
    useGetTaskRunsBulk,
    useGetTaskModelVersions
  };
}

export default MlTasksService;
