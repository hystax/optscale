import React from "react";
import IndeterminateCheckbox from "./IndeterminateCheckbox";

export const useCheckboxesColumn = (() => {
  const plug = (hooks) => {
    const onSelectionChange = hooks.useCheckboxesColumnsOnSelectionChange();

    // variable will be used in shift-click selection
    let lastCheckedRowIndex = 0;

    hooks.allColumns.push((cols) => [
      {
        id: "selection",
        disableGlobalFilter: true,
        Header: ({ getToggleAllRowsSelectedProps, toggleAllRowsSelected }) => (
          <IndeterminateCheckbox
            id="all"
            {...getToggleAllRowsSelectedProps([
              {
                onChange: (e) => {
                  toggleAllRowsSelected(e.target.checked);
                  onSelectionChange();
                }
              }
            ])}
          />
        ),
        Cell: ({
          row,
          rows,
          toggleRowSelected,
          cell: {
            row: { id }
          }
        }) => (
          <IndeterminateCheckbox
            id={id}
            {...row.getToggleRowSelectedProps([
              {
                onChange: (e) => {
                  const newValue = e.target.checked;
                  row.toggleRowSelected(newValue); // toggle current row

                  // do shift click
                  const thisRowIndex = rows.indexOf(row);
                  if (e.nativeEvent.shiftKey) {
                    const beginIndex = Math.min(thisRowIndex, lastCheckedRowIndex);
                    const endIndex = Math.max(thisRowIndex, lastCheckedRowIndex);

                    // setting same value, as in shift-clicked item
                    for (let i = beginIndex; i <= endIndex; i += 1) {
                      if (rows[i] !== row) toggleRowSelected(rows[i].id, newValue); // we already toggled current row
                    }
                  }

                  lastCheckedRowIndex = thisRowIndex;

                  onSelectionChange();
                }
              }
            ])}
          />
        ),
        style: {
          padding: 0,
          width: "48px"
        }
      },
      ...cols
    ]);
  };

  plug.pluginName = "useCheckboxesColumn";

  return plug;
})();

// Plugin doesn't looks like official plugins due to possible problems with bundler treeshake
// https://github.com/tannerlinsley/react-table/discussions/2045
