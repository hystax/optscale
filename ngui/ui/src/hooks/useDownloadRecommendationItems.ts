import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import { formQueryString } from "utils/network";
import { useFetchAndDownload } from "./useFetchAndDownload";
import { useOrganizationInfo } from "./useOrganizationInfo";

export const useDownloadRecommendationItems = ({ limit, type, status, dataSourceIds = [] }) => {
  const { isFileDownloading: isLoading, fetchAndDownload: fetchAndDownloadRecommendation } = useFetchAndDownload();

  const { organizationId } = useOrganizationInfo();

  return {
    download: (format) => {
      const apiPath = `${getApiUrl(RESTAPI)}/organizations/${organizationId}/optimization_data`;
      const queryParameters = formQueryString({
        type,
        status,
        format,
        limit,
        cloud_account_id: dataSourceIds
      });

      const url = `${apiPath}?${queryParameters}`;

      fetchAndDownloadRecommendation({
        url,
        fallbackFilename: `${type}.${format}`
      });
    },
    isLoading
  };
};
