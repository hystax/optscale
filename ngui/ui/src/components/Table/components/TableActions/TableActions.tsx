import { Slider } from "@mui/material";
import Box from "@mui/material/Box";
import ActionBar from "components/ActionBar";
import SearchInput from "components/SearchInput";
import ColumnSets from "../ColumnSets";
import ColumnsSelector from "../ColumnsSelector";
import useStyles from "./TableActions.styles";

const TableActionBar = ({ actionBarDefinition, tableContext, selectedRowsCount }) => {
  const getActionBarItems = () =>
    actionBarDefinition.items.map((item) => {
      const { enableIfSelectedRows, ...rest } = typeof item === "function" ? item(tableContext) : item;

      return {
        /**
         * TODO: enableIfSelectedRows looks to specific, perhaps we could create a function and pass a set of properties there
         * and then let the action bar item decide if is has to be disabled
         * For example:
         * ```
         *   disabled: item.isDisabled({ selectedRowsCount })
         * ```
         */
        disabled: enableIfSelectedRows && selectedRowsCount === 0,
        ...rest
      };
    });

  return (
    <Box>
      <ActionBar
        isPage={false}
        data={{
          items: getActionBarItems()
        }}
      />
    </Box>
  );
};

const TableActions = ({
  selectedRowsCount = 0,
  actionBar = {},
  withSearch,
  onSearchChange,
  searchValue = "",
  rangeFilter,
  onRangeChange,
  rangeValue,
  tableContext,
  columnsSelectorUID,
  columnSetsSelectorId,
  dataTestIds = {}
}) => {
  const { classes } = useStyles();

  const { columnsSelector: columnsSelectorTestIds = {} } = dataTestIds;
  const { show: showActionBar = false, definition: actionBarDefinition } = actionBar;

  const withColumnsSelector = !!columnsSelectorUID;
  const withColumnSetsSelector = !!columnSetsSelectorId;

  const withRangeFilter = !!rangeFilter;

  const gotSomethingToDisplay = showActionBar || withSearch || withRangeFilter || withColumnsSelector || withColumnSetsSelector;

  /**
   * TODO: Do not render TableActions completely if there is nothing to display
   */
  if (!gotSomethingToDisplay) {
    return null;
  }

  return (
    <Box className={classes.actionsWrapper}>
      {showActionBar && (
        <TableActionBar
          actionBarDefinition={actionBarDefinition}
          tableContext={tableContext}
          selectedRowsCount={selectedRowsCount}
        />
      )}
      <Box
        sx={{
          marginLeft: showActionBar ? "" : "auto",
          display: "flex",
          flexWrap: withSearch && withColumnSetsSelector && withColumnsSelector ? "wrap" : "nowrap",
          gap: 1
        }}
      >
        {withSearch && <SearchInput onSearch={onSearchChange} initialSearchText={searchValue} dataTestIds={dataTestIds} />}
        <Box display="flex" flexWrap="nowrap">
          {withColumnsSelector && <ColumnsSelector tableContext={tableContext} dataTestIds={columnsSelectorTestIds} />}
          {withColumnSetsSelector && <ColumnSets tableContext={tableContext} />}
        </Box>
      </Box>
      {withRangeFilter && (
        <Box flexGrow={1} px={2}>
          {rangeFilter.title(rangeValue)}
          <Slider
            getAriaLabel={() => ""}
            value={rangeValue}
            step={rangeFilter.step}
            min={rangeFilter.min}
            max={rangeFilter.max}
            onChange={(_, segment) => {
              let [a, b] = segment;
              a = a === b && b === rangeFilter.max ? Math.max(0, a - rangeFilter.step) : a;
              b = a === b && b !== rangeFilter.max ? Math.min(rangeFilter.max, a + rangeFilter.step) : b;
              onRangeChange([a, b]);
            }}
            valueLabelDisplay="off"
          />
        </Box>
      )}
    </Box>
  );
};

export default TableActions;
