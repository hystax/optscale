import { handleChange } from "../utils";

export const useColumnOrderTableSettings = ({ columnOrder, onColumnOrderChange }) => {
  if (!!columnOrder && Array.isArray(columnOrder)) {
    return {
      state: {
        columnOrder
      },
      tableOptions: {
        onColumnOrderChange:
          typeof onColumnOrderChange === "function" ? handleChange(columnOrder, onColumnOrderChange) : undefined
      }
    };
  }

  return {
    state: {},
    tableOptions: {}
  };
};
