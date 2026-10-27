import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getMlExecutors, getMlExecutorsBreakdown } from "api";
import { GET_ML_EXECUTORS, GET_ML_EXECUTORS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGet = ({
  taskIds,
  runIds,
  organizationId,
  arceeToken,
}: {
  taskIds?: string[];
  runIds?: string[];
  organizationId?: string;
  arceeToken?: string;
} = {}) => {
  const dispatch = useDispatch();

  const {
    apiData: { executors = [] },
  } = useApiData(GET_ML_EXECUTORS);

  const { isLoading, shouldInvoke } = useApiState(GET_ML_EXECUTORS, {
    organizationId,
    taskIds,
    runIds,
    arceeToken,
  });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(
        getMlExecutors(organizationId, {
          taskIds,
          runIds,
          arceeToken,
        })
      );
    }
  }, [taskIds, dispatch, organizationId, runIds, arceeToken, shouldInvoke]);

  return { isLoading, executors };
};

const useGetBreakdown = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { breakdown = {} },
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
