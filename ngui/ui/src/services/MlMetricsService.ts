import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { createMlMetric, getMlMetric, getMlMetrics, updateMlMetric, deleteMlMetric } from "api";
import {
  CREATE_GLOBAL_METRIC,
  GET_ML_GLOBAL_METRIC,
  GET_ML_METRICS,
  UPDATE_GLOBAL_METRIC,
  DELETE_GLOBAL_METRIC
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { isError } from "utils/api";

const useGetMlMetrics = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { metrics = [] }
  } = useApiData(GET_ML_METRICS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_METRICS, {
    organizationId
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlMetrics(organizationId));
    }
  }, [dispatch, organizationId, shouldInvoke]);

  return { isLoading, metrics };
};

const useAlwaysGetMlMetric = (metricId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const [metric, setMetric] = useState({});

  const { isLoading } = useApiState(GET_ML_GLOBAL_METRIC, {
    organizationId
  });

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(getMlMetric(organizationId, metricId)).then(() => {
        const state = getState();
        if (!isError(GET_ML_GLOBAL_METRIC, getState())) {
          setMetric(state.restapi[GET_ML_GLOBAL_METRIC]);
        }
      });
    });
  }, [dispatch, organizationId, metricId]);

  return { isLoading, metric };
};

const useCreateMlMetric = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(CREATE_GLOBAL_METRIC);

  const onCreate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createMlMetric(organizationId, params)).then(() => {
          if (!isError(CREATE_GLOBAL_METRIC, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onCreate, isLoading };
};

const useUpdateMlMetric = (metricId) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(UPDATE_GLOBAL_METRIC);

  const onUpdate = (params) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(updateMlMetric(organizationId, metricId, params)).then(() => {
          if (!isError(UPDATE_GLOBAL_METRIC, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onUpdate, isLoading };
};

const useDeleteMlMetric = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();
  const { isLoading } = useApiState(DELETE_GLOBAL_METRIC);

  const onDelete = (metricId) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(deleteMlMetric(organizationId, metricId)).then(() => {
          if (!isError(DELETE_GLOBAL_METRIC, getState())) {
            return resolve();
          }
          return reject();
        });
      });
    });

  return { onDelete, isLoading };
};

function MlMetricsService() {
  return {
    useGetMlMetrics,
    useCreateMlMetric,
    useUpdateMlMetric,
    useAlwaysGetMlMetric,
    useDeleteMlMetric
  };
}

export default MlMetricsService;
