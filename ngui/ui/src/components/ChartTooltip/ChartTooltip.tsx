import Typography from "@mui/material/Typography";
import { withStyles } from "tss-react/mui";
import useStyles from "./ChartTooltip.styles";

const TooltipTypography = withStyles(Typography, {
  root: {
    fontSize: "0.9rem"
  }
});

const ChartTooltip = ({ body }) => {
  const { classes } = useStyles();

  return (
    <TooltipTypography component="div" className={classes.container}>
      {body}
    </TooltipTypography>
  );
};

export default ChartTooltip;
