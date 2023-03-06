import React, { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import Tooltip from "../Tooltip";
import useStyles from "./TourUi.styles";

const TOUR_UI = "tourUi";

const getTourTargetElement = (target) => document.querySelector(`[data-product-tour-id='${target}']`);

const TourUi = ({ steps, close }) => {
  const { classes } = useStyles();

  const [currentStep, setCurrentStep] = useState(0);
  const [coords, setCoords] = useState({ top: 0, left: 0, width: 0, height: 0, isSet: false });

  // buttons onClick handlers
  const onSkip = useCallback(() => {
    setCoords((prev) => ({ ...prev, isSet: false }));
    close();
  }, [close]);

  const doStep = useCallback(
    (diff) => {
      // find next step:
      let nextStep;
      let isStepFound = false;

      for (let i = currentStep + diff; i < steps.length && i > -1; i += diff) {
        const { target, missable } = steps[i];
        const isThereTargetElement = !!getTourTargetElement(target);
        isStepFound = isThereTargetElement || !missable;

        if (isStepFound) {
          nextStep = i;
          break;
        }
      }

      if (!isStepFound) {
        onSkip();
      } else {
        setCurrentStep(nextStep);
      }
    },
    [currentStep, onSkip, steps]
  );

  const onNext = useCallback(() => {
    doStep(1);
  }, [doStep]);

  const onBack = useCallback(() => {
    doStep(-1);
  }, [doStep]);

  // step content and target element
  const { target, content, dataTestId } = steps[currentStep] ?? {};

  // set target element bounding client rectangle
  const updateTargetElementPosition = useCallback(() => {
    const targetElement = getTourTargetElement(target);

    if (targetElement) {
      const { top, left, width, height } = targetElement.getBoundingClientRect();
      if (top !== coords.top || left !== coords.left || width !== coords.width || height !== coords.height) {
        setCoords({ top, left, width, height, isSet: true });
      }
    }
  }, [coords.top, coords.left, coords.width, coords.height, target]);

  // update coordinates of target element 24 frames per second
  useEffect(() => {
    updateTargetElementPosition();
    const positionChecker = setInterval(updateTargetElementPosition, 1000 / 24);

    return () => clearInterval(positionChecker);
  }, [updateTargetElementPosition]);

  // preventing clicks / tooltips / etc...
  useEffect(() => {
    const events = ["click", "mousedown", "mouseup", "touchstart", "touchend", "mouseover"];

    const stopper = (e) => {
      const isTourUiEvent = document.getElementById(TOUR_UI)?.contains(e.target);
      if (!isTourUiEvent && getTourTargetElement(target)) {
        e.preventDefault();
        e.stopImmediatePropagation();
        return false;
      }

      return true;
    };

    events.forEach((eventName) => window.document.addEventListener(eventName, stopper, { capture: true }));
    return () => {
      events.forEach((eventName) => window.document.removeEventListener(eventName, stopper, { capture: true }));
    };
  }, [target]);

  // do not show tour before target element bounding rectangle is calculated
  if (!coords.isSet) {
    return null;
  }

  return (
    <>
      <div
        className={classes.mask}
        style={{
          top: `${coords.top}px`,
          left: `${coords.left}px`,
          width: `${coords.width}px`,
          height: `${coords.height}px`
        }}
      />
      <div id={TOUR_UI}>
        <Tooltip
          coords={coords}
          onBack={onBack}
          onNext={onNext}
          onSkip={onSkip}
          stepIndex={currentStep}
          size={steps.length}
          stepContent={{ content, dataTestId }}
        />
      </div>
    </>
  );
};

TourUi.propTypes = {
  steps: PropTypes.array,
  close: PropTypes.func
};

export default TourUi;
