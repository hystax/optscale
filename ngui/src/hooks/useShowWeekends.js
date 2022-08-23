import { useDispatch } from "react-redux";
import { useRootData } from "./useRootData";

const UPDATE_SHOW_WEEKENDS = "UPDATE_SHOW_WEEKENDS";

const updateShowWeekends = (value) => ({
  type: UPDATE_SHOW_WEEKENDS,
  payload: value
});

export const SHOW_WEEKENDS = "showWeekends";

export const reducer = (state = true, action) => {
  switch (action.type) {
    case UPDATE_SHOW_WEEKENDS:
      return action.payload;
    default:
      return state;
  }
};

export const useShowWeekends = () => {
  const dispatch = useDispatch();

  const { rootData: showWeekends = true } = useRootData(SHOW_WEEKENDS);

  const onChange = (value) => {
    dispatch(updateShowWeekends(value));
  };

  return {
    showWeekends,
    onChange
  };
};
