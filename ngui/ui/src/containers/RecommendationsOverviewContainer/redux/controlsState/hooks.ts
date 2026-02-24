import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { getSearchParams, updateSearchParams } from "utils/network";
import { RECOMMENDATIONS_CONTROLS_STATE } from "./reducer";

export const useControlState = ({ redux: { stateAccessor, actionCreator }, queryParamName, defaultValue, possibleStates }) => {
  const dispatch = useDispatch();

  const {
    rootData: { [stateAccessor]: reduxState },
  } = useRootData(RECOMMENDATIONS_CONTROLS_STATE);

  const [stateValue, setStateValue] = useState(() => {
    const { [queryParamName]: queryValue } = getSearchParams();

    if (queryValue) {
      return possibleStates.includes(queryValue) ? queryValue : defaultValue;
    }

    if (reduxState) {
      return possibleStates.includes(reduxState) ? reduxState : defaultValue;
    }

    return defaultValue;
  });

  useEffect(() => {
    updateSearchParams({ [queryParamName]: stateValue });
  }, [queryParamName, stateValue]);

  useEffect(() => {
    dispatch(actionCreator(stateValue));
  }, [actionCreator, dispatch, stateValue]);

  return [stateValue, setStateValue];
};
