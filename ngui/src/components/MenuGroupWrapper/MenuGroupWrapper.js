import React from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Accordion, AccordionDetails, AccordionSummary } from "@mui/material";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import ListItemTextDivider from "components/ListItemTextDivider";
import { COLLAPSED_MENU_ITEMS } from "components/MenuGroupWrapper/reducer";
import { useRootData } from "hooks/useRootData";
import { updateCollapsedMenuItems } from "./actionCreators";
import useStyles from "./MenuGroupWrapper.styles";

const MainMenuGroupWrapper = ({ sectionTitleMessageId, showSection = true, children, id }) => {
  const { classes } = useStyles();
  const dispatch = useDispatch();

  const { rootData: collapsedItems = [] } = useRootData(COLLAPSED_MENU_ITEMS);

  const persistedIsCollapsed = collapsedItems.includes(id);

  const onAccordionChange = (_, expanded) => {
    let updatedItemsList;
    if (expanded) {
      updatedItemsList = collapsedItems.filter((itemId) => itemId !== id);
    } else {
      updatedItemsList = [...collapsedItems, id];
    }
    dispatch(updateCollapsedMenuItems(updatedItemsList));
  };

  if (!showSection) {
    return null;
  }

  if (!sectionTitleMessageId) {
    return children;
  }

  return (
    <Accordion
      expanded={!persistedIsCollapsed}
      className={classes.menu}
      disableGutters
      elevation={0}
      square
      onChange={onAccordionChange}
    >
      <AccordionSummary expandIcon={<ArrowDropDownIcon fontSize="small" />}>
        <ListItemTextDivider messageId={sectionTitleMessageId} />
      </AccordionSummary>
      <AccordionDetails>{children}</AccordionDetails>
    </Accordion>
  );
};

MainMenuGroupWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  sectionTitleMessageId: PropTypes.string,
  showSection: PropTypes.bool,
  id: PropTypes.string.isRequired
};

export default MainMenuGroupWrapper;
