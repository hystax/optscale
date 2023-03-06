import { START_TOUR, FINISH_TOUR } from "./actionTypes";

export const startTour = (label) => ({
  label,
  type: START_TOUR
});

export const finishTour = (label) => ({
  label,
  type: FINISH_TOUR
});
