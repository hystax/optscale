import React from "react";
import PropTypes from "prop-types";
import { useChartTheme } from "hooks/useChartTheme";
import { unixTimestampToDateTime, EN_FORMAT, EN_TIME_FORMAT } from "utils/datetime";
import { remToPx } from "utils/fonts";

const getTranslateYShiftBasedOnTextFontSize = (fontSize) => {
  const numberFontSize = parseFloat(fontSize);

  return fontSize.toString().includes("rem") ? remToPx(numberFontSize) : numberFontSize;
};

const MetricChartBottomTick = ({ tick }) => {
  const { axis: { ticks: { line = {}, text = {} } = {} } = {} } = useChartTheme();
  const { stroke, strokeWidth } = line;
  const { fontSize, fill } = text;

  const { x, y, lineX, lineY, textAnchor, textBaseline, textX, textY, rotate, value } = tick;

  const defaultTextProps = {
    textAnchor,
    dominantBaseline: textBaseline,
    style: {
      fill,
      fontSize
    }
  };

  const getTextTransform = ({ translateX = textX, translateY = textY } = {}) =>
    `translate(${translateX}, ${translateY}), rotate(${rotate})`;

  return (
    <g transform={`translate(${x},${y})`}>
      <line stroke={stroke} strokeWidth={strokeWidth} x1={lineX} y1={lineX} x2={lineX} y2={lineY} />
      <text {...defaultTextProps} transform={getTextTransform()}>
        {unixTimestampToDateTime(value, EN_FORMAT)}
      </text>
      <text
        {...defaultTextProps}
        transform={getTextTransform({ translateY: textY + getTranslateYShiftBasedOnTextFontSize(fontSize) })}
      >
        {unixTimestampToDateTime(value, EN_TIME_FORMAT)}
      </text>
    </g>
  );
};

MetricChartBottomTick.propTypes = {
  tick: PropTypes.object
};

export default MetricChartBottomTick;
