import React from "react";
import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import { capitalize } from "utils/strings";
import useStyles from "./ProgressBar.styles";

const ProgressBar = ({ children, value, width = "auto", color = "primary", tooltip = {} }) => {
  const { classes, cx } = useStyles();

  const { show: showTooltip = false, value: tooltipValue = "", messageId = "", placement = "top" } = tooltip;

  const renderProgress = () => (
    <Box className={classes.wrapper} width={width}>
      <LinearProgress
        className={cx(classes.progress, classes["progress".concat(capitalize(color))])}
        classes={{
          bar: classes["bar".concat(capitalize(color))]
        }}
        variant="determinate"
        value={value > 100 ? 100 : value || 0}
      />
      <Box className={classes.valueWrapper}>{children}</Box>
    </Box>
  );

  return showTooltip ? (
    <Tooltip title={tooltipValue || <FormattedMessage id={messageId} />} placement={placement}>
      {renderProgress()}
    </Tooltip>
  ) : (
    renderProgress()
  );
};

ProgressBar.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number,
  width: PropTypes.string,
  color: PropTypes.string,
  tooltip: PropTypes.object
};

export default ProgressBar;
