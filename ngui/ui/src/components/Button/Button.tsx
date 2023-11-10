import { forwardRef } from "react";
import MuiButton from "@mui/material/Button";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import useStyles from "./Button.styles";

const Button = forwardRef(
  (
    {
      dataTestId,
      dataProductTourId,
      messageId,
      text,
      onClick,
      link,
      download,
      href,
      customClass,
      dashedBorder = false,
      size = "small",
      variant = "outlined",
      uppercase = true,
      disabled = false,
      color = "info",
      type = "button",
      tooltip = {},
      ...rest
    },
    ref
  ) => {
    const { classes, cx } = useStyles();

    const { show: showTooltip = false, value = "", messageId: tooltipMessageId = "", body, placement = "bottom" } = tooltip;

    const buttonClasses = cx(
      classes.button,
      uppercase ? classes.uppercase : "",
      dashedBorder ? classes.dashed : "",
      customClass || ""
    );

    const button = (
      <MuiButton
        {...rest}
        ref={ref}
        color={color}
        className={buttonClasses}
        data-test-id={dataTestId}
        data-product-tour-id={dataProductTourId}
        onClick={onClick}
        disabled={disabled}
        variant={variant}
        size={size}
        type={type}
      >
        {messageId ? <FormattedMessage id={messageId} /> : text}
      </MuiButton>
    );

    // We need span here to be able to add a tooltip for a disabled control
    // https://material-ui.com/components/tooltips/#disabled-elements
    const renderButton = () =>
      showTooltip ? (
        <Tooltip title={body || value || <FormattedMessage id={tooltipMessageId} />} placement={placement}>
          <span className={classes.tooltipSpan}>{button}</span>
        </Tooltip>
      ) : (
        button
      );

    // TODO: NGUI-1509. Need to bring the solution to one type(MenuItem, Button, Popover).
    const renderLinkButton = () => {
      if (link) {
        return disabled ? (
          renderButton()
        ) : (
          <NavLink to={link} className={classes.link}>
            {renderButton()}
          </NavLink>
        );
      }
      return disabled ? (
        renderButton()
      ) : (
        <Link href={href} className={classes.link} target="_blank" rel="noopener" download={download}>
          {renderButton()}
        </Link>
      );
    };

    return link || href ? renderLinkButton() : renderButton();
  }
);

export default Button;
