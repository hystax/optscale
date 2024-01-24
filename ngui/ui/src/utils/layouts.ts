import { SUCCESS, WARNING, ERROR } from "utils/constants";

export const SPACING_1 = 1;
export const SPACING_2 = 2;
export const SPACING_3 = 3;
export const SPACING_4 = 4;
export const SPACING_5 = 5;
export const SPACING_6 = 6;

export const scrolledToBottom = (target) => target.scrollTop + document.documentElement.offsetHeight > target.scrollHeight;

/**
 * Calculate the approximate width of the provided text
 *
 * @param { string } text - The text whose width we want to calculate
 * @param { string } font - Font string (e.g. "12px sans-serif")
 *
 * @description
 * Calculates text width using the canvas "measureText" function
 *
 * @returns Rounded up to the next largest integer width
 */
export const getTextWidth = (text, font) => {
  const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
  const context = canvas.getContext("2d");
  context.font = font;
  const { width } = context.measureText(text);
  return Math.ceil(width);
};

export const getPoolColorStatus = (percent = 0) => {
  if (percent >= 90 && percent < 100) {
    return WARNING;
  }
  if (percent >= 100) {
    return ERROR;
  }
  return SUCCESS;
};

/**
 * Calculate border styles for n*2 cards/nodes layouts (home page, integrations)
 *
 * @param count - The number of cards/nodes
 * @param index - The current card/node index. Cards are iterated in a loop.
 *
 * TODO - improve to add a dynamic number of columns, more breakpoints
 * @returns The border styles object, ready to use for `sx`
 */
export const getSquareNodesStyle = (count: number, index: number) => ({
  borderRight: {
    xs: "0",
    lg: index % 2 === 0 ? "1px solid" : "0px solid"
  },
  borderBottom: {
    xs: index + 1 === count ? "0" : "1px solid",
    lg: index + 2 >= count ? "0" : "1px solid"
  },
  borderColor: {
    xs: "divider",
    lg: "divider"
  }
});
