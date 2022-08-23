import React from "react";
import MuiSkeleton from "@mui/material/Skeleton";
import PropTypes from "prop-types";
import useStyles from "./Skeleton.styles";

const Skeleton = ({ children, fullWidth, ...rest }) => {
  const { classes } = useStyles();

  const skeletonClasses = fullWidth ? classes.fullWidth : "";

  return (
    <MuiSkeleton className={skeletonClasses} {...rest}>
      {children}
    </MuiSkeleton>
  );
};

Skeleton.propTypes = {
  children: PropTypes.node,
  fullWidth: PropTypes.bool
};

export default Skeleton;
