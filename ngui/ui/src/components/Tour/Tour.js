import React, { useCallback, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { finishTour } from "./actionCreators";
import { TOURS_DEFINITIONS } from "./definitions";
import { useIsTourAvailableForCurrentBreakpoint, useProductTour, useUpdateTourStep } from "./hooks";
import { TOURS } from "./reducer";
import TourUi from "./TourUi";

const Tour = () => {
  const dispatch = useDispatch();

  const { rootData = {} } = useRootData(TOURS);
  const currentTourId = Object.entries(rootData).find(([, { isOpen }]) => isOpen)?.[0] ?? "";
  const { isOpen } = useProductTour(currentTourId);

  const steps = currentTourId ? TOURS_DEFINITIONS[currentTourId] : null;

  const close = useCallback(() => {
    dispatch(finishTour(currentTourId));
  }, [dispatch, currentTourId]);

  const isTourAvailableForCurrentBreakpoint = useIsTourAvailableForCurrentBreakpoint();

  useEffect(() => {
    if (!isTourAvailableForCurrentBreakpoint && isOpen) {
      close();
    }
  }, [close, isTourAvailableForCurrentBreakpoint, isOpen]);

  const updateTourStep = useUpdateTourStep();

  const onStepChange = useCallback((stepId) => updateTourStep(currentTourId, stepId), [currentTourId, updateTourStep]);

  return isOpen && <TourUi steps={steps} close={close} onStepChange={onStepChange} />;
};

export default Tour;
