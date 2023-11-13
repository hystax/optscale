import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { createMlRunset, getMlRunset, getMlRunsetExecutors, getMlRunsetsRuns, getMlRunsets } from "api";
import { stopMlRunset } from "api/restapi/actionCreators";
import {
  CREATE_ML_RUNSET,
  GET_ML_RUNSET,
  GET_ML_RUNSETS,
  GET_ML_RUNSETS_RUNS,
  GET_ML_RUNSET_EXECUTORS,
  STOP_ML_RUNSET
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetAll = (runsetTemplateId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { runsets = [], total_runs: runsCount, total_cost: totalCost, last_runset_cost: lastRunsetCost }
  } = useApiData(GET_ML_RUNSETS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSETS, { organizationId, runsetTemplateId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunsets(organizationId, runsetTemplateId));
    }
  }, [dispatch, organizationId, runsetTemplateId, shouldInvoke]);

  return {
    isLoading,
    data: {
      runsets,
      runsCount,
      totalCost,
      lastRunsetCost
    }
  };
};

const useGetOne = (runsetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { apiData } = useApiData(GET_ML_RUNSET);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSET, { organizationId, runsetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunset(organizationId, runsetId));
    }
  }, [dispatch, organizationId, runsetId, shouldInvoke]);

  return { isLoading, runset: apiData };
};

const useCreate = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_ML_RUNSET);

  const onCreate = (runsetTemplateId, params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlRunset(organizationId, runsetTemplateId, params)).then(() => {
          if (!isError(CREATE_ML_RUNSET, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useGetRuns = (runsetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { runs = [] }
  } = useApiData(GET_ML_RUNSETS_RUNS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSETS_RUNS, { organizationId, runsetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunsetsRuns(organizationId, runsetId));
    }
  }, [dispatch, organizationId, runsetId, shouldInvoke]);

  return {
    isLoading,
    runs
  };
};

const useGetRunners = (runsetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { runners: executors = [] }
  } = useApiData(GET_ML_RUNSET_EXECUTORS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_RUNSET_EXECUTORS, { organizationId, runsetId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlRunsetExecutors(organizationId, runsetId));
    }
  }, [dispatch, organizationId, runsetId, shouldInvoke]);

  return { isLoading, executors };
};

const useStopRunset = (runsetId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(STOP_ML_RUNSET);

  const onStop = () =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(stopMlRunset(organizationId, runsetId)).then(() => {
          if (!isError(STOP_ML_RUNSET, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onStop, isLoading };
};

function MlRunsetsService() {
  return { useGetAll, useGetOne, useCreate, useGetRuns, useGetRunners, useStopRunset };
}

export default MlRunsetsService;
