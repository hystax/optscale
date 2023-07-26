import React, { useRef } from "react";
import Box from "@mui/material/Box";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import { useResizeObserver } from "hooks/useResizeObserver";

const MARKER_WIDTH = "1px";
const MARKER_STYLE = "dashed";

const CloudExpensesChartMarker = ({
  value,
  valueMessageId,
  chartBorderWidth,
  chartSegmentHeight,
  chartBase,
  position = "bottom"
}) => {
  const theme = useTheme();
  const ref = useRef();
  const { width: markerWidth } = useResizeObserver(ref);

  const borderStyle = `${MARKER_WIDTH} ${MARKER_STYLE} ${theme.palette.info.dark}`;
  const textSpacing = theme.spacing(0.5);
  const markerVerticalShift = `${chartBorderWidth} + ${chartSegmentHeight}`;

  const leftShift = (value / chartBase) * 100 || 0;

  const isRightSideMarker = leftShift < 50;

  const positionStyles = {
    top: {
      bottom: `calc(${markerVerticalShift})`
    },
    bottom: {
      alignItems: "flex-end",
      top: `calc(${markerVerticalShift})`
    }
  };

  return (
    <Box
      ref={ref}
      style={{
        position: "absolute",
        display: "flex",
        width: "max-content",
        ...positionStyles[position],
        // move dashed line to the start/end of marker
        justifyContent: isRightSideMarker ? "flex-start" : "flex-end",
        ...(isRightSideMarker
          ? {
              left: `${leftShift}%`
            }
          : {
              left: `calc(${leftShift}% - ${markerWidth}px)`
            })
      }}
    >
      <Box
        style={{
          position: "absolute",
          borderRight: borderStyle,
          height: `calc(100% + ${markerVerticalShift})`
        }}
      />
      <KeyValueLabel
        style={
          isRightSideMarker
            ? {
                paddingLeft: textSpacing
              }
            : {
                paddingRight: textSpacing
              }
        }
        messageId={valueMessageId}
        value={<FormattedMoney value={value} />}
      />
    </Box>
  );
};

CloudExpensesChartMarker.propTypes = {
  value: PropTypes.number.isRequired,
  valueMessageId: PropTypes.string.isRequired,
  chartBase: PropTypes.number.isRequired,
  chartBorderWidth: PropTypes.string.isRequired,
  chartSegmentHeight: PropTypes.string.isRequired,
  position: PropTypes.oneOf(["top", "bottom"])
};

export default CloudExpensesChartMarker;
