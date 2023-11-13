import { getExpandedRowModel } from "@tanstack/react-table";
import { isObject } from "utils/objects";
import { handleChange } from "../utils";

export const useExpandedTableSettings = ({ withExpanded, getSubRows, expanded, onExpandedChange }) => {
  if (withExpanded) {
    const defaultExpandedTableOptions = {
      getExpandedRowModel: getExpandedRowModel(),
      getSubRows
    };

    const isControlled = !!expanded && isObject(expanded) && typeof onExpandedChange === "function";

    if (isControlled) {
      return {
        state: {
          expanded
        },
        tableOptions: {
          ...defaultExpandedTableOptions,
          onExpandedChange: handleChange(expanded, onExpandedChange)
        }
      };
    }

    return {
      state: {},
      tableOptions: defaultExpandedTableOptions
    };
  }

  return {
    state: {},
    tableOptions: {}
  };
};
