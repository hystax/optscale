import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
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

ChartTooltip.propTypes = {
  body: PropTypes.node
};

export default ChartTooltip;
