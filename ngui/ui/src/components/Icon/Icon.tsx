import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
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

  const { show: showTooltip = false, value = "", messageId = "", body, placement = "top" } = tooltip;

  const iconClasses = cx(classes.icon, hasRightMargin ? classes.right : "", hasLeftMargin ? classes.left : "", classes[color]);

  const icon = <IconComponent fontSize={fontSize} className={iconClasses} data-test-id={dataTestId} />;

  return showTooltip ? (
    <Tooltip
      title={body || (value ? <KeyValueLabel keyMessageId={messageId} value={value} /> : <FormattedMessage id={messageId} />)}
      placement={placement}
    >
      {icon}
    </Tooltip>
  ) : (
    icon
  );
};

export default Icon;
