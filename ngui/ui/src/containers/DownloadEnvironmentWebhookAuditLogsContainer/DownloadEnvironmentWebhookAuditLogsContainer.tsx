import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { FormattedMessage } from "react-intl";
import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import IconButton from "components/IconButton";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";

const DownloadEnvironmentWebhookAuditLogsContainer = ({ webhookId }) => {
  const { isDemo } = useOrganizationInfo();

  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  const download = (format) => {
    fetchAndDownload({
      url: `${getApiUrl(RESTAPI)}/webhooks/${webhookId}/logs?format=${format}`,
      fallbackFilename: `${webhookId}.${format}`
    });
  };

  return (
    <IconButton
      icon={<CloudDownloadOutlinedIcon />}
      onClick={() => download(DOWNLOAD_FILE_FORMATS.XLSX)}
      disabled={isDemo}
      tooltip={{
        show: true,
        value: <FormattedMessage id={isDemo ? "notAvailableInLiveDemo" : "downloadAuditLogs"} />
      }}
      isLoading={isFileDownloading}
    />
  );
};

export default DownloadEnvironmentWebhookAuditLogsContainer;
