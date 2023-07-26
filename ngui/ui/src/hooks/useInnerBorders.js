import { useIsUpMediaQuery } from "./useMediaQueries";

export const useInnerBorders = ({ tileCount, columns, borderStyle, lastChildBorderOnMobile }) => {
  const isUpSm = useIsUpMediaQuery("sm");
  const getLeftBorderCondition = (i) => i % columns !== 0 && isUpSm;
  const lastBorderIndexOnMobile = lastChildBorderOnMobile ? 0 : 1;
  const getBottomBorderCondition = (i) => i < tileCount - (isUpSm ? columns : lastBorderIndexOnMobile);

  return (i) => ({
    borderLeft: getLeftBorderCondition(i) ? borderStyle : "",
    borderBottom: getBottomBorderCondition(i) ? borderStyle : ""
  });
};
