import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getMlExecutors, getMlExecutorsBreakdown } from "api";
import { GET_ML_EXECUTORS, GET_ML_EXECUTORS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGet = ({ applicationIds, runIds } = {}) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { executors = [] }
  } = useApiData(GET_ML_EXECUTORS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_EXECUTORS, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getMlExecutors(organizationId, {
          applicationIds,
          runIds
        })
      );
    }
  }, [shouldInvoke, dispatch, organizationId, applicationIds, runIds]);

  return { isLoading, executors };
};

const useGetBreakdown = (params) => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { breakdown = {} }
  } = useApiData(GET_ML_EXECUTORS_BREAKDOWN);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_EXECUTORS_BREAKDOWN, { organizationId, ...params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlExecutorsBreakdown(organizationId, params));
    }
  }, [shouldInvoke, dispatch, organizationId, params]);

  return { isLoading, breakdown };
};

function MlExecutorsService() {
  return { useGet, useGetBreakdown };
}

export default MlExecutorsService;
