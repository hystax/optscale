import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getArchivedOptimizationsCount, getArchivedOptimizationsBreakdown, RESTAPI } from "api";
import { GET_ARCHIVED_OPTIMIZATIONS_COUNT, GET_ARCHIVED_OPTIMIZATIONS_BREAKDOWN } from "api/restapi/actionTypes";
import { getApiUrl } from "api/utils";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";
import { formatUTC } from "utils/datetime";
import { formQueryString } from "utils/network";

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

const useDownloadArchivedOptimizations = () => {
  const { isFileDownloading: isLoading, fetchAndDownload } = useFetchAndDownload();
  const { organizationId } = useOrganizationInfo();

  const onDownload = (params: { startDate: number; endDate: number }) =>
    fetchAndDownload({
      url: `${getApiUrl(RESTAPI)}/organizations/${organizationId}/archived_recommendations_details?${formQueryString({
        start_date: params.startDate,
        end_date: params.endDate
      })}`,
      fallbackFilename: `recommendations_archive_${formatUTC(params.startDate)}__${formatUTC(params.endDate)}.${DOWNLOAD_FILE_FORMATS.JSON}`
    });

  return { isLoading, onDownload };
};

function ArchivedRecommendationService() {
  return {
    useGetArchivedOptimizationsCount,
    useGetArchivedOptimizationsBreakdown,
    useDownloadArchivedOptimizations
  };
}

export default ArchivedRecommendationService;
