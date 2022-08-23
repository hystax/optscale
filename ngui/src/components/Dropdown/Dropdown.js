import React from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowDropUpIcon from "@mui/icons-material/ArrowDropUp";
import MoreVertOutlinedIcon from "@mui/icons-material/MoreVertOutlined";
import Link from "@mui/material/Link";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { usePopupState as useDropDownState, bindTrigger, bindMenu } from "material-ui-popup-state/hooks";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { NavLink } from "react-router-dom";
import ButtonLoader from "components/ButtonLoader";
import IconButton from "components/IconButton";
import MenuItemLoader from "components/MenuItemLoader";
import Tooltip from "components/Tooltip";
import { isEmpty } from "utils/arrays";
import useStyles from "./Dropdown.styles";

const renderButtonTrigger = (dropDownState, { messageId, icon, dataTestId, tooltip, isLoading, disabled }) => {
  const trigger = bindTrigger(dropDownState);
  return (
    <ButtonLoader
      dataTestId={dataTestId}
      messageId={messageId}
      variant="text"
      startIcon={icon}
      disabled={disabled}
      tooltip={tooltip}
      endIcon={dropDownState.isOpen ? <ArrowDropUpIcon /> : <ArrowDropDownIcon />}
      isLoading={isLoading}
      {...trigger}
    />
  );
};

const renderIconButtonTrigger = (dropDownState, { dataTestId, tooltip }) => (
  <IconButton dataTestId={dataTestId} tooltip={tooltip} icon={<MoreVertOutlinedIcon />} {...bindTrigger(dropDownState)} />
);

const renderDropDownItem = (item, dropDownState, classes) => {
  const { show = true } = item;

  // TODO: NGUI-1509. Need to bring the solution to one type(MenuItem, Button, Dropdown).
  const renderNavLink = () => {
    if (item.disabled) {
      return (
        <MenuItem key={item.key} disabled={item.disabled} style={item.disabled ? { pointerEvents: "all" } : {}}>
          {item.node}
        </MenuItem>
      );
    }

    const renderClickableMenuItem = <MenuItem onClick={dropDownState.close}>{item.node}</MenuItem>;

    if (item.link) {
      return (
        <NavLink key={item.key} to={item.link} className={classes.link}>
          {renderClickableMenuItem}
        </NavLink>
      );
    }
    return (
      <Link key={item.key} href={item.href} className={classes.link} target="_blank" rel="noopener" download={item.download}>
        {renderClickableMenuItem}
      </Link>
    );
  };

  // { pointerEvents: "all" } - This is a workaround for adding a tooltip, since we can't wrap this element in span,
  // because then the list structure changes (ul -> li) and the event works on the menu instead of the menu item.
  const renderMenuItem = () =>
    item.link || item.href ? (
      renderNavLink()
    ) : (
      <MenuItem
        key={item.key}
        data-test-id={item.dataTestId}
        disabled={item.disabled}
        style={item.disabled ? { pointerEvents: "all" } : {}}
        onClick={(event) => {
          if (!item.disabled) {
            if (typeof item.action === "function") {
              item.action(event, item.value);
            }
            dropDownState.close();
          }
        }}
      >
        {item.node}
      </MenuItem>
    );

  const renderItem = () => (show ? renderMenuItem() : null);

  return item.isLoading ? <MenuItemLoader key={item.key} messageId={item.messageId} text={item.text} /> : renderItem();
};

const getDropDownItemNode = ({ text, classes = "", tooltip = {} }) => {
  if (tooltip.show) {
    return (
      <Tooltip
        title={tooltip.body || tooltip.value || <FormattedMessage id={tooltip.messageId} />}
        placement={tooltip.placement}
      >
        <span className={classes}>{text}</span>
      </Tooltip>
    );
  }
  return <span className={classes}>{text}</span>;
};

const Dropdown = ({
  items,
  trigger,
  messageId,
  icon,
  popupId,
  isMobile,
  dataTestId,
  tooltip,
  isLoading = false,
  disabled = false
}) => {
  const { classes, cx } = useStyles();

  const getTriggerTemplate = ({ type, dropDownState }) => {
    const renderTrigger = {
      button: renderButtonTrigger,
      iconButton: renderIconButtonTrigger
    }[type];

    return renderTrigger(dropDownState, {
      dataTestId,
      messageId,
      icon,
      tooltip,
      isLoading,
      disabled
    });
  };

  const renderDropDownItems = (menuItems, dropDownState) =>
    menuItems.map((item) =>
      renderDropDownItem(
        {
          ...item,
          node: getDropDownItemNode({
            classes: item.tooltip?.show ? classes.tooltipSpan : "",
            text: item.messageId ? <FormattedMessage id={item.messageId} /> : item.text,
            tooltip: item.tooltip
          })
        },
        dropDownState,
        classes
      )
    );

  const renderMobileDropDownItems = (mobileItems, dropDownState) =>
    mobileItems.map((item) => {
      const itemMessageId = item.mobileMessageId || item.messageId;
      const parentObject = {
        ...item,
        messageId: itemMessageId,
        node: getDropDownItemNode({
          classes: item.tooltip?.show ? classes.tooltipSpan : "",
          tooltip: item.tooltip,
          text: itemMessageId ? <FormattedMessage id={itemMessageId} /> : item.text
        })
      };
      return item.menu
        ? [
            {
              ...parentObject,
              disabled: true
            }
          ]
            .concat(
              item.menu.items.map((el) => {
                const elMessageId = el.mobileMessageId || el.messageId;
                return {
                  ...el,
                  messageId: elMessageId,
                  node: getDropDownItemNode({
                    classes: cx(el.tooltip?.show ? classes.tooltipSpan : "", classes.childItem),
                    tooltip: el.tooltip,
                    text: elMessageId ? <FormattedMessage id={elMessageId} /> : el.text
                  }),
                  disabled: item.isLoading
                };
              })
            )
            .map((el) => renderDropDownItem(el, dropDownState, classes))
        : renderDropDownItem(parentObject, dropDownState, classes);
    });

  const dropDownState = useDropDownState({ variant: "popover", popupId });

  return (
    <>
      {!isEmpty(items) &&
        getTriggerTemplate({
          type: trigger,
          dropDownState
        })}
      <Menu
        {...bindMenu(dropDownState)}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left"
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "left"
        }}
      >
        {isMobile ? renderMobileDropDownItems(items, dropDownState) : renderDropDownItems(items, dropDownState)}
      </Menu>
    </>
  );
};

Dropdown.propTypes = {
  items: PropTypes.array.isRequired,
  trigger: PropTypes.string.isRequired,
  popupId: PropTypes.string,
  icon: PropTypes.object,
  isMobile: PropTypes.bool,
  messageId: PropTypes.string,
  dataTestId: PropTypes.string,
  customClass: PropTypes.string,
  tooltip: PropTypes.object,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool
};

export default Dropdown;
