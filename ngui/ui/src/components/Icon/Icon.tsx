import { ComponentType, ReactNode } from "react";
import { SvgIconProps } from "@mui/material";
import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import Tooltip from "components/Tooltip";
import useStyles from "./Icon.styles";

type IconProps = {
  icon: ComponentType<{
    fontSize?: SvgIconProps["fontSize"];
    className?: string;
  }>;
  hasRightMargin?: boolean;
  hasLeftMargin?: boolean;
  fontSize?: SvgIconProps["fontSize"];
  color?: "info" | "success" | "warning" | "error";
  tooltip?: {
    show?: boolean;
    value?: string;
    messageId?: string;
    body?: ReactNode;
    placement?: "top" | "bottom" | "left" | "right";
  };
  dataTestId?: string;
};

const Icon = ({
  icon: IconComponent,
  hasRightMargin = false,
  hasLeftMargin = false,
  fontSize = "small",
  color = "info",
  tooltip = {},
  dataTestId,
}: IconProps) => {
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
