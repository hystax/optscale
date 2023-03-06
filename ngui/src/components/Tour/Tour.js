import React from "react";
import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { finishTour } from "./actionCreators";
import { TOURS_DEFINITIONS } from "./definitions";
import { useProductTour } from "./hooks";
import { TOURS } from "./reducer";
import TourUi from "./TourUi";

const Tour = () => {
  const dispatch = useDispatch();

  const { rootData = {} } = useRootData(TOURS);
  const currentTourId = Object.entries(rootData).find(([, { isOpen }]) => isOpen)?.[0] ?? "";
  const { isOpen } = useProductTour(currentTourId);

  const steps = currentTourId ? TOURS_DEFINITIONS[currentTourId] : null;

  const close = () => {
    dispatch(finishTour(currentTourId));
  };

  return isOpen && <TourUi steps={steps} close={close} />;
};

export default Tour;
