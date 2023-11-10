import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { REST_API_URL } from "api";
import ButtonLoader from "components/ButtonLoader";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";
import { formQueryString } from "utils/network";

const DownloadObjectsListContainer = ({ fromBucketName, toBucketName, checkId }) => {
  const { isDemo } = useOrganizationInfo();

  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  const downloadObjectsList = () => {
    const url = `${REST_API_URL}/geminis/${checkId}/data?${formQueryString({
      bucket: [fromBucketName, toBucketName]
    })}`;

    fetchAndDownload({
      url,
      fallbackFilename: `objects_list.${DOWNLOAD_FILE_FORMATS.XLSX}`
    });
  };

  return (
    <ButtonLoader
      sx={{ whiteSpace: "nowrap" }}
      messageId="downloadObjectsList"
      startIcon={<CloudDownloadOutlinedIcon />}
      onClick={() => downloadObjectsList()}
      color="primary"
      variant="contained"
      isLoading={isFileDownloading}
      disabled={isDemo}
      tooltip={{ show: isDemo, messageId: "notAvailableInLiveDemo" }}
    />
  );
};

export default DownloadObjectsListContainer;
