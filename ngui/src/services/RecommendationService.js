import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getArchivedOptimizationsCount, getArchivedOptimizationsBreakdown, getOptimizations } from "api";
import {
  GET_ARCHIVED_OPTIMIZATIONS_COUNT,
  GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN,
  GET_OPTIMIZATIONS
} from "api/restapi/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

export const useGetRelevantOptimizations = () => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { apiData: data } = useApiData(GET_OPTIMIZATIONS, {});

  const { isLoading, shouldInvoke } = useApiState(GET_OPTIMIZATIONS, { organizationId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getOptimizations(organizationId));
    }
  }, [shouldInvoke, dispatch, organizationId]);

  return { isLoading, data };
};

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

function RecommendationService() {
  return {
    useGetRelevantOptimizations,
    useGetArchivedOptimizationsCount,
    useGetArchivedOptimizationsBreakdown
  };
}

export default RecommendationService;
