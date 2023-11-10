import { makeStyles } from "tss-react/mui";

const HOVER = "hover";

const useStyles = makeStyles()((theme, { borderWidth }) => ({
  wrapper: {
    "& svg": {
      [`& .${HOVER}`]: {
        strokeWidth: borderWidth + 1,
        cursor: "pointer"
      }
    }
  }
}));

export const useChartHoverStyles = ({ borderWidth = 0 }) => {
  const { classes } = useStyles({ borderWidth });

  const addHoverClass = (element) => {
    element.classList.add(HOVER);
  };

  const removeHoverClass = (element) => {
    element.classList.remove(HOVER);
  };

  return [classes.wrapper, addHoverClass, removeHoverClass];
};
