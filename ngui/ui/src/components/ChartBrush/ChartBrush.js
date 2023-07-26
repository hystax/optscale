import React, { forwardRef, useMemo, useRef } from "react";
import { useTheme } from "@mui/material/styles";
import { Brush } from "@visx/brush";
import { Group } from "@visx/group";
import { scaleLinear, scalePoint, scaleTime } from "d3-scale";
import PropTypes from "prop-types";
import { useResizeObserver } from "hooks/useResizeObserver";
import { getThemeSpacingCoefficient } from "theme";
import { DEFAULT_BAR_CHART_MARGIN } from "utils/constants";
import useStyles from "./ChartBrush.styles";

// Handle code source: https://airbnb.io/visx/brush
const HANDLE_PATH_WIDTH = 8;
const HANDLE_PATH_HEIGHT = 15;
const BrushHandle = ({ x, height, isBrushActive }) => {
  const theme = useTheme();
  if (!isBrushActive) {
    return null;
  }
  return (
    <Group left={x + HANDLE_PATH_WIDTH / 2} top={(height - HANDLE_PATH_HEIGHT) / 2}>
      <path
        fill={theme.palette.common.white}
        d="M -4.5 0.5 L 3.5 0.5 L 3.5 15.5 L -4.5 15.5 L -4.5 0.5 M -1.5 4 L -1.5 12 M 0.5 4 L 0.5 12"
        stroke={theme.palette.info.main}
        strokeWidth="1"
        style={{ cursor: "ew-resize" }}
      />
    </Group>
  );
};

const getScaleFn = (scaleType) =>
  ({
    time: scaleTime,
    linear: scaleLinear,
    point: scalePoint
  }[scaleType]);

const ChartBrush = forwardRef(
  (
    {
      content,
      xRange = [0, 0],
      onChange,
      height: heightProperty = 12,
      marginLeft: marginLeftInPixels = DEFAULT_BAR_CHART_MARGIN.left,
      marginRight: marginRightInPixels = DEFAULT_BAR_CHART_MARGIN.right,
      isLoading,
      xScaleType = "time"
    },
    brushRef
  ) => {
    const theme = useTheme();

    const wrapRef = useRef(null);
    const { width: wrapperWidthInPixels } = useResizeObserver(wrapRef);

    const heightInPx = heightProperty * getThemeSpacingCoefficient(theme);

    const { classes } = useStyles({ wrapperHeight: heightProperty });

    // Adjust Brush working area width with the area where the chart elements are rendered (bands, lines, etc)
    // Note: width is been used in some calculations as divider, so glitches will appear on 0 or negative value
    const brushWidthInPx = wrapperWidthInPixels ? wrapperWidthInPixels - marginLeftInPixels - marginRightInPixels : 1;

    const xScale = useMemo(
      () => getScaleFn(xScaleType)().domain(xRange).range([0, brushWidthInPx]),
      [brushWidthInPx, xRange, xScaleType]
    );
    const yScale = useMemo(() => scaleLinear().domain([0, 0]).range([0, heightInPx]), [heightInPx]);

    const onBrushChange = (domain) => {
      if (!domain) return;

      onChange(domain);
    };

    const onClick = () => onChange(null);

    const innerBrushRef = (brushInstance) => {
      /**
       * Check that brushRef is passed to a component
       *   <Component />                            => ref = null
       *   <Component ref={useRef(defaultValue)} /> => ref = { current: defaultValue }
       */
      if (brushRef !== null) {
        if (brushInstance !== null) {
          // eslint-disable-next-line no-param-reassign
          brushRef.current = {
            resetTo: (xValue0, xValue1 = xValue0) => {
              const [xMinValue, xMaxValue] = xRange;

              const updater = (prevBrush) => {
                const newX0Coordinate = xScale(Math.max(xValue0, xMinValue));
                const newX1Coordinate = xScale(Math.min(xValue1, xMaxValue));

                const newExtent = brushInstance.getExtent({ x: newX0Coordinate }, { x: newX1Coordinate });

                return {
                  ...prevBrush,
                  start: { x: newExtent.x0, y: newExtent.y0 },
                  end: { x: newExtent.x1, y: newExtent.y1 },
                  extent: newExtent
                };
              };

              brushInstance.updateBrush(updater);
            },
            brush: brushInstance
          };
        } else {
          // eslint-disable-next-line no-param-reassign
          brushRef.current = null;
        }
      }
    };

    return (
      <div className={classes.wrapper} ref={wrapRef}>
        <div className={classes.contentWrapper}>{content}</div>
        <svg
          className={classes.brushSvg}
          style={{
            width: brushWidthInPx,
            height: heightInPx,
            // Emulate spacings that @nivo adds when you provide margin.left and margin.right properties
            marginLeft: marginLeftInPixels,
            marginRight: marginRightInPixels
          }}
        >
          {!isLoading && (
            <Brush
              xScale={xScale}
              yScale={yScale}
              width={brushWidthInPx}
              height={heightInPx}
              handleSize={8}
              innerRef={innerBrushRef}
              brushDirection="horizontal"
              onChange={onBrushChange}
              onClick={onClick}
              useWindowMoveEvents
              renderBrushHandle={(props) => <BrushHandle {...props} />}
            />
          )}
        </svg>
      </div>
    );
  }
);

ChartBrush.propTypes = {
  content: PropTypes.node,
  xRange: PropTypes.any,
  xScaleType: PropTypes.oneOf(["time", "linear"]),
  onChange: PropTypes.func,
  height: PropTypes.number,
  isLoading: PropTypes.bool,
  brushRef: PropTypes.object,
  marginLeft: PropTypes.number,
  marginRight: PropTypes.number
};

export default ChartBrush;
