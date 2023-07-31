import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import { useFetchAndDownload } from "./useFetchAndDownload";

export const useDownloadCleanupScript = ({ type }) => {
  const { isFileDownloading: isDownloadingCleanupScript, fetchAndDownload: fetchAndDownloadCleanupScripts } =
    useFetchAndDownload();

  return {
    download: (cloudAccount) => {
      fetchAndDownloadCleanupScripts({
        url: `${getApiUrl(RESTAPI)}/cloud_accounts/${cloudAccount}/cleanup_${type}.sh`
      });
    },
    isLoading: isDownloadingCleanupScript
  };
};
