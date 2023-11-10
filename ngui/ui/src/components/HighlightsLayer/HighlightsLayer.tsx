import { useTheme } from "@mui/material/styles";
import { isEmpty as isEmptyArray } from "utils/arrays";

const HighlightArea = ({ start, end, height, areaOpacity }) => {
  const theme = useTheme();
  const color = theme.palette.info.main;
  return <rect x={start} width={end - start} height={height} opacity={areaOpacity} fill={color} />;
};

const getAreas = ({ shouldHighlight, xValues, getXCoordinateOfXValue }) => {
  if (xValues.length <= 1) {
    return [];
  }

  const halfDistanceBetweenValues = (getXCoordinateOfXValue(xValues[1]) - getXCoordinateOfXValue(xValues[0])) / 2;

  const getAreaStartShift = (currentValueIndex) => (currentValueIndex === 0 ? 0 : -halfDistanceBetweenValues);
  const getAreaEndShift = (currentValueIndex) => (currentValueIndex === xValues.length - 1 ? 0 : halfDistanceBetweenValues);

  return xValues
    .map((xValue, currentXValueIndex) => {
      if (shouldHighlight(xValue)) {
        const currentValueXCoordinate = getXCoordinateOfXValue(xValue);
        return {
          start: currentValueXCoordinate + getAreaStartShift(currentXValueIndex),
          end: currentValueXCoordinate + getAreaEndShift(currentXValueIndex)
        };
      }
      return null;
    })
    .filter(Boolean);
};

const HighlightsLayer = ({ chartOptions, shouldHighlight }) => {
  const { data = [], xScale: getXCoordinateOfXValue, innerHeight, areaOpacity } = chartOptions;

  const { data: points = [] } = data[0] ?? {};

  const xValues = points.map(({ x }) => x);

  const areas = getAreas({
    shouldHighlight,
    xValues,
    getXCoordinateOfXValue
  });

  return !isEmptyArray(areas) ? (
    <svg>
      <g>
        {areas.map(({ start, end }) => (
          <HighlightArea key={start} start={start} end={end} height={innerHeight} areaOpacity={areaOpacity} />
        ))}
      </g>
    </svg>
  ) : null;
};

export default HighlightsLayer;
