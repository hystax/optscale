import React from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Accordion, AccordionDetails, AccordionSummary, Box } from "@mui/material";
import PropTypes from "prop-types";
import useMenuItemState from "hooks/useMenuItemState";
import useStyles from "./MenuGroupWrapper.styles";

// TODO: there is a refactoring proposition https://gitlab.com/hystax/ngui/-/merge_requests/2936#note_1123674985
const MenuGroupWrapper = ({ menuSectionTitle, menuSectionBadge, children, id, keepExpanded = false }) => {
  const { classes } = useStyles();
  const { isExpanded, updateIsExpanded } = useMenuItemState(id);

  if (!menuSectionTitle) {
    return children;
  }

  return (
    <Accordion
      expanded={keepExpanded || isExpanded}
      className={classes.menu}
      disableGutters
      elevation={0}
      square
      onChange={(_, expanded) => !keepExpanded && updateIsExpanded(expanded)}
    >
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          height: "32px"
        }}
      >
        <AccordionSummary sx={{ paddingRight: "0px" }} expandIcon={<ArrowDropDownIcon fontSize="small" />}>
          {menuSectionTitle}
        </AccordionSummary>
        {menuSectionBadge}
      </Box>
      <AccordionDetails>{children}</AccordionDetails>
    </Accordion>
  );
};

MenuGroupWrapper.propTypes = {
  children: PropTypes.node.isRequired,
  menuSectionTitle: PropTypes.node,
  menuSectionBadge: PropTypes.node,
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  keepExpanded: PropTypes.bool
};

export default MenuGroupWrapper;
