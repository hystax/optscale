import React from "react";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import Joyride, { LIFECYCLE, STATUS } from "react-joyride";
import { useDispatch } from "react-redux";
import { useRootData } from "hooks/useRootData";
import { finishTour } from "./actionCreators";
import { TOURS } from "./reducer";
import Tooltip from "./Tooltip";

const ProductTour = ({ steps, label }) => {
  const theme = useTheme();
  const dispatch = useDispatch();

  const { rootData: { [label]: { isOpen } = {} } = {} } = useRootData(TOURS);

  const callback = (data) => {
    const { status, lifecycle } = data;

    if ([STATUS.SKIPPED, STATUS.FINISHED].includes(status)) {
      if (lifecycle === LIFECYCLE.COMPLETE) {
        dispatch(finishTour(label));
      }
    }
  };

  return (
    <Joyride
      run={isOpen}
      continuous
      scrollToFirstStep
      showSkipButton
      floaterProps={{
        disableAnimation: true,
        disableFlip: true
      }}
      callback={callback}
      tooltipComponent={Tooltip}
      disableScrollParentFix
      disableOverlayClose
      disableCloseOnEsc
      steps={steps}
      styles={{
        options: {
          zIndex: theme.zIndex.drawer + 1
        }
      }}
      spotlightPadding={0}
    />
  );
};

ProductTour.propTypes = {
  steps: PropTypes.array.isRequired,
  label: PropTypes.string.isRequired
};

export default ProductTour;
