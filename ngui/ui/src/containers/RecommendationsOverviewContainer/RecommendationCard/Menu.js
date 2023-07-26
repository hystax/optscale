import React from "react";
import { MenuItem } from "@mui/material";
import PropTypes from "prop-types";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import IconButton from "components/IconButton";
import Popover from "components/Popover";
import Tooltip from "components/Tooltip";

const Menu = ({ items, Icon, tooltipMessage, disabled, isLoading }) => (
  <Popover
    renderMenu={({ closeHandler }) =>
      items.map(({ key, isItemLoading, body, onClick }, i) => (
        <ContentBackdropLoader isLoading={isItemLoading} key={key} size={15}>
          <MenuItem
            key={key}
            tabIndex={i + 1}
            onClick={() => {
              onClick();
              closeHandler();
            }}
          >
            {body}
          </MenuItem>
        </ContentBackdropLoader>
      ))
    }
    disabled={disabled}
    label={
      <Tooltip title={isLoading ? undefined : tooltipMessage}>
        <span>
          <IconButton icon={<Icon />} disabled={disabled} isLoading={isLoading} />
        </span>
      </Tooltip>
    }
  />
);

Menu.propTypes = {
  items: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      body: PropTypes.node.isRequired,
      onClick: PropTypes.func.isRequired,
      isLoading: PropTypes.bool
    })
  ),
  Icon: PropTypes.elementType.isRequired,
  tooltipMessage: PropTypes.node,
  disabled: PropTypes.bool,
  isLoading: PropTypes.bool
};

export default Menu;
