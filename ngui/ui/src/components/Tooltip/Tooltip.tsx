import MuiTooltip from "@mui/material/Tooltip";
import { withStyles } from "tss-react/mui";

const StyledTooltip = withStyles(MuiTooltip, (theme) => ({
  tooltip: {
    backgroundColor: theme.palette.common.white,
    color: "inherit",
    fontSize: theme.typography.pxToRem(12),
    border: "1px solid",
    borderColor: theme.palette.info.main
  }
}));

const Tooltip = ({ enterTouchDelay = 0, children, ...rest }) => (
  <StyledTooltip enterTouchDelay={enterTouchDelay} {...rest}>
    {children}
  </StyledTooltip>
);

export default Tooltip;
