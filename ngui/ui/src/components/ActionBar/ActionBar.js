import React, { Fragment, createRef } from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import MoreVertOutlinedIcon from "@mui/icons-material/MoreVertOutlined";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import List from "@mui/material/List";
import MenuItem from "@mui/material/MenuItem";
import Switch from "@mui/material/Switch";
import Toolbar from "@mui/material/Toolbar";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import ActionBarHeader from "components/ActionBarHeader";
import Breadcrumbs from "components/Breadcrumbs";
import ButtonGroup from "components/ButtonGroup";
import ButtonLoader from "components/ButtonLoader";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import { useAllowedItems } from "hooks/useAllowedActions";
import { isEmpty, splitIntoTwoChunks } from "utils/arrays";
import { SCOPE_TYPES } from "utils/constants";
import useStyles from "./ActionBar.styles";
import { COLLAPSE_MODE, HIDE_MODE, useHideActionsForSmallScreens } from "./useHideActionsForSmallScreens";

const getButton = (item) => (
  <ButtonLoader
    isLoading={item.isLoading}
    messageId={item.messageId}
    link={item.link}
    href={item.href}
    download={item.download}
    disabled={item.disabled}
    onClick={item.action}
    dataTestId={item.dataTestId}
    dataProductTourId={item.dataProductTourId}
    variant={item.variant || "text"}
    color={item.color}
    startIcon={item.icon}
    tooltip={item.tooltip}
  />
);

// TODO: to add support for a mobile view
const renderIconButton = (item) => (
  <IconButton
    icon={item.icon}
    isLoading={item.isLoading}
    link={item.link}
    href={item.href}
    disabled={item.disabled}
    onClick={item.action}
    dataTestId={item.dataTestId}
    dataProductTourId={item.dataProductTourId}
    tooltip={item.tooltip}
  />
);

const renderButton = (item) => {
  const { show = true } = item;

  return show ? getButton(item) : null;
};

const renderSwitch = (item) => (
  <Box key={item.key} display="flex" alignItems="center">
    <Switch
      checked={item.checked}
      onChange={item.action}
      color="secondary"
      inputProps={{ "aria-label": "secondary checkbox" }}
    />
    <Box whiteSpace="nowrap">
      <FormattedMessage id={item.messageId} />
    </Box>
  </Box>
);

const onMenuItemClick = (action, onClose) => {
  if (typeof action === "function") {
    action();
  }
  onClose();
};

/**
 * TODO: There is no mobile support for custom nodes, e.g date pickers
 */
const DropDownMenu = ({ items, onClose }) => {
  const { classes } = useStyles();

  const getItem = (menuItem, parentMenuItem = null) => {
    const item = (
      <MenuItem
        key={menuItem.key}
        onClick={() => {
          if (!menuItem.disabled) {
            onMenuItemClick(menuItem.action, onClose);
          }
        }}
        data-test-id={menuItem.dataTestId}
        disabled={menuItem.disabled}
        style={menuItem.disabled ? { pointerEvents: "all" } : {}}
      >
        {parentMenuItem && (
          // If an item is nested, skip the "parent" and
          // render just nested items with combined parent and child messages
          <>
            <FormattedMessage id={parentMenuItem.messageId} />
            &nbsp;
          </>
        )}
        {menuItem.text ?? <FormattedMessage id={menuItem.messageId} />}
      </MenuItem>
    );

    if (menuItem.link) {
      return (
        <NavLink to={menuItem.link} className={classes.link}>
          {item}
        </NavLink>
      );
    }

    if (menuItem.href) {
      return (
        <Link href={menuItem.href} className={classes.link} target="_blank" rel="noopener">
          {item}
        </Link>
      );
    }

    return item;
  };

  return (
    <List>
      {items.map((menuItem) => {
        const { show = true } = menuItem;
        if (show) {
          if (menuItem?.menu?.items) {
            return menuItem.menu.items.map((nestedMenuItem) => getItem(nestedMenuItem, menuItem));
          }
          return getItem(menuItem);
        }
        return null;
      })}
    </List>
  );
};

const renderDropdown = (item) => (
  <Popover
    renderMenu={({ closeHandler }) => <DropDownMenu items={item.menu.items} onClose={closeHandler} />}
    label={({ isOpen }) => (
      <ButtonLoader
        dataTestId={item.dataTestId}
        messageId={item.messageId}
        variant="text"
        startIcon={item.startIcon}
        isLoading={item.isLoading}
        endIcon={isOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
        tooltip={item.tooltip}
      />
    )}
  />
);

const renderButtonGroup = ({ buttons, activeButtonId }) => (
  <ButtonGroup buttons={buttons} activeButtonIndex={buttons.indexOf(buttons.find((button) => button.id === activeButtonId))} />
);

const renderItems = (barItems) => {
  const getItem = (type) => {
    const types = {
      button: renderButton,
      iconButton: renderIconButton,
      dropdown: renderDropdown,
      switch: renderSwitch,
      buttonGroup: renderButtonGroup,
      custom: ({ node }) => node
    };
    return types[type];
  };

  return barItems.map((item) => <Fragment key={item.key}>{getItem(item.type)(item)}</Fragment>);
};

const renderTitle = (title, ref) => {
  const CustomTitleComponent = title.custom;
  return CustomTitleComponent ? (
    <CustomTitleComponent reference={ref} />
  ) : (
    title.custom ?? (
      <ActionBarHeader
        dataTestId={title.dataTestId || null}
        dataProductTourId={title.dataProductTourId || null}
        text={title.text || null}
        messageId={title.messageId || null}
        isLoading={title.isLoading}
        logo={title.logo || null}
        ref={ref}
      />
    )
  );
};

const getUseIsAllowedParameters = (poolId) => (poolId ? { entityType: SCOPE_TYPES.POOL, entityId: poolId } : {});

const ActionBar = ({ data, isPage = true }) => {
  const { classes, cx } = useStyles();
  const { items = [], title, breadcrumbs, barClass = classes.bar, poolId = null, hideItemsOnSmallScreens = true } = data;

  const mapBarClass = cx(barClass, isPage ? classes.isPage : "");
  const actionsClasses = cx(classes.margin, classes.actions);

  const allowedItems = useAllowedItems({ ...getUseIsAllowedParameters(poolId), items });
  const showable = allowedItems.filter(({ show }) => show !== false);
  const isEmptyActions = isEmpty(showable);

  // need to use createRef, so reference object could trigger useEffect inside useHideActionsForSmallScreens
  // useRef will set all of them to null initially
  const titleRef = createRef();
  const buttonsRef = createRef();
  const wrapperRef = createRef();

  const { hiddenElementsLength } = useHideActionsForSmallScreens({
    enabled: hideItemsOnSmallScreens,
    wrapperRef,
    titleRef,
    buttonsRef,
    itemsLength: showable.length,
    mode: isPage ? HIDE_MODE : COLLAPSE_MODE,
    breakpoint: "md"
  });

  const [hidden, visible] = splitIntoTwoChunks(showable, hiddenElementsLength);

  const showBreadcrumbs = !!breadcrumbs && !title.isLoading;

  return title || !isEmptyActions ? (
    <AppBar position="static" className={mapBarClass}>
      <Toolbar disableGutters ref={wrapperRef}>
        <Box pt={2} pb={2} width="100%">
          {showBreadcrumbs ? <Breadcrumbs withSlashAtTheEnd>{breadcrumbs}</Breadcrumbs> : null}
          <Box display="flex" width="100%">
            {title ? (
              <Box display="flex" flexGrow="1" alignItems="center">
                {renderTitle(title, titleRef)}
              </Box>
            ) : null}
            {!isEmptyActions ? (
              <Box className={classes.itemsWrapper} ref={buttonsRef}>
                {!isEmpty(hidden) && (
                  <Box component="div" className={actionsClasses}>
                    <Popover
                      renderMenu={({ closeHandler }) => <DropDownMenu items={hidden} onClose={closeHandler} />}
                      label={<IconButton isLoading={hidden.some((item) => item.isLoading)} icon={<MoreVertOutlinedIcon />} />}
                    />
                  </Box>
                )}
                {!isEmpty(visible) && (
                  <Box component="div" className={actionsClasses}>
                    {renderItems(visible)}
                  </Box>
                )}
              </Box>
            ) : null}
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  ) : null;
};

ActionBar.propTypes = {
  data: PropTypes.object.isRequired,
  isPage: PropTypes.bool
};

export default ActionBar;
