import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import KeyValueLabel from "components/KeyValueLabel";
import useStyles from "./InfoArea.styles";

const DisplayedLabel = ({ tableContext, rowsCount, totalNumber, dataTestIds }) => {
  const getDisplayedValue = () => {
    if (tableContext.getPageCount() <= 1) {
      return rowsCount;
    }

    const { pageIndex, pageSize } = tableContext.getState().pagination;

    const from = pageIndex * pageSize + 1;

    const currentPageLastRowIndex = (pageIndex + 1) * pageSize;
    const to = Math.min(currentPageLastRowIndex, totalNumber);

    return <FormattedMessage id="fromTo" values={{ from, to }} />;
  };

  return (
    <KeyValueLabel
      value={getDisplayedValue()}
      messageId="displayed"
      variant="caption"
      dataTestIds={{
        typography: dataTestIds.displayed,
        key: dataTestIds.displayedKey,
        value: dataTestIds.displayedValue
      }}
    />
  );
};

const InfoArea = ({
  showCounters,
  hideTotal,
  hideDisplayed,
  totalNumber = 0,
  rowsCount = 0,
  selectedRowsCount = 0,
  dataTestIds = {},
  showAllLink,
  tableContext
}) => {
  const { classes } = useStyles();
  const { showAll: showAllDataTestId = null } = dataTestIds;

  const hasSomethingToShow = showCounters || !!showAllLink;

  return (
    hasSomethingToShow && (
      <Box className={classes.infoWrapper}>
        {showCounters && (
          <>
            {hideTotal ? null : (
              <KeyValueLabel
                value={totalNumber}
                messageId="total"
                variant="caption"
                dataTestIds={{ typography: dataTestIds.total, key: dataTestIds.totalKey, value: dataTestIds.totalValue }}
              />
            )}
            {hideDisplayed ? null : (
              <DisplayedLabel
                tableContext={tableContext}
                rowsCount={rowsCount}
                totalNumber={totalNumber}
                dataTestIds={dataTestIds}
              />
            )}
            {selectedRowsCount !== 0 && (
              <KeyValueLabel
                value={selectedRowsCount}
                messageId="selected"
                variant="caption"
                dataTestIds={{
                  typography: dataTestIds.selected,
                  key: dataTestIds.selectedKey,
                  value: dataTestIds.selectedValue
                }}
              />
            )}
          </>
        )}
        {!!showAllLink && (
          <Link variant="caption" data-test-id={showAllDataTestId} to={showAllLink} component={RouterLink}>
            <FormattedMessage id="showAll" />
          </Link>
        )}
      </Box>
    )
  );
};

export default InfoArea;
