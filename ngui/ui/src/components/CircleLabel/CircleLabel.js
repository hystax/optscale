import React from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Circle from "components/Circle";
import Tooltip from "components/Tooltip";

const CircleLabel = ({ figureColor, textFirst = true, label, tooltip = {} }) => {
  const { show: showTooltip = false, value = "", messageId = "", placement = "bottom" } = tooltip;

  return (
    <Box display="flex" alignItems="center">
      <span>{textFirst ? label : ""}</span>
      {showTooltip ? (
        <Tooltip title={value || <FormattedMessage id={messageId} />} placement={placement}>
          <Circle color={figureColor} ml={label && textFirst ? 0.5 : 0} mr={label && !textFirst ? 0.5 : 0} />
        </Tooltip>
      ) : (
        <Circle color={figureColor} ml={label && textFirst ? 0.5 : 0} mr={label && !textFirst ? 0.5 : 0} />
      )}
      {!textFirst ? <span>{label}</span> : null}
    </Box>
  );
};

CircleLabel.propTypes = {
  figureColor: PropTypes.string,
  label: PropTypes.node,
  textFirst: PropTypes.bool,
  tooltip: PropTypes.object
};

export default CircleLabel;
