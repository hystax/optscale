import React from "react";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import MuiAccordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import PropTypes from "prop-types";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import useStyles from "./Accordion.styles";

const Accordion = ({
  children: [summary, ...details],
  disableExpandedSpacing = false,
  zeroSummaryMinHeight = false,
  hideExpandIcon = false,
  inheritFlexDirection = false,
  actions = null,
  headerDataTestId,
  ...rest
}) => {
  const { classes, cx } = useStyles();

  return (
    <MuiAccordion
      TransitionProps={{ unmountOnExit: true }}
      {...rest}
      className={disableExpandedSpacing ? classes.disableExpandedSpacing : ""}
    >
      <AccordionSummary
        data-test-id={headerDataTestId}
        expandIcon={hideExpandIcon ? null : <ExpandMoreIcon />}
        className={cx(
          classes.summary,
          zeroSummaryMinHeight ? classes.zeroSummaryMinHeight : "",
          inheritFlexDirection ? classes.inheritFlexDirection : "",
          hideExpandIcon ? "" : classes.summaryPadding
        )}
      >
        {summary}
      </AccordionSummary>
      <AccordionDetails className={classes.details}>
        {details}
        {actions && <FormButtonsWrapper>{actions}</FormButtonsWrapper>}
      </AccordionDetails>
    </MuiAccordion>
  );
};

Accordion.propTypes = {
  children: PropTypes.node.isRequired,
  disableExpandedSpacing: PropTypes.bool,
  zeroSummaryMinHeight: PropTypes.bool,
  hideExpandIcon: PropTypes.bool,
  inheritFlexDirection: PropTypes.bool,
  headerDataTestId: PropTypes.string,
  actions: PropTypes.object,
  dataTestIds: PropTypes.shape({
    summary: PropTypes.string
  })
};

export default Accordion;
