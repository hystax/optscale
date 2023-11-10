import { useMemo } from "react";
import IndeterminateCheckbox from "../components/IndeterminateCheckbox";
import { SELECTION_COLUMN_ID } from "../utils/constants";

const addSelectionColumn = (columns) => {
  let lastCheckedRowIndex = 0;

  return [
    {
      id: SELECTION_COLUMN_ID,
      enableHiding: false,
      enableGlobalFilter: false,
      header: ({ table }) => (
        <IndeterminateCheckbox
          id="all"
          checked={table.getIsAllRowsSelected()}
          indeterminate={table.getIsSomeRowsSelected()}
          onChange={table.getToggleAllRowsSelectedHandler()}
        />
      ),
      cell: ({ row: currentRowContext, table: tableContext }) => {
        /**
         * TODO: Are we sure that we need to get sorted rows here?
         */
        const rows = tableContext.getSortedRowModel().flatRows;

        const toggleCurrentRowSelected = currentRowContext.getToggleSelectedHandler();

        return (
          <IndeterminateCheckbox
            id={currentRowContext.id}
            checked={currentRowContext.getIsSelected()}
            indeterminate={currentRowContext.getIsSomeSelected()}
            onChange={(event) => {
              const newValue = event.target.checked;

              toggleCurrentRowSelected(event);

              const thisRowIndex = currentRowContext.index;

              // Do shift click
              if (event.nativeEvent.shiftKey) {
                const beginIndex = Math.min(thisRowIndex, lastCheckedRowIndex);
                const endIndex = Math.max(thisRowIndex, lastCheckedRowIndex);

                // setting same value, as in shift-clicked item
                const toBeToggled = [];
                for (let i = beginIndex; i <= endIndex; i += 1) {
                  if (rows[i].id !== currentRowContext.id) {
                    toBeToggled.push([rows[i].id, newValue]);
                  }
                }

                tableContext.setRowSelection((currentSelectionState) => {
                  const newState = {
                    ...currentSelectionState,
                    ...Object.fromEntries(toBeToggled)
                  };
                  /**
                   * TODO: Investigate state format
                   * Is seems like the selection state object should contain only "selected" rows in the following format:
                   * { 0: true, 1: true, ... }
                   */
                  return Object.fromEntries(Object.entries(newState).filter(([, isSelected]) => isSelected));
                });
              }

              lastCheckedRowIndex = thisRowIndex;
            }}
          />
        );
      },
      style: {
        padding: 0,
        width: "48px"
      }
    },
    ...columns
  ];
};

export const useColumns = (defaultColumns, { withSelection }) =>
  useMemo(() => {
    let columns = [...defaultColumns];

    if (withSelection) {
      columns = addSelectionColumn(columns);
    }

    return columns;
  }, [defaultColumns, withSelection]);
