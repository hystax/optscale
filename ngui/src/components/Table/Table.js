import React from "react";
import { Box, TableBody, TableCell, TableHead, TableRow, TableSortLabel } from "@mui/material";
import MuiTable from "@mui/material/Table";
import { flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import TableLoader from "components/TableLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import { CELL_EMPTY_VALUE } from "utils/tables";
import InfoArea from "./components/InfoArea";
import Pagination from "./components/Pagination";
import TableActions from "./components/TableActions";
import {
  useColumnOrderTableSettings,
  useColumns,
  useColumnsVisibility,
  useExpandedTableSettings,
  useGlobalFilterTableSettings,
  useInitialSortingState,
  usePaginationTableSettings,
  useRowSelectionTableSettings,
  useSortingTableSettings
} from "./hooks";
import useStyles from "./Table.styles";
import { getRowsCount } from "./utils";

const DEFAULT_EMPTY_MESSAGE_ID = "noRecordsToDisplay";

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
  withSearch,
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
  columnOrder,
  onColumnOrderChange
}) => {
  const { showCounters = false, hideTotal = false, hideDisplayed = false } = counters;

  const { classes } = useStyles();

  const { tableOptions: sortingTableOptions } = useSortingTableSettings();

  const {
    state: globalFilterState,
    tableOptions: globalFilterTableOptions,
    onSearchChange
  } = useGlobalFilterTableSettings({
    queryParamPrefix
  });

  const { state: columnsVisibilityState, tableOptions: columnsVisibilityTableOptions } =
    useColumnsVisibility(columnsSelectorUID);

  const { state: paginationState, tableOptions: paginationTableOptions } = usePaginationTableSettings({
    pageSize,
    rowsCount: getRowsCount(data, {
      withExpanded,
      getSubRows
    }),
    queryParamPrefix
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

  const tableState = {
    ...globalFilterState,
    ...paginationState,
    ...expandedState,
    ...columnOrderState,
    ...rowSelectionState,
    ...columnsVisibilityState
  };

  const tableOptions = {
    ...globalFilterTableOptions,
    ...paginationTableOptions,
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

  const { flatRows: filteredSelectedFlatRows } = table.getFilteredSelectedRowModel();

  const selectedRowsCounts = withSelection ? filteredSelectedFlatRows.length : 0;

  const { rows } = table.getRowModel();

  return (
    <div data-test-id={dataTestIds.container}>
      <TableActions
        actionBar={actionBar}
        selectedRowsCount={selectedRowsCounts}
        withSearch={withSearch}
        onSearchChange={withSearch ? (newSearchValue) => onSearchChange(newSearchValue, { tableContext: table }) : null}
        searchValue={withSearch ? globalFilterState.globalFilter : ""}
        tableContext={table}
        columnsSelectorUID={columnsSelectorUID}
        /**
         * TODO: Split dataTestIds and pass only what belongs to TableActions
         */
        dataTestIds={dataTestIds}
      />
      {/* Wrap with box in order to make table fit 100% width with small amount of columns */}
      <Box className={classes.horizontalScroll}>
        {isLoading ? (
          <TableLoader columnsCounter={columns.length ?? 5} showHeader />
        ) : (
          <MuiTable>
            {withHeader && (
              <TableHead>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      const { style: cellStyle = {} } = header.column.columnDef;

                      const renderCell = ({ content, cellProps = {} }) => (
                        <TableCell
                          key={header.id}
                          colSpan={header.colSpan}
                          rowSpan={header.rowSpan}
                          style={cellStyle}
                          {...cellProps}
                        >
                          {content ? <strong>{content}</strong> : null}
                        </TableCell>
                      );

                      const renderContent = () => {
                        if (header.isPlaceholder) {
                          return renderCell({ content: null });
                        }

                        if (header.column.getCanSort()) {
                          const appliedSortDirection = header.column.getIsSorted();
                          const isSorted = ["asc", "desc"].includes(appliedSortDirection);
                          const labelSortDirection = appliedSortDirection === "desc" ? "desc" : "asc";

                          return renderCell({
                            content: (
                              <TableSortLabel active={isSorted} direction={labelSortDirection}>
                                {flexRender(header.column.columnDef.header, header.getContext())}
                              </TableSortLabel>
                            ),
                            cellProps: {
                              onClick: header.column.getToggleSortingHandler()
                            }
                          });
                        }

                        return renderCell({
                          content: flexRender(header.column.columnDef.header, header.getContext())
                        });
                      };

                      return renderContent();
                    })}
                  </TableRow>
                ))}
              </TableHead>
            )}
            <TableBody>
              {isEmptyArray(rows) ? (
                <TableRow>
                  <TableCell align="center" colSpan={columns.length}>
                    <FormattedMessage id={localization.emptyMessageId || DEFAULT_EMPTY_MESSAGE_ID} />
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((row, index) => {
                  const rowStyle = typeof getRowStyle === "function" ? getRowStyle(row.original) : {};

                  return (
                    <TableRow data-test-id={`row_${index}`} key={row.id} style={rowStyle}>
                      {row.getVisibleCells().map((cell) => {
                        const { style: cellStyle = {}, dataProductTourId, accessorKey, accessorFn } = cell.column.columnDef;

                        return (
                          <TableCell key={cell.id} data-product-tour-id={dataProductTourId} style={cellStyle}>
                            {cell.getValue() === undefined && (accessorKey !== undefined || accessorFn !== undefined)
                              ? cell.column.columnDef.emptyValue || CELL_EMPTY_VALUE
                              : flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </TableCell>
                        );
                      })}
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </MuiTable>
        )}
      </Box>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          paddingTop: SPACING_1,
          flexDirection: { xs: "column-reverse", md: "row" },
          ":empty": { display: "none" }
        }}
      >
        <InfoArea
          showCounters={showCounters}
          hideTotal={hideTotal}
          hideDisplayed={hideDisplayed}
          totalNumber={counters.total || data.length}
          rowsCount={rows.length}
          selectedRowsCount={selectedRowsCounts}
          dataTestIds={dataTestIds.infoAreaTestIds}
          showAllLink={showAllLink}
          tableContext={table}
        />
        {table.getPageCount() > 1 && (
          <Pagination
            count={table.getPageCount()}
            page={table.getState().pagination.pageIndex + 1}
            paginationHandler={(newPageIndex) => table.setPageIndex(newPageIndex)}
          />
        )}
      </Box>
    </div>
  );
};

Table.propTypes = {
  data: PropTypes.array.isRequired,
  columns: PropTypes.array.isRequired,
  isLoading: PropTypes.bool,
  getRowStyle: PropTypes.func,
  withHeader: PropTypes.bool,
  withSearch: PropTypes.bool,
  dataTestIds: PropTypes.object,
  queryParamPrefix: PropTypes.string,
  localization: PropTypes.shape({
    emptyMessageId: PropTypes.string
  }),
  pageSize: PropTypes.number,
  counters: PropTypes.shape({
    showCounters: PropTypes.bool,
    hideTotal: PropTypes.bool,
    hideDisplayed: PropTypes.bool
  }),
  showAllLink: PropTypes.string,
  withSelection: PropTypes.bool,
  withExpanded: PropTypes.bool,
  getSubRows: PropTypes.func,
  getRowId: PropTypes.func,
  expanded: PropTypes.object,
  onExpandedChange: PropTypes.func,
  actionBar: PropTypes.object,
  columnsSelectorUID: PropTypes.string,
  columnOrder: PropTypes.array,
  onColumnOrderChange: PropTypes.func,
  rowSelection: PropTypes.object,
  onRowSelectionChange: PropTypes.func
};

export default Table;
