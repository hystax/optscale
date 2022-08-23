import React, { Fragment, createRef } from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Switch from "@mui/material/Switch";
import Toolbar from "@mui/material/Toolbar";
import useMediaQuery from "@mui/material/useMediaQuery";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBarHeader from "components/ActionBarHeader";
import ButtonGroup from "components/ButtonGroup";
import ButtonLoader from "components/ButtonLoader";
import Dropdown from "components/Dropdown";
import GoBackButton from "components/GoBackButton";
import IconButton from "components/IconButton";
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
    size="large"
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

const renderDropdown = (item) => (
  <Dropdown
    dataTestId={item.dataTestId}
    popupId="desktopPopup"
    icon={item.icon}
    messageId={item.messageId}
    items={item.menu.items}
    tooltip={item.tooltip}
    trigger="button"
    isLoading={item.isLoading}
    disabled={item.disabled}
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
      buttonGroup: renderButtonGroup
    };
    return types[type];
  };

  return barItems.map((item) => <Fragment key={item.key}>{getItem(item.type)(item)}</Fragment>);
};

const renderTitle = (title, ref) =>
  title.text || title.messageId ? (
    <ActionBarHeader
      dataTestId={title.dataTestId || null}
      dataProductTourId={title.dataProductTourId || null}
      text={title.text || null}
      messageId={title.messageId || null}
      isLoading={title.isLoading}
      logo={title.logo || null}
      ref={ref}
    />
  ) : (
    title.custom
  );

const getTitleMargin = (goBack, isUpSm) => {
  if (isUpSm) {
    return goBack ? 2 : 4;
  }
  return goBack ? 0 : 2;
};

const getUseIsAllowedParameters = (poolId) => (poolId ? { entityType: SCOPE_TYPES.POOL, entityId: poolId } : {});

const ActionBar = ({ data, isPage = true }) => {
  const isUpSm = useMediaQuery((theme) => theme.breakpoints.up("sm"));
  const { classes, cx } = useStyles();
  const { items = [], title, goBack, barClass = classes.bar, poolId = null, hideItemsOnSmallScreens = true } = data;

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

  return title || !isEmptyActions ? (
    <AppBar position="static" className={mapBarClass}>
      <Toolbar disableGutters ref={wrapperRef}>
        {goBack ? <GoBackButton /> : null}
        {title ? (
          <Box display="flex" flexGrow="1" alignItems="center" ml={getTitleMargin(goBack, isUpSm)}>
            {renderTitle(title, titleRef)}
          </Box>
        ) : null}
        {!isEmptyActions ? (
          <Box className={classes.itemsWrapper} ref={buttonsRef}>
            {!isEmpty(hidden) && (
              <Box component="div" className={actionsClasses}>
                <Dropdown popupId="mobilePopup" items={hidden} trigger="iconButton" isMobile />
              </Box>
            )}
            {!isEmpty(visible) && (
              <Box component="div" className={actionsClasses}>
                {renderItems(visible)}
              </Box>
            )}
          </Box>
        ) : null}
      </Toolbar>
    </AppBar>
  ) : null;
};

ActionBar.propTypes = {
  data: PropTypes.object.isRequired,
  isPage: PropTypes.bool
};

export default ActionBar;
