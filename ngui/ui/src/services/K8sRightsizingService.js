import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getK8sRightsizing } from "api/restapi/actionCreators";
import { GET_K8S_RIGHTSIZING } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGet = (params = {}) => {
  const dispatch = useDispatch();

  const { startDate, endDate } = params;

  const { organizationId } = useOrganizationInfo();

  const { isDataReady, shouldInvoke } = useApiState(GET_K8S_RIGHTSIZING, {
    organizationId,
    startDate,
    endDate
  });

  const {
    apiData: { k8sRightsizing = {} }
  } = useApiData(GET_K8S_RIGHTSIZING);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getK8sRightsizing(organizationId, { startDate, endDate }));
    }
  }, [shouldInvoke, dispatch, organizationId, startDate, endDate]);

  return { isLoading: !isDataReady, k8sRightsizing };
};

function K8sRightsizingService() {
  return { useGet };
}

export default K8sRightsizingService;
