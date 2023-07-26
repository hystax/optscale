import React from "react";
import { Typography } from "@mui/material";
import useStyles from "./MonoTypography.styles";

const MonoTypography = ({ classes: classesProp = {}, ...props }) => {
  const { classes, cx } = useStyles();

  return <Typography {...props} className={cx(classes.mono, ...Object.values(classesProp))} />;
};

export default MonoTypography;
