import { useCallback } from "react";
import { useDispatch } from "react-redux";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { useRootData } from "hooks/useRootData";
import { startTour, updateTourStep as updateTourStepAction } from "./actionCreators";
import { TOURS_DEFINITIONS } from "./definitions";
import { TOURS } from "./reducer";

export const useIsTourAvailableForCurrentBreakpoint = () => {
  const isDesktop = useIsUpMediaQuery("md");

  return isDesktop;
};

export const useStartTour = () => {
  const dispatch = useDispatch();

  const isTourAvailableForCurrentBreakpoint = useIsTourAvailableForCurrentBreakpoint();

  return useCallback(
    (tourId) => {
      if (!isTourAvailableForCurrentBreakpoint) {
        return;
      }
      const stepId = TOURS_DEFINITIONS[tourId][0].id;
      dispatch(startTour(tourId, stepId));
    },
    [dispatch, isTourAvailableForCurrentBreakpoint]
  );
};

export const useUpdateTourStep = () => {
  const dispatch = useDispatch();

  return useCallback(
    (tourId, stepId) => {
      dispatch(updateTourStepAction(tourId, stepId));
    },
    [dispatch]
  );
};

export const useProductTour = (tourId) => {
  const { rootData: { [tourId]: { isOpen, isFinished, stepId } = {} } = {} } = useRootData(TOURS);
  return { isOpen, isFinished, stepId };
};
