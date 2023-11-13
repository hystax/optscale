import MuiBackdrop from "@mui/material/Backdrop";
import Collapse from "@mui/material/Collapse";
import useStyles from "./Backdrop.styles";

const Backdrop = ({ children, customClass, open = true, aboveDrawers = false }) => {
  const { classes, cx } = useStyles(aboveDrawers);

  return (
    <MuiBackdrop className={cx(classes.backdrop, classes[customClass])} open={open} TransitionComponent={Collapse}>
      {children}
    </MuiBackdrop>
  );
};

export default Backdrop;
