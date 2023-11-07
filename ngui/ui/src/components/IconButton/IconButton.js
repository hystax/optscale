import React, { forwardRef } from "react";
import CircularProgress from "@mui/material/CircularProgress";
import MuiIconButton from "@mui/material/IconButton";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import useStyles from "./IconButton.styles";

const IconButton = forwardRef(
  (
    {
      dataTestId,
      dataProductTourId,
      icon,
      onClick,
      link,
      href,
      customClass,
      isLoading,
      disabled = false,
      color = "info",
      size = "small",
      type = "button",
      edge = false,
      tooltip = {},
      ...rest
    },
    ref
  ) => {
    const { classes } = useStyles();

    const { show: showTooltip = false, value = "", messageId = "", placement = "top" } = tooltip;

    const renderMuiIconButton = (
      <MuiIconButton
        {...rest}
        ref={ref}
        data-test-id={dataTestId}
        data-product-tour-id={dataProductTourId}
        onClick={onClick}
        disabled={disabled}
        className={customClass}
        size={size}
        edge={edge}
        type={type}
        color={color}
      >
        {icon}
      </MuiIconButton>
    );

    const renderButton = () =>
      showTooltip ? (
        <Tooltip title={value || <FormattedMessage id={messageId} />} placement={placement}>
          <span className={classes.tooltipSpan}>{renderMuiIconButton}</span>
        </Tooltip>
      ) : (
        renderMuiIconButton
      );

    const renderButtonOrLoader = () =>
      isLoading ? <CircularProgress size={24} className={classes.buttonProgress} /> : renderButton();

    const renderLinkButton = () => {
      if (link) {
        return (
          <NavLink color="inherit" to={link}>
            {renderButtonOrLoader()}
          </NavLink>
        );
      }
      return (
        <Link href={href} color="inherit" target="_blank" rel="noopener">
          {renderButtonOrLoader()}
        </Link>
      );
    };

    return link || href ? renderLinkButton() : renderButtonOrLoader();
  }
);

IconButton.propTypes = {
  icon: PropTypes.node,
  onClick: PropTypes.func,
  size: PropTypes.oneOf(["small", "medium"]),
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  color: PropTypes.oneOf(["inherit", "primary", "success", "error", "info"]),
  edge: PropTypes.oneOf(["start", "end", false]),
  link: PropTypes.string,
  href: PropTypes.string,
  customClass: PropTypes.string,
  type: PropTypes.string,
  tooltip: PropTypes.shape({
    show: PropTypes.bool,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
    messageId: PropTypes.string,
    placement: PropTypes.string
  }),
  dataTestId: PropTypes.string,
  dataProductTourId: PropTypes.string
};

export default IconButton;
