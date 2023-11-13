import { useDispatch } from "react-redux";
import { updateMainMenuState } from "components/CollapsableMenuDrawer/actionCreators";
import { MAIN_MENU_EXPANDED } from "components/CollapsableMenuDrawer/reducer";
import { useRootData } from "hooks/useRootData";

export const useMainMenuState = () => {
  const dispatch = useDispatch();
  const { rootData: isExpanded } = useRootData(MAIN_MENU_EXPANDED);

  const updateIsExpanded = (newIsExpanded) => {
    dispatch(updateMainMenuState(newIsExpanded));
  };

  return {
    isExpanded,
    updateIsExpanded
  };
};

export default useMainMenuState;
