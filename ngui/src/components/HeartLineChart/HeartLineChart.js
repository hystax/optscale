import React, { useRef, useEffect, useCallback, useMemo, forwardRef } from "react";
import PropTypes from "prop-types";

/**
 * When plot is straight line (delta is 0) — place it at center(height/2) of canvas
 * If it's not — function will return
 *  1) normalized [0;1] // (value - min) / delta)
 *  2) to height [0;height] // * height
 *  3) reversed value [height;0] // height -
 *
 * @param {number} props.value Value to normalize
 * @param {number} props.min Minimum of all the values
 * @param {number} props.delta Difference between minimum and maximum values
 * @param {number} props.height Actual height of plot (without paddings)
 * @returns normalized to height reversed value
 */
const getNormalValue = ({ value, min, delta, height }) => (delta === 0 ? height / 2 : (1 - (value - min) / delta) * height);

const getNormalizedDots = ({ values, width, height, min, delta }) => {
  // if only one dot is present for chart — we place it at center
  if (values.length === 1) {
    return [[width / 2, height / 2]];
  }

  const step = width / (values.length - 1);
  return values.map((rawY, i) => [i * step, getNormalValue({ value: rawY, min, delta, height })]);
};

const HeartLineChart = forwardRef(({ values, redZoneValue, width, height, average, ...rest }, ref) => {
  const canvasRef = useRef(null);

  const padding = 3;
  const paddedWidth = width + padding * 2;
  const paddedHeight = height + padding * 2;

  // preparing data for plot: normalizing values
  const max = Math.max(...values);
  const min = Math.min(...values);
  const delta = max - min;

  const dots = useMemo(
    () => getNormalizedDots({ values, width, height, min, delta }).map(([x, y]) => [x + padding, y + padding]),
    [values, width, height, min, delta]
  );
  const averagePercentage = getNormalValue({ value: average, min, delta, height: 1 });
  const redY = getNormalValue({ value: redZoneValue, min, delta, height });

  const draw = useCallback(
    (ctx) => {
      const plotRed = "#FF0000";
      const plotGreen = "#00BE41";
      ctx.clearRect(0, 0, paddedWidth, paddedHeight);

      const gradient = ctx.createLinearGradient(0, redY, 0, paddedHeight);

      if (averagePercentage > 0) {
        gradient.addColorStop(0, plotRed);
        gradient.addColorStop(averagePercentage, plotGreen);
      } else {
        gradient.addColorStop(0, plotGreen);
      }

      ctx.strokeStyle = gradient;
      ctx.fillStyle = gradient;
      ctx.lineWidth = 2;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";

      // line
      ctx.beginPath();
      const [firstX, firstY] = dots[0];
      ctx.moveTo(firstX, firstY);
      dots.forEach(([x, y]) => ctx.lineTo(x, y));
      ctx.stroke();

      // dot (color is taken from current image data)
      const [[lastX, lastY]] = dots.slice(-1);
      ctx.beginPath();
      const pixel = ctx.getImageData(lastX * window.devicePixelRatio, lastY * window.devicePixelRatio, 1, 1).data;
      const pixelColorRGBA = `rgba(${pixel[0]}, ${pixel[1]}, ${pixel[2]}, ${pixel[3] / 255})`;
      ctx.fillStyle = pixelColorRGBA;
      ctx.arc(lastX, lastY, 3, 0, Math.PI * 2, true);
      ctx.fill();
    },
    [dots, paddedHeight, paddedWidth, averagePercentage, redY]
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) {
      return;
    }

    canvas.width = paddedWidth * window.devicePixelRatio;
    canvas.height = paddedHeight * window.devicePixelRatio;
    canvas.style.width = `${paddedWidth}px`;
    canvas.style.height = `${paddedHeight}px`;

    context.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Our draw come here
    draw(context);
  }, [draw, paddedHeight, paddedWidth]);

  return (
    <span ref={ref} {...rest}>
      <canvas width={width} height={height} ref={canvasRef} />
    </span>
  );
});

HeartLineChart.propTypes = {
  values: PropTypes.array.isRequired,
  redZoneValue: PropTypes.number.isRequired,
  average: PropTypes.number.isRequired,
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired
};

export default HeartLineChart;
