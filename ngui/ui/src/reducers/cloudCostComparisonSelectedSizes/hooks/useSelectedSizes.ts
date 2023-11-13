import { useRootData } from "hooks/useRootData";
import { CLOUD_COST_COMPARISON_SELECTED_SIZES } from "../reducer";

export const useSelectedSizes = () => {
  const { rootData } = useRootData(CLOUD_COST_COMPARISON_SELECTED_SIZES);

  return rootData;
};
