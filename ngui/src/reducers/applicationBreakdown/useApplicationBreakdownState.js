import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { setBreakdowns as setBreakdownsActionCreator } from "./actionCreator";
import { APPLICATION_BREAKDOWN } from "./reducer";

export const useApplicationBreakdownState = ({ applicationId, storeId, defaultSelectedBreakdowns = [] }) => {
  const dispatch = useDispatch();

  const selectedBreakdowns = useSelector(
    (state) => state[APPLICATION_BREAKDOWN]?.[applicationId]?.[storeId] ?? defaultSelectedBreakdowns
  );

  const setBreakdowns = useCallback(
    (values) => {
      dispatch(setBreakdownsActionCreator(storeId, applicationId, values));
    },
    [applicationId, dispatch, storeId]
  );

  const addBreakdown = useCallback(
    (breakdownName) => {
      const breakdowns = [...selectedBreakdowns, breakdownName];

      dispatch(setBreakdownsActionCreator(storeId, applicationId, breakdowns));
    },
    [applicationId, dispatch, selectedBreakdowns, storeId]
  );

  const removeBreakdown = useCallback(
    (breakdownName) => {
      const breakdowns = selectedBreakdowns.filter((name) => name !== breakdownName);

      dispatch(setBreakdownsActionCreator(storeId, applicationId, breakdowns));
    },
    [applicationId, dispatch, selectedBreakdowns, storeId]
  );

  return {
    selectedBreakdowns,
    setBreakdowns,
    addBreakdown,
    removeBreakdown
  };
};
