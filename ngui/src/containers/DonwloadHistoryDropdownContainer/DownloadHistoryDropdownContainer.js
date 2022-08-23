import React from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import Dropdown from "components/Dropdown";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";

const DownloadHistoryDropdownContainer = ({ environmentId }) => {
  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();

  const downloadPropsHistory = (format) => {
    fetchAndDownload({
      url: `${getApiUrl(RESTAPI)}/cloud_resources/${environmentId}/env_properties_history?format=${format}`,
      fallbackFilename: `${environmentId}.${format}`
    });
  };

  return (
    <Box display="inline-block" ml={1}>
      <Dropdown
        dataTestId={"download-history-dropdown"}
        popupId="downloadHistory"
        icon={<CloudDownloadOutlinedIcon fontSize="small" />}
        messageId="downloadHistory"
        items={[
          {
            key: "xlsx",
            messageId: "xlsxFile",
            dataTestId: "download-history-xlsx",
            action: () => downloadPropsHistory(DOWNLOAD_FILE_FORMATS.XLSX)
          },
          {
            key: "json",
            messageId: "jsonFile",
            dataTestId: "download-history-json",
            action: () => downloadPropsHistory(DOWNLOAD_FILE_FORMATS.JSON)
          }
        ]}
        trigger="button"
        isLoading={isFileDownloading}
      />
    </Box>
  );
};

DownloadHistoryDropdownContainer.propTypes = {
  environmentId: PropTypes.string.isRequired
};

export default DownloadHistoryDropdownContainer;
