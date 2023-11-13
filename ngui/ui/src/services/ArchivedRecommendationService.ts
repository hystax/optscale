import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getArchivedOptimizationsCount, getArchivedOptimizationsBreakdown } from "api";
import { GET_ARCHIVED_OPTIMIZATIONS_COUNT, GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN } from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const useGetArchivedOptimizationsCount = (params) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_ARCHIVED_OPTIMIZATIONS_COUNT, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ARCHIVED_OPTIMIZATIONS_COUNT, { organizationId, ...params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getArchivedOptimizationsCount(organizationId, params));
    }
  }, [shouldInvoke, dispatch, organizationId, params]);

  return { isLoading, data };
};

const useGetArchivedOptimizationsBreakdown = (params) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN, {});

  const { isLoading, shouldInvoke } = useApiState(GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN, { organizationId, ...params });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getArchivedOptimizationsBreakdown(organizationId, params));
    }
  }, [shouldInvoke, dispatch, organizationId, params]);

  return {
    isLoading,
    data
  };
};

function ArchivedRecommendationService() {
  return {
    useGetArchivedOptimizationsCount,
    useGetArchivedOptimizationsBreakdown
  };
}

export default ArchivedRecommendationService;
