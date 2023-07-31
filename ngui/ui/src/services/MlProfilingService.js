import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getProfilingToken } from "api";
import { GET_PROFILING_TOKEN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetToken = () => {
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const {
    apiData: { token = "" }
  } = useApiData(GET_PROFILING_TOKEN);

  const { isLoading, shouldInvoke } = useApiState(GET_PROFILING_TOKEN, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getProfilingToken(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, token };
};

function MlProfilingService() {
  return { useGetToken };
}

export default MlProfilingService;
