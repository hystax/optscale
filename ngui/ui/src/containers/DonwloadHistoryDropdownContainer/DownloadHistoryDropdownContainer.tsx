import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import { Box } from "@mui/material";
import List from "@mui/material/List";
import MenuItem from "@mui/material/MenuItem";
import { FormattedMessage } from "react-intl";
import { RESTAPI } from "api";
import { getApiUrl } from "api/utils";
import ButtonLoader from "components/ButtonLoader";
import Popover from "components/Popover";
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

  const onMenuItemClick = (format, onClose) => {
    downloadPropsHistory(format);
    onClose();
  };

  return (
    <Box display="inline-block" ml={1}>
      <Popover
        renderMenu={({ closeHandler }) => (
          <List>
            <MenuItem
              onClick={() => onMenuItemClick(DOWNLOAD_FILE_FORMATS.XLSX, closeHandler)}
              data-test-id="download-history-xlsx"
            >
              <FormattedMessage id="xlsxFile" />
            </MenuItem>
            <MenuItem
              onClick={() => onMenuItemClick(DOWNLOAD_FILE_FORMATS.JSON, closeHandler)}
              data-test-id="download-history-json"
            >
              <FormattedMessage id="jsonFile" />
            </MenuItem>
          </List>
        )}
        label={({ isOpen }) => (
          <ButtonLoader
            dataTestId="download-history-dropdown"
            messageId="downloadHistory"
            variant="text"
            startIcon={<CloudDownloadOutlinedIcon />}
            isLoading={isFileDownloading}
            endIcon={isOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
          />
        )}
      />
    </Box>
  );
};

export default DownloadHistoryDropdownContainer;
