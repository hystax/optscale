import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import IconButton from "components/IconButton";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";

const DownloadEnvironmentWebhookAuditLogsContainer = ({ webhookId }) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  const download = (format) => {
    fetchAndDownload({
      url: `${getApiUrl(RESTAPI)}/webhooks/${webhookId}/logs?format=${format}`,
      fallbackFilename: `${webhookId}.${format}`,
    });
  };

  return (
    <IconButton
      icon={<CloudDownloadOutlinedIcon />}
      onClick={() => download(DOWNLOAD_FILE_FORMATS.XLSX)}
      disabled={isRestricted}
      tooltip={{
        show: true,
        value: isRestricted ? restrictionReasonMessage : "downloadAuditLogs",
      }}
      isLoading={isFileDownloading}
    />
  );
};

export default DownloadEnvironmentWebhookAuditLogsContainer;
