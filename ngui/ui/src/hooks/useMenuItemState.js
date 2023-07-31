import { useDispatch } from "react-redux";
import { updateCollapsedMenuItems } from "components/MenuGroupWrapper/actionCreators";
import { COLLAPSED_MENU_ITEMS } from "components/MenuGroupWrapper/reducer";
import { useRootData } from "hooks/useRootData";

const useMenuItemState = (id) => {
  const dispatch = useDispatch();
  const { rootData: collapsedItems = [] } = useRootData(COLLAPSED_MENU_ITEMS);

  const isExpanded = !collapsedItems.includes(id);

  const updateIsExpanded = (newIsExpanded) => {
    let updatedItemsList;
    if (newIsExpanded) {
      updatedItemsList = collapsedItems.filter((itemId) => itemId !== id);
    } else {
      updatedItemsList = [...collapsedItems, id];
    }
    dispatch(updateCollapsedMenuItems(updatedItemsList));
  };

  return {
    isExpanded,
    updateIsExpanded
  };
};

export default useMenuItemState;
