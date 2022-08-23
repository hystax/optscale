import React, { useRef, useMemo, useState, useEffect, useCallback } from "react";
import Box from "@mui/material/Box";
import MaUTable from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useTable, usePagination, useSortBy, useExpanded, useRowSelect, useGlobalFilter, useColumnOrder } from "react-table";
import Pagination from "components/Table/Pagination";
import { useRootData } from "hooks/useRootData";
import { COLUMNS } from "reducers/columns";
import { isEmpty } from "utils/arrays";
import { getQueryParams, updateQueryParams } from "utils/network";
import { CELL_EMPTY_VALUE, getPaginationQueryKey, getSearchQueryKey } from "utils/tables";
import { InfoAreaProps } from "./InfoArea";
import useStyles from "./styles/Table.styles";
import TableActions from "./TableActions";
import { useCheckboxesColumn } from "./useCheckboxesColumn";

const getI18n = (messageId, values) => (
  <Typography>
    <FormattedMessage id={messageId} values={values} />
  </Typography>
);

// gets ?page= by def, or ?<label>Page= if label is passed
const getInitialPage = (key) => {
  const { [key]: page = 1 } = getQueryParams();
  return page;
};

const getInitialSearchQuery = (key) => {
  const { [key]: search = "" } = getQueryParams();
  return search;
};

const DEFAULT_EMPTY_MESSAGE_ID = "noRecordsToDisplay";

const Table = ({
  columns,
  data,
  getConditionalRowStyle,
  totalNumberOverride = 0,
  actionBar,
  showAllLink,
  withSearch = false,
  withHeader = true,
  order = [],
  columnsSelectorUID,
  counters = { showCounters: false },
  pageSize = 0,
  setSelectedRows,
  onSelectionChange,
  addSelectionColumn = false,
  withSubRows = false,
  getSubRows = undefined,
  expandedByDefault,
  localization = {},
  dataTestIds = {},
  initialSelectedRows,
  getRowId,
  queryParamPrefix,
  autoResetSortBy = true
}) => {
  const { classes } = useStyles();

  const INITIAL_SELECTED_ROWS = useMemo(() => ({}), []);

  const queryKeyForPage = getPaginationQueryKey(queryParamPrefix);
  const searchQueryKey = getSearchQueryKey(queryParamPrefix);
  const rawPageQuery = getInitialPage(queryKeyForPage);
  const [currentPage, setCurrentPage] = useState(parseInt(rawPageQuery, 10) || 0); // parsing query to integer
  const [searchInputValue, setSearchInputValue] = useState(getInitialSearchQuery(searchQueryKey));

  // must be memoized https://react-table.tanstack.com/docs/api/useSortBy#table-options
  const defSortColumn = columns.find((c) => c.defaultSort);
  const defSortBy = useMemo(
    () => (defSortColumn ? [{ id: defSortColumn.accessor, desc: defSortColumn.defaultSort === "desc" }] : []),
    [defSortColumn]
  );

  const { rootData: savedHiddenColumns = [] } = useRootData(COLUMNS, (result) => result?.[columnsSelectorUID]);
  // removing static columns from already hidden by user
  const hiddenColumns = savedHiddenColumns.filter(
    (hiddenColumnId) => !columns.find(({ accessor }) => accessor === hiddenColumnId)?.isStatic
  );
  // generating available for hiding columns
  const hideableColumns = columns
    .filter(({ isStatic }) => !isStatic)
    .map(({ accessor, columnsSelector = {} }) => ({
      accessor,
      title: columnsSelector.messageId ? <FormattedMessage id={columnsSelector.messageId} /> : columnsSelector.title,
      dataTestId: columnsSelector.dataTestId
    }));

  // Must be memoized (according to the examples from the react-table)
  const defaultColumn = useMemo(
    () => ({
      sortType: "basic"
    }),
    []
  );

  const {
    getTableProps,
    headerGroups,
    rows, // filtered rows
    prepareRow,
    page, // only current page filtered rows, use preFilteredRows if needed
    pageCount, // how much pages there are
    gotoPage,
    selectedFlatRows,
    setGlobalFilter,
    setHiddenColumns,
    state: { pageIndex },
    allColumns
  } = useTable(
    {
      columns,
      data,
      getSubRows,
      disableSortRemove: true,
      initialState: {
        sortBy: defSortBy,
        pageIndex: currentPage - 1,
        pageSize,
        globalFilter: searchInputValue,
        hiddenColumns,
        columnOrder: order,
        selectedRowIds: initialSelectedRows || INITIAL_SELECTED_ROWS
      },
      defaultColumn,
      getRowId,
      autoResetSortBy
    },
    withSearch && useGlobalFilter,
    useSortBy,
    withSubRows && useExpanded,
    pageSize && usePagination,
    ...(addSelectionColumn
      ? [
          useRowSelect,
          (hooks) => {
            // eslint-disable-next-line no-param-reassign
            hooks.useCheckboxesColumnsOnSelectionChange = () =>
              typeof onSelectionChange === "function" ? onSelectionChange : () => {};
          },
          useCheckboxesColumn
        ]
      : []),
    !isEmpty(order) && useColumnOrder
  );

  const addSearchToQueryParams = (searchKey, searchText) => {
    updateQueryParams({ [searchKey]: searchText });
  };

  // passing original selected rows twimc
  useEffect(() => {
    if (typeof setSelectedRows === "function") {
      setSelectedRows(selectedFlatRows.map((d) => d.original));
    }
  }, [selectedFlatRows, setSelectedRows]);

  const paginationHandler = useCallback(
    (newPage) => {
      if (!pageSize) return;
      updateQueryParams({ [queryKeyForPage]: newPage !== 1 ? newPage : undefined });
      setCurrentPage(newPage);
      gotoPage(newPage - 1);
    },
    [setCurrentPage, gotoPage, queryKeyForPage, pageSize]
  );

  const currentRows = pageSize ? page : rows;

  // automatically switching back to the closest non-empty page if there are no rows left on the current page
  useEffect(() => {
    if (currentPage > 1 && +rawPageQuery > pageCount && currentRows.length === 0) {
      paginationHandler(pageCount);
    }
  }, [currentPage, currentRows, pageCount, paginationHandler, rawPageQuery]);

  // expanding rows by some condition
  useEffect(() => {
    if (withSubRows) {
      currentRows?.forEach((row) => {
        if (typeof expandedByDefault === "function" && expandedByDefault(row.original) && !row.isExpanded) {
          row.toggleRowExpanded(true);
        }
      });
    }
  }, [currentRows, expandedByDefault, withSubRows]);

  // filter set logic — dropping pagination each time to 1 page, setting search query
  const searchInited = useRef(false);
  useEffect(() => {
    if (!withSearch) return;
    // prevent dropping page query on initialization
    if (searchInited.current) {
      paginationHandler(1);

      // also query parameter is set into initial state of react table, no need to set global filter on mount
      addSearchToQueryParams(searchQueryKey, searchInputValue);
      setGlobalFilter(searchInputValue);
    }
    searchInited.current = true;
  }, [searchInputValue, searchQueryKey, setGlobalFilter, paginationHandler, withSearch]);

  const rowsRenderer = (anyRows) =>
    anyRows.map((row) => {
      prepareRow(row);
      const { key: rowKey, ...restRowProps } = row.getRowProps();
      const conditionalRowStyle = typeof getConditionalRowStyle === "function" ? getConditionalRowStyle(row.original) : null;

      return (
        <TableRow key={rowKey} style={conditionalRowStyle} {...restRowProps}>
          {row.cells.map((cell) => {
            const { key: cellKey, ...restCellProps } = cell.getCellProps([{ style: cell.column.style }]);
            return (
              <TableCell data-product-tour-id={cell.column.dataProductTourId} key={cellKey} {...restCellProps}>
                {cell.value === undefined && cell.column.accessor !== undefined
                  ? cell.column.emptyValue || CELL_EMPTY_VALUE
                  : cell.render("Cell")}
              </TableCell>
            );
          })}
        </TableRow>
      );
    });

  const checkPagination = ({ isPaginationEnabled, parsedPage, pageQuery, pagesTotal, noRowsToDisplay, hasData }) => {
    // no pagination enabled — hide ui and do not check query
    if (!isPaginationEnabled) {
      return { showPagination: false, isPageNumberInvalid: false };
    }

    // "Invalid" means "not (integer & >0)"
    const isPageQueryInvalid = parsedPage.toString() !== pageQuery.toString() || parsedPage <= 0; // pageQuery is string, parsedPage — number

    // parsed page number is invalid if it exeeds total pages num or not equal to page query string, and there are some pages at all
    const isPageNumberInvalid = pagesTotal > 0 && (parsedPage > pagesTotal || isPageQueryInvalid);

    // Show pagination logic:
    // 1. standard case scenario (there are rows and more than 2 pages)
    const regularShowPaginationCase = pagesTotal > 1 && !noRowsToDisplay;
    // 2. invalid page query but data available (ability for user to return to normal page via UI)
    const invalidPageQueryCase = isPageNumberInvalid && hasData;
    // 3.
    const showPagination = regularShowPaginationCase || invalidPageQueryCase;

    return { showPagination, isPageNumberInvalid };
  };

  const noRowsToDisplay = currentRows.length === 0;
  const hasData = isEmpty(data.length);
  const { showPagination, isPageNumberInvalid } = checkPagination({
    isPaginationEnabled: pageSize !== 0,
    parsedPage: currentPage,
    pageQuery: rawPageQuery,
    pagesTotal: pageCount,
    noRowsToDisplay,
    hasData
  });

  const renderMessageInsteadCells = noRowsToDisplay || isPageNumberInvalid;

  const noRowsRenderer = () => (
    <TableRow>
      <TableCell align="center" colSpan={allColumns.length}>
        {isPageNumberInvalid && hasData ? (
          <FormattedMessage id="pageIsUnavailable" values={{ value: rawPageQuery }} />
        ) : (
          getI18n(localization.emptyMessageId || DEFAULT_EMPTY_MESSAGE_ID)
        )}
      </TableCell>
    </TableRow>
  );

  return (
    <div data-test-id={dataTestIds.container}>
      <TableActions
        actionBar={actionBar}
        showAllLink={showAllLink}
        selectedRowsCount={selectedFlatRows?.length}
        setSearchInputValue={withSearch ? setSearchInputValue : null}
        searchInputValue={withSearch ? searchInputValue : null}
        counters={{
          invalidPageQuery: isPageNumberInvalid,
          // displayed without pagination filtered rows (for Displayed counter)
          rowsLength: rows.length,
          pagesNum: pageCount,
          pageSize,
          currentPage: pageIndex,
          // total rows number — overridden (if more than 5000) or just data.length (for Total counter)
          totalNumber: totalNumberOverride || data.length,
          ...counters
        }}
        columnsSelectorProps={{
          columnsSelectorUID,
          hideableColumns,
          setHiddenColumns
        }}
        dataTestIds={dataTestIds}
      />
      {/* need that box wrap to make table fit 100% width with small amount of columns */}
      <Box className={classes.horizontalScroll}>
        <MaUTable {...getTableProps()}>
          {withHeader && (
            <TableHead>
              {headerGroups.map((headerGroup) => {
                const { key: headerGroupKey, ...restHeaderGroupProps } = headerGroup.getHeaderGroupProps();
                return (
                  <TableRow key={headerGroupKey} {...restHeaderGroupProps}>
                    {headerGroup.headers.map((column) => {
                      const { key: headerKey, ...restHeaderProps } = column.getHeaderProps([
                        column.getSortByToggleProps(),
                        { style: column.style }
                      ]);
                      return (
                        <TableCell key={headerKey} {...restHeaderProps}>
                          <strong>
                            {column.canSort ? (
                              <TableSortLabel active={column.isSorted} direction={column.isSortedDesc ? "desc" : "asc"}>
                                {column.render("Header")}
                              </TableSortLabel>
                            ) : (
                              column.render("Header")
                            )}
                          </strong>
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableHead>
          )}
          <TableBody>{renderMessageInsteadCells ? noRowsRenderer() : rowsRenderer(currentRows)}</TableBody>
        </MaUTable>
      </Box>
      {showPagination && (
        <Pagination count={pageCount} page={isPageNumberInvalid ? 0 : currentPage} paginationHandler={paginationHandler} />
      )}
    </div>
  );
};

Table.propTypes = {
  data: PropTypes.array.isRequired,
  totalNumberOverride: PropTypes.number,
  columns: PropTypes.array.isRequired,
  getConditionalRowStyle: PropTypes.func,
  localization: PropTypes.shape({
    emptyMessageId: PropTypes.string
  }),
  actionBar: PropTypes.object,
  showAllLink: PropTypes.string,
  dataTestIds: PropTypes.object,
  withSearch: PropTypes.bool,
  withHeader: PropTypes.bool,
  withSubRows: PropTypes.bool,
  getSubRows: PropTypes.func, // optional, defaults to (row) => row.subRows || []
  expandedByDefault: PropTypes.func,
  columnsSelectorUID: PropTypes.string,
  pageSize: PropTypes.number,
  counters: PropTypes.shape(InfoAreaProps),
  setSelectedRows: PropTypes.func,
  onSelectionChange: PropTypes.func,
  addSelectionColumn: PropTypes.bool,
  autoResetSortBy: PropTypes.bool,
  order: PropTypes.array,
  initialSelectedRows: PropTypes.object,
  getRowId: PropTypes.func,
  queryParamPrefix: PropTypes.string
};

export default Table;
