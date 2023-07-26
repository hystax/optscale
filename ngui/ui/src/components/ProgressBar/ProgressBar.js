import React from "react";
import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Tooltip from "components/Tooltip";
import { capitalize } from "utils/strings";
import useStyles from "./ProgressBar.styles";

const ProgressBar = ({ children, value, minWidth = "", color = "primary", tooltip = {} }) => {
  const { classes, cx } = useStyles();

  const { show: showTooltip = false, value: tooltipValue = "", messageId = "", placement = "top" } = tooltip;

  const renderProgress = () => (
    <Box className={classes.wrapper} minWidth={minWidth}>
      <LinearProgress
        className={classes.progress}
        classes={{
          bar: classes["bar".concat(capitalize(color))]
        }}
        variant="determinate"
        value={value > 100 ? 100 : value || 0}
      />
      <Box className={cx(classes.valueWrapper, classes["value".concat(capitalize(color))])}>{children}</Box>
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
  minWidth: PropTypes.string,
  color: PropTypes.string,
  tooltip: PropTypes.object
};

export default ProgressBar;
