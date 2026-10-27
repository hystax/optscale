import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import MuiAccordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
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
  disableShadows = false,
  enabledBorder = false,
  expandTitleColor,
  alwaysHighlightTitle = false,
  ...rest
}) => {
  const { classes, cx } = useStyles({
    expandTitleColor,
    alwaysHighlightTitle,
  });

  return (
    <MuiAccordion
      TransitionProps={{ unmountOnExit: true }}
      {...rest}
      className={cx(disableExpandedSpacing ? classes.disableExpandedSpacing : "", disableShadows ? classes.disableShadows : "")}
    >
      <AccordionSummary
        data-test-id={headerDataTestId}
        expandIcon={hideExpandIcon ? null : <ExpandMoreIcon />}
        className={cx(
          classes.summary,
          zeroSummaryMinHeight ? classes.zeroSummaryMinHeight : "",
          inheritFlexDirection ? classes.inheritFlexDirection : "",
          hideExpandIcon ? "" : classes.summaryPadding,
          enabledBorder ? classes.enableBorder : "",
          classes.expandTitleColor
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

export default Accordion;
