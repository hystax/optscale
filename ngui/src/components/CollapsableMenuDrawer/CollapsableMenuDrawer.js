import React, { useState } from "react";
import ArrowForwardIosOutlinedIcon from "@mui/icons-material/ArrowForwardIosOutlined";
import Drawer from "@mui/material/Drawer";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import IconButton from "components/IconButton";
import Tooltip from "components/Tooltip";
import { useMainMenuState } from "hooks/useMainMenuState";
import useStyles from "./CollapsableMenuDrawer.styles";

const CollapsableMenuDrawer = ({ children }) => {
  const { isExpanded, updateIsExpanded } = useMainMenuState();

  const [isMouseOverBorder, setIsMouseOverBorder] = useState(false);
  const [showDueToMouseOver, setShowDueToMouseOver] = useState(false);

  const showButton = isMouseOverBorder || showDueToMouseOver || !isExpanded;
  const hidden = !isExpanded && !showDueToMouseOver;

  const { classes, cx } = useStyles({ buttonOpacity: showButton ? 1 : 0, isExpanded });

  return (
    <div
      className={cx(classes.wrapper, isExpanded ? classes.wrapperExpanded : "")}
      onMouseMove={() => setShowDueToMouseOver(true)}
      onMouseLeave={() => setShowDueToMouseOver(false)}
    >
      <Drawer
        variant="permanent"
        className={cx(classes.menu, hidden ? classes.hiddenMenu : undefined)}
        classes={{
          paper: cx(classes.drawerPaper, hidden ? classes.drawerPaperHidden : undefined)
        }}
        open
      >
        {children}
      </Drawer>
      <div
        onClick={() => {
          // to hide menu instantly after click — dropping "mouseOver" cause
          setShowDueToMouseOver(false);
          updateIsExpanded(!isExpanded);
        }}
        onMouseEnter={() => setIsMouseOverBorder(true)}
        onMouseLeave={() => setIsMouseOverBorder(false)}
        className={classes.menuCollapseBorder}
      >
        <div
          className={classes.invisibleButtonBack}
          onMouseMove={(e) => {
            e.stopPropagation();
            e.preventDefault();
          }}
        >
          <Tooltip title={<FormattedMessage id={isExpanded ? "collapse" : "expand"} />} placement="right">
            <IconButton
              icon={<ArrowForwardIosOutlinedIcon color="inherit" className={classes.buttonIcon} />}
              customClass={classes.button}
            />
          </Tooltip>
        </div>
      </div>
    </div>
  );
};

CollapsableMenuDrawer.propTypes = {
  children: PropTypes.node
};

export default CollapsableMenuDrawer;
