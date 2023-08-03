import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { addSize, removeSizes, resetSelection } from "../actionCreator";

export const useSelectionActions = () => {
  const dispatch = useDispatch();

  return {
    resetSelection: useCallback(() => dispatch(resetSelection()), [dispatch]),
    addSize: useCallback((flavor) => dispatch(addSize(flavor)), [dispatch]),
    removeSize: useCallback((flavor) => dispatch(removeSizes(flavor)), [dispatch])
  };
};
