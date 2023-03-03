import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { startTour } from "./actionCreators";
import { TOURS } from "./reducer";

export const useStartTour = () => {
  const dispatch = useDispatch();

  const startTourCallback = useCallback(
    (tourId) => {
      dispatch(startTour(tourId));
    },
    [dispatch]
  );

  return startTourCallback;
};

export const useProductTour = (tourId) => {
  const { rootData: { [tourId]: { isOpen, isFinished } = {} } = {} } = useRootData(TOURS);
  return { isOpen, isFinished };
};
