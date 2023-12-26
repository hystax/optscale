import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getMlExecutors, getMlExecutorsBreakdown } from "api";
import { GET_ML_EXECUTORS, GET_ML_EXECUTORS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGet = ({ modelIds, runIds } = {}) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const {
    apiData: { executors = [] }
  } = useApiData(GET_ML_EXECUTORS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_EXECUTORS, { organizationId, modelIds, runIds });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getMlExecutors(organizationId, {
          modelIds,
          runIds
        })
      );
    }
  }, [modelIds, dispatch, organizationId, runIds, shouldInvoke]);

  return { isLoading, executors };
};

const useGetBreakdown = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { breakdown = {} }
  } = useApiData(GET_ML_EXECUTORS_BREAKDOWN);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_EXECUTORS_BREAKDOWN, organizationId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getMlExecutorsBreakdown(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, breakdown };
};

function MlExecutorsService() {
  return { useGet, useGetBreakdown };
}

export default MlExecutorsService;
