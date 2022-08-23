import React from "react";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import SearchInput from "components/SearchInput";
import ColumnsSelector, { ColumnsSelectorProps, ColumnsSelectorTestIdsProp } from "./ColumnsSelector";
import InfoArea, { InfoAreaProps, InfoAreaTestIdsProp } from "./InfoArea";
import useStyles from "./styles/TableActions.styles";

const TableActions = ({
  actionBar = {},
  selectedRowsCount = 0,
  setSearchInputValue,
  searchInputValue = "",
  counters,
  columnsSelectorProps,
  dataTestIds = {},
  showAllLink
}) => {
  const { classes } = useStyles();

  const {
    infoArea: infoAreaTestIds = {},
    columnsSelector: columnsSelectorTestIds = {},
    showAll: showAllDataTestId = null
  } = dataTestIds;
  const { show: showActionBar = false, definition: actionBarDefinition } = actionBar;

  if (showActionBar) {
    // TODO: separate ActionBar https://datatrendstech.atlassian.net/browse/OS-3554
    // making ActionBar data structure ({items:...}), also adding disabled prop to items
    actionBarDefinition.items = actionBarDefinition.items.map((item) => ({
      disabled: item.enableIfSelectedRows && selectedRowsCount === 0,
      ...item
    }));
  }

  const showSearch = typeof setSearchInputValue === "function";
  const { showCounters } = counters;
  const showColumnsSelector = !!columnsSelectorProps.columnsSelectorUID;
  const gotSomethingToDisplay = showActionBar || showSearch || showCounters || showColumnsSelector || !!showAllLink;

  return (
    gotSomethingToDisplay && (
      <Box className={classes.wrapper}>
        {showCounters || !!showAllLink ? (
          <Box className={classes.infoWrapper}>
            {showCounters && <InfoArea selectedRowsCount={selectedRowsCount} {...counters} dataTestIds={infoAreaTestIds} />}
            {!!showAllLink && (
              <Link data-test-id={showAllDataTestId} to={showAllLink} component={RouterLink}>
                <FormattedMessage id="showAll" />
              </Link>
            )}
          </Box>
        ) : null}
        {showSearch || showActionBar || showColumnsSelector ? (
          <Box className={classes.actionsWrapper}>
            {showSearch && (
              <SearchInput onSearch={setSearchInputValue} initialSearchText={searchInputValue} dataTestIds={dataTestIds} />
            )}
            {showActionBar && (
              <Box>
                <ActionBar isPage={false} data={actionBarDefinition} />
              </Box>
            )}
            {showColumnsSelector && <ColumnsSelector {...columnsSelectorProps} dataTestIds={columnsSelectorTestIds} />}
          </Box>
        ) : null}
      </Box>
    )
  );
};

export const TableActionTestIdsProp = PropTypes.shape({
  infoArea: InfoAreaTestIdsProp,
  searchInput: PropTypes.string,
  columnsSelector: ColumnsSelectorTestIdsProp,
  showAll: PropTypes.string
});

TableActions.propTypes = {
  actionBar: PropTypes.shape({
    show: PropTypes.bool,
    definition: PropTypes.object
  }),
  selectedRowsCount: PropTypes.number,
  setSearchInputValue: PropTypes.func,
  searchInputValue: PropTypes.string,
  counters: PropTypes.shape(InfoAreaProps),
  columnsSelectorProps: PropTypes.shape(ColumnsSelectorProps),
  dataTestIds: TableActionTestIdsProp,
  showAllLink: PropTypes.string
};

export default TableActions;
