import { makeStyles } from "tss-react/mui";

const HOVER = "hover";

const useStyles = makeStyles()((theme, { borderWidth, isClickable }) => ({
  wrapper: {
    "& svg": {
      [`& .${HOVER}`]: {
        strokeWidth: borderWidth + 1,
        cursor: isClickable ? "pointer" : "auto"
      }
    }
  }
}));

export const useChartHoverStyles = ({ borderWidth = 0, isClickable = false }) => {
  const { classes } = useStyles({ borderWidth, isClickable });

  const addHoverClass = (element) => {
    element.classList.add(HOVER);
  };

  const removeHoverClass = (element) => {
    element.classList.remove(HOVER);
  };

  return [classes.wrapper, addHoverClass, removeHoverClass];
};
