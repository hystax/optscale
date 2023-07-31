import React, { useCallback } from "react";
import PropTypes from "prop-types";
import Tooltip from "components/Tooltip";
import { findMaxNumber, findMinNumber } from "utils/arrays";
import { getScaledCanvasContext, renderCanvasLine } from "utils/charts";
import { normalize, percentXofY } from "utils/math";

/**
 * Returns a function that scales a value from a specified domain to a specified range.
 *
 * @param {Object} options - An options object.
 * @param {Array<number>} options.domain - The domain to scale from represented as an array with two numbers, where the first number is the minimum value and the second number is the maximum value.
 * @param {number} options.range - The range to scale to represented as a number.
 * @returns {Function} A function that scales a value from the specified domain to the specified range.
 */
const getScale = ({ domain, range }) => {
  const [min, max] = domain;
  const delta = max - min;

  return (value) => {
    if (delta === 0) {
      return range / 2;
    }
    return normalize(value, [min, max], [0, range]);
  };
};

const getGradient = (
  ctx,
  { thresholdArea, maxValue, minValue, thresholdStart, thresholdEnd, endThresholdColor, startThresholdColor, lineAreaRectangle }
) => {
  const { start: thresholdAreaStart, end: thresholdAreaEnd } = thresholdArea;

  const isHorizontalLine = minValue === maxValue;
  const isThresholdAbove = thresholdAreaStart >= maxValue && thresholdAreaEnd >= maxValue;
  const isThresholdBelow = thresholdAreaStart <= minValue && thresholdAreaEnd <= minValue;
  const isSharpGradient = thresholdAreaStart === thresholdAreaEnd;

  // One color cases
  if (isThresholdAbove || isThresholdBelow || (isSharpGradient && isHorizontalLine)) {
    const solidColor = ctx.createLinearGradient(0, 0, 0, lineAreaRectangle.yEnd);
    solidColor.addColorStop(0, isThresholdBelow ? endThresholdColor : startThresholdColor);
    return solidColor;
  }

  // Two color case with sharp gradient (from one color to another without smooth transition)
  if (isSharpGradient) {
    const gradient = ctx.createLinearGradient(0, 0, 0, lineAreaRectangle.yEnd);
    const stop = percentXofY(thresholdStart, lineAreaRectangle.yEnd);
    gradient.addColorStop(stop, endThresholdColor);
    gradient.addColorStop(stop, startThresholdColor);
    return gradient;
  }

  // Two colors with smooth gradient
  const gradient = ctx.createLinearGradient(
    0,
    Math.min(thresholdStart, thresholdEnd) + (isHorizontalLine ? 1 : 0),
    0,
    Math.max(thresholdStart, thresholdEnd, 1) - (isHorizontalLine ? 1 : 0)
  );
  gradient.addColorStop(0, endThresholdColor);
  gradient.addColorStop(1, startThresholdColor);
  return gradient;
};

export const DEFAULT_COLORS = Object.freeze({
  START_THRESHOLD: "#00BE41",
  END_THRESHOLD: "#FF0000"
});

const DOT_RADIUS = 3;

const MARGIN = Object.freeze({
  LEFT: DOT_RADIUS + 1,
  TOP: DOT_RADIUS + 1,
  BOTTOM: DOT_RADIUS + 1,
  RIGHT: DOT_RADIUS + 1
});

const HeartLineChart = ({ values, width, height, thresholdArea, thresholdColors = {}, tooltip, debug = false }) => {
  const { start: startThresholdColor = DEFAULT_COLORS.START_THRESHOLD, end: endThresholdColor = DEFAULT_COLORS.END_THRESHOLD } =
    thresholdColors;

  const draw = useCallback(
    (ctx) => {
      const innerHeight = height - MARGIN.TOP - MARGIN.BOTTOM;
      const innerWidth = width - MARGIN.LEFT - MARGIN.RIGHT;

      const maxValue = findMaxNumber(values);
      const minValue = findMinNumber(values);

      const yScale = getScale({
        domain: [maxValue, minValue],
        range: innerHeight
      });

      const xScale = getScale({
        domain: [0, values.length - 1],
        range: innerWidth
      });

      const points = values.map((value, index) => ({
        x: xScale(index),
        y: yScale(value)
      }));

      const thresholdStart = yScale(thresholdArea.start);
      const thresholdEnd = yScale(thresholdArea.end);

      ctx.translate(MARGIN.LEFT, MARGIN.TOP);

      const lineAreaRectangle = {
        xStart: 0,
        yStart: 0,
        xEnd: innerWidth,
        yEnd: innerHeight
      };

      const gradient = getGradient(ctx, {
        thresholdArea,
        minValue,
        maxValue,
        thresholdStart,
        thresholdEnd,
        startThresholdColor,
        endThresholdColor,
        lineAreaRectangle
      });

      ctx.strokeStyle = gradient;
      ctx.fillStyle = gradient;
      ctx.lineWidth = 2;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";

      renderCanvasLine(ctx, {
        points,
        originRelativeToCanvas: {
          x: MARGIN.LEFT,
          y: MARGIN.TOP
        },
        strokeStyle: gradient,
        fillStyle: gradient,
        dotRadius: DOT_RADIUS
      });

      if (debug) {
        ctx.save();
        ctx.strokeStyle = "black";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.rect(lineAreaRectangle.xStart, lineAreaRectangle.yStart, lineAreaRectangle.xEnd, lineAreaRectangle.yEnd);
        ctx.stroke();

        ctx.beginPath();
        ctx.strokeStyle = startThresholdColor;
        ctx.moveTo(lineAreaRectangle.xStart, thresholdStart);
        ctx.lineTo(lineAreaRectangle.xEnd, thresholdStart);
        ctx.stroke();

        ctx.beginPath();
        ctx.strokeStyle = endThresholdColor;
        ctx.moveTo(lineAreaRectangle.xStart, thresholdEnd);
        ctx.lineTo(lineAreaRectangle.xEnd, thresholdEnd);
        ctx.stroke();

        ctx.restore();
      }

      return () => ctx.clearRect(0, 0, width, height);
    },
    [debug, endThresholdColor, height, startThresholdColor, thresholdArea, values, width]
  );

  const measuredRef = useCallback(
    (canvas) => {
      if (canvas !== null && values.length !== 0) {
        const ctx = getScaledCanvasContext(canvas, { width, height });
        draw(ctx);
      }
    },
    [draw, height, values.length, width]
  );

  return (
    <>
      <Tooltip title={tooltip}>
        <canvas width={width} height={height} ref={measuredRef} />
      </Tooltip>
    </>
  );
};

HeartLineChart.propTypes = {
  values: PropTypes.array.isRequired,
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  thresholdArea: PropTypes.shape({
    start: PropTypes.number.isRequired,
    end: PropTypes.number.isRequired
  }).isRequired,
  thresholdColors: PropTypes.shape({
    start: PropTypes.string,
    end: PropTypes.string
  }),
  tooltip: PropTypes.node,
  debug: PropTypes.bool
};

export default HeartLineChart;
