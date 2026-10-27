import MuiTooltip, { TooltipProps } from "@mui/material/Tooltip";
import { withStyles } from "tss-react/mui";

const StyledTooltip = withStyles(MuiTooltip, (theme) => ({
  tooltip: {
    backgroundColor: theme.palette.common.white,
    color: "inherit",
    fontSize: theme.typography.pxToRem(12),
    border: "1px solid",
    borderColor: theme.palette.info.main,
  },
}));

const Tooltip = ({ enterTouchDelay = 0, children, placement = "right", title, ...rest }: TooltipProps) => {
  if (!title && title !== 0) {
    return children;
  }

  return (
    <StyledTooltip enterTouchDelay={enterTouchDelay} placement={placement} title={title} {...rest}>
      {children}
    </StyledTooltip>
  );
};

export default Tooltip;
