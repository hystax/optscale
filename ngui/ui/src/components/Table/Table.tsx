import { useRef } from "react";
import { Box, TableBody, TableCell, TableFooter, TableHead, TableRow } from "@mui/material";
import MuiTable from "@mui/material/Table";
import { getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { FormattedMessage } from "react-intl";
import TableLoader from "components/TableLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import InfoArea from "./components/InfoArea";
import Pagination from "./components/Pagination";
import TableActions from "./components/TableActions";
import { MemoTableBodyCell, TableBodyCell } from "./components/TableBodyCell";
import TableFooterCell from "./components/TableFooterCell";
import TableHeaderCell from "./components/TableHeaderCell";
import {
  useColumnOrderTableSettings,
  useColumns,
  useColumnsVisibility,
  useExpandedTableSettings,
  useGlobalFilterTableSettings,
  useInitialSortingState,
  usePaginationTableSettings,
  useRowSelectionTableSettings,
  useSortingTableSettings,
  useSticky
} from "./hooks";
import useStyles from "./Table.styles";
import { getRowsCount } from "./utils";
import { SELECTION_COLUMN_ID } from "./utils/constants";

const DEFAULT_EMPTY_MESSAGE_ID = "noDataToDisplay";

const Table = ({
  data,
  columns: columnsProperty,
  /**
   * TODO: Remove isLoading from this component
   * Motivation: This component manages a local state, so if we render it when data is not fully
   * ready (isLoading = false) then we will need to update the local state that depends on a dynamic (api) data
   * when it is ready.
   * We could make **THIS** component isLoading-independent in order to initialize the state when the data is fully loaded
   * In order to do so, we could create another **Table** component and define the following logic there:
   * ```
   * const Table = ({ isLoading, ...rest }) => {
   *    if(isLoading) { return <TableLoader /> }
   *
   *    return <TableComponent {...rest}/>
   * }
   * ```
   */
  isLoading,
  getRowStyle,
  withHeader = true,
  withFooter = false,
  withSearch,
  rangeFilter,
  dataTestIds = {},
  queryParamPrefix,
  localization = {},
  pageSize,
  counters = {},
  /**
   * TODO: The name is confusing, it looks like it is a boolean, but it is a string
   * @ekirillov would suggest refactoring it to something more generic line "link" or "header link"
   */
  showAllLink,
  withSelection,
  rowSelection,
  onRowSelectionChange,
  withExpanded,
  getSubRows = (row) => row.children,
  getRowId,
  expanded,
  onExpandedChange,
  actionBar,
  columnsSelectorUID,
  columnSetsSelectorId,
  columnOrder,
  onColumnOrderChange,
  stickySettings = {},
  memoBodyCells = false,
  getRowCellClassName,
  getHeaderCellClassName,
  onRowClick,
  isSelectedRow,
  overflowX = "auto",
  disableBottomBorderForLastRow = false,
  tableLayout = "auto",
  enableSearchQueryParam,
  enablePaginationQueryParam,
  manualPagination,
  manualGlobalFiltering
}) => {
  const headerRef = useRef();

  const { classes } = useStyles();

  const { stickyHeaderCellStyles, stickyTableStyles } = useSticky({
    headerRef,
    stickySettings
  });

  const getRowHoverProperties = (row) => {
    if (typeof onRowClick !== "function" || typeof isSelectedRow !== "function") {
      return {};
    }
    return {
      onClick: () => onRowClick(row.original),
      hover: true,
      selected: isSelectedRow(row.original),
      className: classes.hoverableRow
    };
  };

  const { tableOptions: sortingTableOptions } = useSortingTableSettings();

  const {
    state: globalFilterState,
    tableOptions: globalFilterTableOptions,
    onSearchChange,
    onRangeChange
  } = useGlobalFilterTableSettings({
    withSearch,
    queryParamPrefix,
    enableSearchQueryParam,
    rangeFilter,
    columns: columnsProperty
  });

  const { state: columnsVisibilityState, tableOptions: columnsVisibilityTableOptions } =
    useColumnsVisibility(columnsSelectorUID);

  const totalRowsCount = getRowsCount(data, {
    withExpanded,
    getSubRows
  });

  const { state: paginationState, tableOptions: paginationTableOptions } = usePaginationTableSettings({
    pageSize,
    rowsCount: totalRowsCount,
    queryParamPrefix,
    enablePaginationQueryParam
  });

  const columns = useColumns(columnsProperty, {
    withSelection
  });

  const { state: expandedState, tableOptions: expandedTableOptions } = useExpandedTableSettings({
    withExpanded,
    getSubRows,
    expanded,
    onExpandedChange
  });

  const { state: columnOrderState, tableOptions: columnOrderTableOptions } = useColumnOrderTableSettings({
    columnOrder,
    onColumnOrderChange
  });

  const { state: rowSelectionState, tableOptions: rowSelectionTableOptions } = useRowSelectionTableSettings({
    withSelection,
    rowSelection,
    onRowSelectionChange
  });

  const initialSortingState = useInitialSortingState(columns);

  const isManualPagination = !!manualPagination;
  const isManualFiltering = !!manualGlobalFiltering;

  const tableState = {
    ...(isManualFiltering ? {} : globalFilterState),
    ...(isManualPagination ? {} : paginationState),
    ...expandedState,
    ...columnOrderState,
    ...rowSelectionState,
    ...columnsVisibilityState
  };

  const tableOptions = {
    ...(isManualFiltering ? {} : globalFilterTableOptions),
    ...(isManualPagination ? {} : paginationTableOptions),
    ...expandedTableOptions,
    ...columnsVisibilityTableOptions,
    ...columnOrderTableOptions,
    ...rowSelectionTableOptions,
    ...sortingTableOptions
  };

  const table = useReactTable({
    data,
    columns,
    getRowId,
    initialState: {
      sorting: initialSortingState
    },
    defaultColumn: {
      sortDescFirst: false,
      /**
       * TODO: Check sorting of a columns with all equal values. The 8th version doesn't invert the rows order
       */
      sortingFn: "basic"
    },
    getCoreRowModel: getCoreRowModel(),
    state: tableState,
    ...tableOptions
  });

  const selectedRowsCount = withSelection ? table.getSelectedRowModel().flatRows.length : 0;

  const { rows } = table.getRowModel();

  const getPaginationSettings = () => {
    if (isManualPagination) {
      return {
        pageCount: manualPagination.pageCount,
        pageIndex: manualPagination.pageIndex,
        pageSize: manualPagination.pageSize,
        onPageIndexChange: manualPagination.onPageIndexChange,
        totalRows: manualPagination.totalRows
      };
    }

    return {
      pageCount: table.getPageCount(),
      pageIndex: table.getState().pagination.pageIndex,
      pageSize: table.getState().pagination.pageSize,
      onPageIndexChange: table.setPageIndex,
      totalRows: totalRowsCount
    };
  };

  const paginationSettings = getPaginationSettings();

  const getFilterOptions = () => {
    if (isManualFiltering) {
      return {
        withSearch,
        onSearchChange: withSearch ? manualGlobalFiltering.search.onChange : undefined,
        searchValue: withSearch ? manualGlobalFiltering.search.value : undefined,
        rangeFilter,
        rangeValue: rangeFilter ? manualGlobalFiltering.rangeFilter.range : undefined,
        onRangeChange: rangeFilter ? manualGlobalFiltering.rangeFilter.onChange : undefined
      };
    }

    return {
      withSearch,
      searchValue: withSearch ? globalFilterState.globalFilter.search : undefined,
      onSearchChange: withSearch ? (newSearchValue) => onSearchChange(newSearchValue, { tableContext: table }) : null,
      rangeFilter,
      rangeValue: rangeFilter ? globalFilterState.globalFilter.range : undefined,
      onRangeChange: rangeFilter ? (newRangeValue) => onRangeChange(newRangeValue, { tableContext: table }) : null
    };
  };

  const withPagination = paginationSettings.pageCount > 1;

  return (
    <div data-test-id={dataTestIds.container}>
      <TableActions
        actionBar={actionBar}
        selectedRowsCount={selectedRowsCount}
        {...getFilterOptions()}
        tableContext={table}
        columnsSelectorUID={columnsSelectorUID}
        columnSetsSelectorId={columnSetsSelectorId}
        /**
         * TODO: Split dataTestIds and pass only what belongs to TableActions
         */
        dataTestIds={dataTestIds}
      />
      {/* Wrap with box in order to make table fit 100% width with small amount of columns */}
      {/* TODO: Consider using MUI TableContainer */}
      <Box
        className={classes.tableContainer}
        sx={{
          overflowX
        }}
      >
        {isLoading ? (
          <TableLoader columnsCounter={columns.length ?? 5} showHeader />
        ) : (
          <MuiTable
            sx={{
              tableLayout
            }}
            style={{
              ...stickyTableStyles
            }}
          >
            {withHeader && (
              <TableHead ref={headerRef}>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <TableHeaderCell
                        key={header.id}
                        headerContext={header}
                        stickyStyles={stickyHeaderCellStyles}
                        getHeaderCellClassName={getHeaderCellClassName}
                      />
                    ))}
                  </TableRow>
                ))}
              </TableHead>
            )}
            <TableBody>
              {isEmptyArray(rows) ? (
                <TableRow
                  sx={
                    disableBottomBorderForLastRow
                      ? {
                          "&:last-child > td": {
                            borderBottom: "none"
                          }
                        }
                      : {}
                  }
                >
                  <TableCell align="center" colSpan={columns.length}>
                    <FormattedMessage id={localization.emptyMessageId || DEFAULT_EMPTY_MESSAGE_ID} />
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row, index) => {
                  const rowStyle = typeof getRowStyle === "function" ? getRowStyle(row.original) : {};

                  return (
                    <TableRow
                      {...getRowHoverProperties(row)}
                      data-test-id={`row_${index}`}
                      key={row.id}
                      style={rowStyle}
                      sx={
                        disableBottomBorderForLastRow
                          ? {
                              "&:last-child > td": {
                                borderBottom: "none"
                              }
                            }
                          : {}
                      }
                    >
                      {row.getVisibleCells().map((cell) => {
                        if (cell.column.id === SELECTION_COLUMN_ID) {
                          return <TableBodyCell key={cell.id} cell={cell} />;
                        }
                        const Cell = memoBodyCells ? MemoTableBodyCell : TableBodyCell;

                        return (
                          <Cell
                            key={cell.id}
                            cell={cell}
                            className={
                              typeof getRowCellClassName === "function" ? getRowCellClassName(cell.getContext()) : undefined
                            }
                          />
                        );
                      })}
                    </TableRow>
                  );
                })
              )}
            </TableBody>
            {withFooter && (
              <TableFooter>
                {table.getFooterGroups().map((footerGroup) => (
                  <TableRow key={footerGroup.id}>
                    {footerGroup.headers.map((footerContext) => (
                      <TableFooterCell key={footerContext.id} footerContext={footerContext} />
                    ))}
                  </TableRow>
                ))}
              </TableFooter>
            )}
          </MuiTable>
        )}
      </Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          paddingTop: SPACING_1,
          flexWrap: "wrap",
          flexDirection: { xs: "column-reverse", md: "row" },
          ":empty": { display: "none" }
        }}
      >
        <InfoArea
          counters={counters}
          rowsCount={rows.length}
          selectedRowsCount={selectedRowsCount}
          dataTestIds={dataTestIds.infoAreaTestIds}
          showAllLink={showAllLink}
          pagination={paginationSettings}
          withSearch={withSearch}
          withSelection={withSelection}
          withPagination={withPagination}
        />
        {paginationSettings.pageCount > 1 && (
          <Pagination
            count={paginationSettings.pageCount}
            page={paginationSettings.pageIndex + 1}
            paginationHandler={paginationSettings.onPageIndexChange}
          />
        )}
      </Box>
    </div>
  );
};

export default Table;
