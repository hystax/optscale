import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import {
  getMlModels,
  createGlobalParameter,
  getMlGlobalParameter,
  getMlGlobalParameters,
  updateGlobalParameter,
  deleteGlobalParameter,
  RESTAPI,
  getResourceAllowedActions,
  createMlModel,
  deleteMlModel,
  getMlModel,
  getMlModelRecommendationDetails,
  getMlModelRuns,
  updateMlModel,
  getMlModelRecommendations,
  getMlRunDetails,
  getMlRunDetailsBreakdown
} from "api";
import {
  GET_ML_MODELS,
  CREATE_GLOBAL_PARAMETER,
  GET_ML_GLOBAL_PARAMETER,
  GET_ML_GLOBAL_PARAMETERS,
  UPDATE_GLOBAL_PARAMETER,
  DELETE_GLOBAL_PARAMETER,
  CREATE_ML_MODEL,
  GET_ML_MODEL,
  UPDATE_ML_MODEL,
  DELETE_ML_MODEL,
  GET_ML_MODEL_RUNS,
  GET_ML_RUN_DETAILS,
  GET_ML_RUN_DETAILS_BREAKDOWN,
  GET_ML_OPTIMIZATION_DETAILS,
  GET_ML_MODEL_RECOMMENDATIONS
} from "api/restapi/actionTypes";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";
import { isEmpty } from "utils/arrays";

const useGetAll = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { applications: models = [] }
  } = useApiData(GET_ML_MODELS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_MODELS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModels(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, models };
};

const useGetModelRecommendations = (modelId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_MODEL_RECOMMENDATIONS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_MODEL_RECOMMENDATIONS, {
    organizationId,
    modelId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModelRecommendations(organizationId, modelId));
    }
  }, [shouldInvoke, dispatch, organizationId, modelId]);

  return { isLoading, recommendations: apiData };
};

const useGetModelRecommendation = ({ modelId, type, status }) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData: data } = useApiData(GET_ML_OPTIMIZATION_DETAILS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ML_OPTIMIZATION_DETAILS, {
    organizationId,
    modelId,
    type,
    status
  });

  const allRecommendations = useAllRecommendations();

  useEffect(() => {
    if (shouldInvoke) {
      dispatch((_, getState) => {
        dispatch(getMlModelRecommendationDetails(organizationId, modelId, { type, status })).then(() => {
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
  }, [shouldInvoke, dispatch, organizationId, status, type, modelId, allRecommendations]);

  return { isLoading, data };
};

const useCreateModel = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_MODEL);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlModel(organizationId, params)).then(() => {
          if (!isError(CREATE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateModel = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_ML_MODEL);

  const onUpdate = (modelId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlModel(organizationId, modelId, params)).then(() => {
          if (!isError(UPDATE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteModel = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_ML_MODEL);

  const onDelete = (modelId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlModel(organizationId, modelId)).then(() => {
          if (!isError(DELETE_ML_MODEL, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

const useGetOne = (modelId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_MODEL);

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_ML_MODEL, { organizationId, modelId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModel(organizationId, modelId));
    }
  }, [modelId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, isDataReady, model: apiData };
};

const useGetModelRunsList = (modelId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_ML_MODEL_RUNS, {
    organizationId,
    modelId
  });

  const {
    apiData: { runs = [] }
  } = useApiData(GET_ML_MODEL_RUNS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlModelRuns(organizationId, modelId));
    }
  }, [modelId, dispatch, organizationId, shouldInvoke]);

  return { isLoading, isDataReady, runs };
};

const useGetModelRun = (runId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUN_DETAILS, { organizationId, runId });

  const { apiData } = useApiData(GET_ML_RUN_DETAILS);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunDetails(organizationId, runId));
    }
  }, [dispatch, organizationId, runId, shouldInvoke]);

  return { isLoading, run: apiData };
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

const useGetGlobalParameters = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { goals = [] }
  } = useApiData(GET_ML_GLOBAL_PARAMETERS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_GLOBAL_PARAMETERS, {
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlGlobalParameters(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, parameters: goals };
};

const useAlwaysGetGlobalParameter = (parameterId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const [parameter, setParameter] = useState({});

  const { isLoading } = useApiState(GET_ML_GLOBAL_PARAMETER, {
    organizationId
  });

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(getMlGlobalParameter(organizationId, parameterId)).then(() => {
        const state = getState();
        if (!isError(GET_ML_GLOBAL_PARAMETER, getState())) {
          setParameter(state.restapi[GET_ML_GLOBAL_PARAMETER]);
        }
      });
    });
  }, [dispatch, organizationId, parameterId]);

  return { isLoading, parameter };
};

const useCreateGlobalParameter = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_GLOBAL_PARAMETER);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createGlobalParameter(organizationId, params)).then(() => {
          if (!isError(CREATE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateGlobalParameter = (parameterId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_GLOBAL_PARAMETER);

  const onUpdate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateGlobalParameter(organizationId, parameterId, params)).then(() => {
          if (!isError(UPDATE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteGlobalParameter = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_GLOBAL_PARAMETER);

  const onDelete = (parameterId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteGlobalParameter(organizationId, parameterId)).then(() => {
          if (!isError(DELETE_GLOBAL_PARAMETER, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlModelsService() {
  return {
    useGetAll,
    useCreateModel,
    useUpdateModel,
    useDeleteModel,
    useGetGlobalParameters,
    useGetModelRecommendation,
    useGetModelRecommendations,
    useGetModelRun,
    useGetRunBreakdown,
    useGetOne,
    useGetModelRunsList,
    useCreateGlobalParameter,
    useUpdateGlobalParameter,
    useAlwaysGetGlobalParameter,
    useDeleteGlobalParameter
  };
}

export default MlModelsService;
