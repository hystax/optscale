import { isEmpty } from "utils/objects";

const getBarColor = (colorsMap) => (bar) => colorsMap[bar.id];

export const useBarChartColors = (palette, colorsMap) => (isEmpty(colorsMap) ? [...palette] : getBarColor(colorsMap));
