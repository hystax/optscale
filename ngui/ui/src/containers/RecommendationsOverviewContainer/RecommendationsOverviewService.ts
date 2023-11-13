import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getOptimizationsOverview, updateOptimizations } from "api";
import { GET_OPTIMIZATIONS_OVERVIEW } from "api/restapi/actionTypes";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetOptimizationsOverview = (cloudAccountIds) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_OPTIMIZATIONS_OVERVIEW, {});

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_OPTIMIZATIONS_OVERVIEW, { organizationId, cloudAccountIds });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOptimizationsOverview(organizationId, cloudAccountIds));
    }
  }, [shouldInvoke, dispatch, organizationId, cloudAccountIds]);

  return { isLoading, isDataReady, data };
};

const useForceCheck = () => {
  const dispatch = useDispatch();
  const { apiData: optimizations } = useApiData(GET_OPTIMIZATIONS_OVERVIEW, {});
  const isManageChecklistsAllowed = useIsAllowed({
    requiredActions: ["MANAGE_CHECKLISTS"]
  });
  const { isDemo } = useOrganizationInfo();

  return {
    forceCheck: () => dispatch(updateOptimizations(optimizations.id, { nextRun: 1 })),
    isForceCheckAvailable: isManageChecklistsAllowed && !isDemo
  };
};

function RecommendationsOverviewService() {
  return {
    useGetOptimizationsOverview,
    useForceCheck
  };
}

export default RecommendationsOverviewService;
