import React, { useRef } from "react";
import NavigationIcon from "@mui/icons-material/Navigation";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { useBoundingClientRect } from "hooks/useBoundingClientRect";
import { SPACING_1 } from "utils/layouts";
import useStyles from "./Tooltip.styles";
import usePosition from "./usePosition";

const renderLabelWithCounters = (label, stepIndex, size) => `${label} (${stepIndex + 1}/${size})`;

const getAngle = (tooltipNode, targetCoords) => {
  if (!tooltipNode) {
    return 0;
  }

  const tooltipRect = tooltipNode.getBoundingClientRect();
  const targetCenter = { left: targetCoords.left + targetCoords.width / 2, top: targetCoords.top + targetCoords.height / 2 };
  const tooltipCenter = { left: tooltipRect.left + tooltipRect.width / 2, top: tooltipRect.top + tooltipRect.height / 2 };

  // atan2 is the angle measure (in radians) between the positive x-axis and the ray from the origin to the point (x,y) in the Cartesian plane
  // more: https://en.wikipedia.org/wiki/Atan2
  return Math.atan2(tooltipCenter.top - targetCenter.top, tooltipCenter.left - targetCenter.left) - Math.PI / 2;
};

const Tooltip = ({ coords, onBack, onNext, onSkip, stepIndex, size, stepContent: { content, dataTestId } }) => {
  const { classes, cx } = useStyles();
  const intl = useIntl();

  const [tooltipContentRect, tooltipContentRef, tooltipDomNode] = useBoundingClientRect();
  const iconRef = useRef(null);
  const scrollHelpHeight = iconRef.current?.getBoundingClientRect().height ?? 30;

  const {
    result: { top, left },
    isTargetOffscreen
  } = usePosition(coords, tooltipContentRect, scrollHelpHeight);

  const angle = getAngle(tooltipDomNode, coords);

  const scrollHelpClasses = cx(classes.arrowContainer, isTargetOffscreen ? classes.visible : classes.hidden);

  const isLastStep = stepIndex + 1 === size;
  return (
    <Box className={classes.root} sx={{ top: `${top}px`, left: `${left}px` }}>
      <Card ref={tooltipContentRef} sx={{ position: "relative" }} elevation={6}>
        <CardContent data-test-id={dataTestId}>
          <Typography>{content}</Typography>
        </CardContent>
        <CardActions>
          {/* title="" to remove default html tooltips */}

          <Button
            onClick={onSkip}
            dataTestId="btn_skip_tour"
            title=""
            messageId="skipTour"
            variant="text"
            customClass={classes.skipButton}
          />
          {stepIndex > 0 && (
            <Button
              onClick={onBack}
              dataTestId="btn_back"
              title=""
              messageId="back"
              variant="text"
              customClass={classes.backButton}
            />
          )}
          <Button
            onClick={onNext}
            title=""
            text={renderLabelWithCounters(intl.formatMessage({ id: isLastStep ? "finishTour" : "next" }), stepIndex, size)}
            variant="outlined"
            dataTestId={isLastStep ? "btn_finish" : "btn_next"}
            customClass={classes.nextButton}
          />
        </CardActions>
      </Card>
      <Box className={scrollHelpClasses}>
        <Typography color={"white"} marginRight={SPACING_1}>
          <FormattedMessage id="scrollToTheTarget" />
        </Typography>
        <Box>
          <NavigationIcon ref={iconRef} className={classes.arrow} sx={{ rotate: `${angle}rad` }} />
        </Box>
      </Box>
    </Box>
  );
};

Tooltip.propTypes = {
  onBack: PropTypes.func.isRequired,
  onNext: PropTypes.func.isRequired,
  onSkip: PropTypes.func.isRequired,

  stepIndex: PropTypes.number.isRequired,

  size: PropTypes.number.isRequired,
  stepContent: PropTypes.shape({
    content: PropTypes.node,
    dataTestId: PropTypes.string
  }).isRequired,
  coords: PropTypes.shape({
    top: PropTypes.number,
    left: PropTypes.number,
    width: PropTypes.number,
    height: PropTypes.number
  })
};

export default Tooltip;
