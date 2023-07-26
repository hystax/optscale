import React from "react";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import { Link } from "react-router-dom";
import { getPathname, getQueryParams } from "utils/network";
import useStyles from "./MenuItem.styles";

const MenuItem = ({
  children,
  messageId,
  link,
  isActive,
  onClick,
  dataTestId,
  nested = false,
  isRootPath: isRootPathFn,
  icon: Icon = null,
  dataProductTourId
}) => {
  const { classes, cx } = useStyles();
  const intl = useIntl();

  const listItemClasses = cx("listItem", { [classes.nested]: nested });

  const onLinkClick = (e) => {
    const pathname = getPathname();

    const isRootPath = typeof isRootPathFn === "function" ? isRootPathFn(pathname, getQueryParams()) : pathname === link;

    if (isRootPath) {
      e.preventDefault();
    }

    return null;
  };

  const currentPath = getPathname();
  const currentQueryParams = getQueryParams();

  // TODO - we need to be able to pass values to formatted messages
  const renderItem = (
    <ListItem
      data-test-id={dataTestId}
      onClick={onClick}
      button
      data-product-tour-id={dataProductTourId}
      className={listItemClasses}
    >
      {Icon && (
        <ListItemIcon className={classes.icon}>
          <Icon fontSize="small" />
        </ListItemIcon>
      )}
      <ListItemText primary={intl.formatMessage({ id: messageId })} />
      {children}
    </ListItem>
  );

  const isLinkActive = typeof isActive === "function" ? isActive(currentPath, currentQueryParams) : link === currentPath;

  const renderNavLink = (
    <Link
      className={cx(classes.menuLink, isLinkActive ? classes.activeLink : "")}
      onClick={onLinkClick}
      to={{ pathname: link }}
    >
      {renderItem}
    </Link>
  );

  return link ? renderNavLink : renderItem;
};

MenuItem.propTypes = {
  children: PropTypes.node,
  messageId: PropTypes.string.isRequired,
  onClick: PropTypes.func,
  icon: PropTypes.object,
  nested: PropTypes.bool,
  link: PropTypes.string,
  dataTestId: PropTypes.string,
  isActive: PropTypes.func,
  isRootPath: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
  dataProductTourId: PropTypes.string
};

export default MenuItem;
