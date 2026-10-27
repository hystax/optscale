import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import MenuItem from "@mui/material/MenuItem";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import Popover from "components/Popover";
import { useDownloadPoolExpensesReport } from "hooks/useDownloadPoolExpensesReport";
import { DOWNLOAD_FILE_FORMATS } from "utils/constants";

const PoolExpensesReportDownload = ({ startDateTimestamp, endDateTimestamp }) => {
  const { isLoading, download } = useDownloadPoolExpensesReport({
    startDate: startDateTimestamp,
    endDate: endDateTimestamp,
  });

  const onMenuItemClick = (format, onClose) => {
    download(format);
    onClose();
  };

  return (
    <Box display="inline-block">
      <Popover
        renderMenu={({ closeHandler }) => (
          <List>
            <MenuItem
              onClick={() => onMenuItemClick(DOWNLOAD_FILE_FORMATS.CSV, closeHandler)}
              data-test-id="download_pool_expenses_report_csv"
            >
              <FormattedMessage id="csvFile" />
            </MenuItem>
            <MenuItem
              onClick={() => onMenuItemClick(DOWNLOAD_FILE_FORMATS.XLSX, closeHandler)}
              data-test-id="download_pool_expenses_report_xlsx"
            >
              <FormattedMessage id="xlsxFile" />
            </MenuItem>
          </List>
        )}
        label={({ isOpen }) => (
          <ButtonLoader
            dataTestId="btn_download_pool_expenses_report"
            messageId="downloadReport"
            variant="text"
            startIcon={<CloudDownloadOutlinedIcon />}
            isLoading={isLoading}
            endIcon={isOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
          />
        )}
      />
    </Box>
  );
};

export default PoolExpensesReportDownload;
