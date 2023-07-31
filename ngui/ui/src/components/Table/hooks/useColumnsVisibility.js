import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { COLUMNS, saveHiddenColumns } from "reducers/columns";

export const useColumnsVisibility = (columnsSelectorUID) => {
  const dispatch = useDispatch();

  const { rootData: savedHiddenColumns = [] } = useRootData(COLUMNS, (result) => result?.[columnsSelectorUID]);

  const columnVisibility = Object.fromEntries(savedHiddenColumns.map((colName) => [colName, false]));

  const onColumnVisibilityChange = (stateUpdater) => {
    // stateUpdater is an object in case the getToggleAllColumnsVisibilityHandler() were applied to toggle the visibility state
    const newColumnsVisibleState = typeof stateUpdater === "function" ? stateUpdater(columnVisibility) : stateUpdater;

    const hiddenColumns = Object.entries(newColumnsVisibleState)
      .filter(([, isVisible]) => !isVisible)
      .map(([colName]) => colName);

    dispatch(saveHiddenColumns(columnsSelectorUID, hiddenColumns));
  };

  return {
    state: {
      columnVisibility
    },
    tableOptions: {
      onColumnVisibilityChange
    }
  };
};
