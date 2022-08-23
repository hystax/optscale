import React from "react";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { useIntl } from "react-intl";
import Button from "components/Button";
import useStyles from "./Tooltip.styles";

const renderLabelWithCounters = (label, index, size) => `${label} (${index + 1}/${size})`;

const Tooltip = ({ backProps, primaryProps, skipProps, tooltipProps, continuous, index, isLastStep, size, step }) => {
  const { classes } = useStyles();
  const intl = useIntl();

  const { content, showSkipButton, dataTestId } = step;

  return (
    <Card data-test-id="step_tour" {...tooltipProps} className={classes.root}>
      <CardContent data-test-id={dataTestId}>
        <Typography>{content}</Typography>
      </CardContent>
      <CardActions>
        {/* title="" to remove default html tooltips */}
        {showSkipButton && (
          <Button
            {...skipProps}
            dataTestId="btn_skip_tour"
            title=""
            messageId="skipTour"
            variant="text"
            customClass={classes.skipButton}
          />
        )}
        {index > 0 && (
          <Button
            {...backProps}
            dataTestId="btn_back"
            title=""
            messageId="back"
            variant="text"
            customClass={classes.backButton}
          />
        )}
        {continuous && (
          <Button
            {...primaryProps}
            title=""
            text={renderLabelWithCounters(intl.formatMessage({ id: isLastStep ? "finishTour" : "next" }), index, size)}
            variant="outlined"
            dataTestId={isLastStep ? "btn_finish" : "btn_next"}
            customClass={classes.nextButton}
          />
        )}
      </CardActions>
    </Card>
  );
};

Tooltip.propTypes = {
  backProps: PropTypes.object.isRequired,
  primaryProps: PropTypes.object.isRequired,
  skipProps: PropTypes.object.isRequired,
  tooltipProps: PropTypes.object.isRequired,
  continuous: PropTypes.bool.isRequired,
  index: PropTypes.number.isRequired,
  isLastStep: PropTypes.bool.isRequired,
  size: PropTypes.number.isRequired,
  step: PropTypes.object.isRequired
};

export default Tooltip;
