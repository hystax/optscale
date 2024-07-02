import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import useStyles from "./InfoArea.styles";

const DisplayedLabel = ({ rowsCount, totalNumber, pagination, dataTestIds }) => {
  const getDisplayedValue = () => {
    const { pageCount, pageIndex, pageSize } = pagination;

    if (pageCount <= 1 || pageIndex + 1 > pageCount) {
      return rowsCount;
    }

    const from = pageIndex * pageSize + 1;

    const currentPageLastRowIndex = (pageIndex + 1) * pageSize;
    const to = Math.min(currentPageLastRowIndex, totalNumber);

    return <FormattedMessage id="fromTo" values={{ from, to }} />;
  };

  return (
    <KeyValueLabel
      value={getDisplayedValue()}
      keyMessageId="displayed"
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
  pagination
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
                keyMessageId="total"
                variant="caption"
                dataTestIds={{ typography: dataTestIds.total, key: dataTestIds.totalKey, value: dataTestIds.totalValue }}
              />
            )}
            {hideDisplayed ? null : (
              <DisplayedLabel
                rowsCount={rowsCount}
                totalNumber={totalNumber}
                dataTestIds={dataTestIds}
                pagination={pagination}
              />
            )}
            {selectedRowsCount !== 0 && (
              <KeyValueLabel
                value={selectedRowsCount}
                keyMessageId="selected"
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
