import { isObject } from "utils/objects";
import { handleChange } from "../utils";

export const useRowSelectionTableSettings = ({ withSelection, rowSelection, onRowSelectionChange }) => {
  /**
   * Only controlled selection is supported, so "rowSelection" and "onRowSelectionChange" must be provided
   */
  if (withSelection && !!rowSelection && isObject(rowSelection) && typeof onRowSelectionChange === "function") {
    return {
      state: {
        rowSelection
      },
      tableOptions: {
        onRowSelectionChange: handleChange(rowSelection, onRowSelectionChange)
      }
    };
  }

  return {
    state: {},
    tableOptions: {}
  };
};
