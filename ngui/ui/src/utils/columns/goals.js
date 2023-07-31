import React from "react";
import SettingsIcon from "@mui/icons-material/Settings";
import { Box, ListItemText, MenuItem } from "@mui/material";
import { FormattedMessage } from "react-intl";
import HeaderHelperCell from "components/HeaderHelperCell";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import RunGoals from "components/RunGoals";
import TextWithDataTestId from "components/TextWithDataTestId";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SORTING_ORDER } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const SortableHeader = ({
  columnContext,
  label,
  goalsKeyNameEntries,
  renderSortLabel,
  onSortByGoalKeyChange,
  sortByGoalKey
}) => (
  <Box display="flex">
    {renderSortLabel(label)}
    <Popover
      label={<IconButton icon={<SettingsIcon />} />}
      renderMenu={({ closeHandler }) => (
        <>
          <MenuItem style={{ pointerEvents: "none" }}>
            <ListItemText
              primary={
                <strong>
                  <FormattedMessage id="sortBy" />
                </strong>
              }
            />
          </MenuItem>
          {goalsKeyNameEntries.map(([key, name]) => (
            <MenuItem
              key={key}
              selected={key === sortByGoalKey}
              value={key}
              onClick={() => {
                onSortByGoalKeyChange(key);

                const isSorted = columnContext.getIsSorted();

                if (isSorted) {
                  columnContext.toggleSorting(isSorted === SORTING_ORDER.DESC);
                }

                closeHandler();
              }}
            >
              {name}
            </MenuItem>
          ))}
        </>
      )}
    />
  </Box>
);

const goalsColumn = ({
  headerMessageId,
  headerDataTestId,
  helperMessageId,
  accessorKey,
  goalsKeyNameEntries = [],
  onSortByGoalKeyChange,
  sortByGoalKey,
  columnSelector,
  enableSorting = true
}) => {
  const isSortingEnables = enableSorting && !isEmptyArray(goalsKeyNameEntries);

  const headerLabel = helperMessageId ? (
    <HeaderHelperCell titleDataTestId={headerDataTestId} titleMessageId={headerMessageId} helperMessageId={helperMessageId} />
  ) : (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id={headerMessageId} />
    </TextWithDataTestId>
  );

  return {
    header: isSortingEnables
      ? ({ column, renderSortLabel }) => (
          <SortableHeader
            label={headerLabel}
            columnContext={column}
            renderSortLabel={renderSortLabel}
            goalsKeyNameEntries={goalsKeyNameEntries}
            sortByGoalKey={sortByGoalKey}
            onSortByGoalKeyChange={onSortByGoalKeyChange}
          />
        )
      : headerLabel,
    accessorKey,
    enableSorting: isSortingEnables,
    sortingFn: (rowA, rowB) => {
      const reachedGoalsA = rowA.getValue(accessorKey);
      const reachedGoalsB = rowB.getValue(accessorKey);

      const rowAGoalValue = reachedGoalsA?.[sortByGoalKey]?.value;
      const rowBGoalValue = reachedGoalsB?.[sortByGoalKey]?.value;

      if (rowAGoalValue === undefined && rowBGoalValue !== undefined) {
        return -1;
      }

      if (rowAGoalValue !== undefined && rowBGoalValue === undefined) {
        return 1;
      }

      if (rowAGoalValue === undefined && rowBGoalValue === undefined) {
        return 0;
      }

      return rowAGoalValue - rowBGoalValue;
    },
    cell: ({ cell }) => {
      const reachedGoals = cell.getValue();

      if (isEmptyObject(reachedGoals)) {
        return CELL_EMPTY_VALUE;
      }

      return <RunGoals goals={reachedGoals} />;
    },
    columnSelector
  };
};

export default goalsColumn;
