import { useRootData } from "hooks/useRootData";
import { CLOUD_COST_COMPARISON_SELECTED_SIZES } from "../reducer";

export const useIsSizeSelected = (sizeId) => {
  const { rootData: isSelected } = useRootData(
    CLOUD_COST_COMPARISON_SELECTED_SIZES,
    (state) => !!state.find(({ id: idToFind }) => idToFind === sizeId)
  );

  return isSelected;
};
