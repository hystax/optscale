import React from "react";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import useStyles from "./DashedTypography.styles";

const DashedTypography = ({
  className,
  children,
  disablePointerOnHover = false,
  hasRightMargin = false,
  dataTestId,
  ...rest
}) => {
  const { classes, cx } = useStyles();

  const typographyClasses = cx(
    classes.dashed,
    disablePointerOnHover ? "" : classes.cursorPointer,
    hasRightMargin ? classes.right : "",
    className
  );

  return (
    <Typography className={typographyClasses} data-test-id={dataTestId} {...rest}>
      {children}
    </Typography>
  );
};

DashedTypography.propTypes = {
  children: PropTypes.node.isRequired,
  disablePointerOnHover: PropTypes.bool,
  className: PropTypes.string,
  hasRightMargin: PropTypes.bool,
  dataTestId: PropTypes.string
};

export default DashedTypography;
