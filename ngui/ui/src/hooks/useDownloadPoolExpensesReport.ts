import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { stringifySearchParams } from "utils/network";

export const useDownloadPoolExpensesReport = ({ startDate, endDate }) => {
  const { isFileDownloading: isLoading, fetchAndDownload } = useFetchAndDownload();
  const { organizationId } = useOrganizationInfo();

  return {
    download: (format) => {
      const apiPath = `${getApiUrl(RESTAPI)}/organizations/${organizationId}/pool_expenses_report`;
      const queryParameters = stringifySearchParams({
        start_date: startDate,
        end_date: endDate,
        format,
      });

      fetchAndDownload({
        url: `${apiPath}?${queryParameters}`,
        fallbackFilename: `pool_expenses_report_${organizationId}.${format}`,
      });
    },
    isLoading,
  };
};
