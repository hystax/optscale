import SettingsIcon from "@mui/icons-material/Settings";
import { Box, ListItemText, MenuItem } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Circle from "components/Circle";
import HeaderHelperCell from "components/HeaderHelperCell";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import RunGoals from "components/RunGoals";
import { useGoalMetColors } from "hooks/useGoalMetColors";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SORTING_ORDER } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";
import { CELL_EMPTY_VALUE } from "utils/tables";

const SortableHeader = ({
  columnContext,
  label,
  metricsKeyNameEntries,
  renderSortLabel,
  onSortByMetricKeyChange,
  sortByMetricKey
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
          {metricsKeyNameEntries.map(([key, name]) => (
            <MenuItem
              key={key}
              selected={key === sortByMetricKey}
              value={key}
              onClick={() => {
                onSortByMetricKeyChange(key);

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

const GoalTypeDescription = ({ goalType }: { goalType: "goalMet" | "goalNotMet" }) => {
  const colors = useGoalMetColors();
  const color = colors[goalType];

  const messageId = {
    goalMet: "runMetricsDescription.goalMet",
    goalNotMet: "runMetricsDescription.goalNotMet"
  }[goalType];

  return (
    <div
      style={{
        display: "inline-flex"
      }}
    >
      <span
        style={{
          paddingTop: "2px"
        }}
      >
        <Circle fontSize="inherit" color={color} />
      </span>
      <span>
        <FormattedMessage id={messageId} />
      </span>
    </div>
  );
};

const metrics = ({
  accessorKey,
  metricsKeyNameEntries = [],
  onSortByMetricKeyChange,
  sortByMetricKey,
  columnSelector,
  enableSorting = true
}) => {
  const isSortingEnables = enableSorting && !isEmptyArray(metricsKeyNameEntries);

  const headerLabel = (
    <HeaderHelperCell
      titleDataTestId="lbl_metrics"
      titleMessageId="metrics"
      helperMessageId="runMetricsDescription"
      helperMessageValues={{
        br: <br />,
        goalMet: <GoalTypeDescription goalType="goalMet" />,
        goalNotMet: <GoalTypeDescription goalType="goalNotMet" />
      }}
    />
  );

  return {
    header: isSortingEnables
      ? ({ column, renderSortLabel }) => (
          <SortableHeader
            label={headerLabel}
            columnContext={column}
            renderSortLabel={renderSortLabel}
            metricsKeyNameEntries={metricsKeyNameEntries}
            sortByMetricKey={sortByMetricKey}
            onSortByMetricKeyChange={onSortByMetricKeyChange}
          />
        )
      : headerLabel,
    accessorKey,
    enableSorting: isSortingEnables,
    sortingFn: (rowA, rowB) => {
      const reachedMetricValuesA = rowA.getValue(accessorKey);
      const reachedMetricValuesB = rowB.getValue(accessorKey);

      const rowAReachedMetricValue = reachedMetricValuesA?.[sortByMetricKey]?.value;
      const rowBReachedMetricValue = reachedMetricValuesB?.[sortByMetricKey]?.value;

      if (rowAReachedMetricValue === undefined && rowBReachedMetricValue !== undefined) {
        return -1;
      }

      if (rowAReachedMetricValue !== undefined && rowBReachedMetricValue === undefined) {
        return 1;
      }

      if (rowAReachedMetricValue === undefined && rowBReachedMetricValue === undefined) {
        return 0;
      }

      return rowAReachedMetricValue - rowBReachedMetricValue;
    },
    cell: ({ cell }) => {
      const reachedMetricValues = cell.getValue();

      if (isEmptyObject(reachedMetricValues)) {
        return CELL_EMPTY_VALUE;
      }

      return <RunGoals goals={reachedMetricValues} />;
    },
    columnSelector
  };
};

export default metrics;
