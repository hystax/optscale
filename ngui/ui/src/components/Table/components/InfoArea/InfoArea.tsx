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
  rowsCount = 0,
  selectedRowsCount = 0,
  dataTestIds = {},
  showAllLink,
  pagination,
  counters,
  withSearch,
  withSelection,
  withPagination
}) => {
  const { show: showCounters = true, hideTotal = false, hideDisplayed = false, hideSelected = false } = counters;

  const { classes } = useStyles();
  const { showAll: showAllDataTestId = null } = dataTestIds;

  const hasSomethingToShow = showCounters || !!showAllLink;

  const totalNumber = counters.total || pagination.totalRows;

  const showTotal = !hideTotal;
  const showDisplayed = !hideDisplayed && (withSearch || withPagination);
  const showSelected = !hideSelected && withSelection && selectedRowsCount !== 0;

  return (
    hasSomethingToShow && (
      <Box className={classes.infoWrapper}>
        {showCounters && (
          <>
            {showTotal ? (
              <KeyValueLabel
                value={totalNumber}
                keyMessageId="total"
                variant="caption"
                dataTestIds={{ typography: dataTestIds.total, key: dataTestIds.totalKey, value: dataTestIds.totalValue }}
              />
            ) : null}
            {showDisplayed ? (
              <DisplayedLabel
                rowsCount={rowsCount}
                totalNumber={totalNumber}
                dataTestIds={dataTestIds}
                pagination={pagination}
              />
            ) : null}
            {showSelected ? (
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
            ) : null}
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
