import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import useStyles from "./Icon.styles";

const Icon = ({
  icon: IconComponent,
  hasRightMargin = false,
  hasLeftMargin = false,
  fontSize = "small",
  color = "info",
  tooltip = {},
  dataTestId
}) => {
  const { classes, cx } = useStyles();

  const { show: showTooltip = false, value = "", messageId = "", body, placement = "bottom" } = tooltip;

  const iconClasses = cx(classes.icon, hasRightMargin ? classes.right : "", hasLeftMargin ? classes.left : "", classes[color]);

  const icon = <IconComponent fontSize={fontSize} className={iconClasses} data-test-id={dataTestId} />;

  return showTooltip ? (
    <Tooltip
      title={body || (value ? <KeyValueLabel messageId={messageId} value={value} /> : <FormattedMessage id={messageId} />)}
      placement={placement}
    >
      {icon}
    </Tooltip>
  ) : (
    icon
  );
};

Icon.propTypes = {
  icon: PropTypes.elementType.isRequired,
  hasRightMargin: PropTypes.bool,
  hasLeftMargin: PropTypes.bool,
  fontSize: PropTypes.string,
  color: PropTypes.string,
  tooltip: PropTypes.shape({
    show: PropTypes.bool,
    messageId: PropTypes.string,
    body: PropTypes.node,
    value: PropTypes.any, // Proxy to KeyValueLabel
    placement: PropTypes.string
  }),
  dataTestId: PropTypes.string
};

export default Icon;
