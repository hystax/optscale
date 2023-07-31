import { useDispatch } from "react-redux";
import { useRootData } from "./useRootData";

const UPDATE_SHOW_LESS_THAN_VALUE = "UPDATE_SHOW_LESS_THAN_VALUE";

const updateShowLessThanValue = (value) => ({
  type: UPDATE_SHOW_LESS_THAN_VALUE,
  payload: value
});

export const SHOW_LESS_THAN_VALUE = "showLessThanValue";

export const reducer = (state = true, action) => {
  switch (action.type) {
    case UPDATE_SHOW_LESS_THAN_VALUE:
      return action.payload;
    default:
      return state;
  }
};

// TODO: that is copy of Show weekends stuff
export const useShowLessThanValue = () => {
  const dispatch = useDispatch();

  const { rootData: showLessThanValue = true } = useRootData(SHOW_LESS_THAN_VALUE);

  const onChange = (value) => {
    dispatch(updateShowLessThanValue(value));
  };

  return {
    showLessThanValue,
    onChange
  };
};
