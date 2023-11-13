import { useTheme } from "@mui/material";
import { useIsOrganizationWeekend } from "hooks/useIsOrganizationWeekend";

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

        const xStart = currentValueXCoordinate + getAreaStartShift(currentXValueIndex);
        const xEnd = currentValueXCoordinate + getAreaEndShift(currentXValueIndex);
        const width = xEnd - xStart;

        return {
          xStart,
          xEnd,
          width
        };
      }
      return null;
    })
    .filter(Boolean);
};

export const useRenderWeekendsHighlightLayer = () => {
  const theme = useTheme();
  const isOrganizationWeekend = useIsOrganizationWeekend();

  return (ctx, layerProps) => {
    const { x, xScale, areaOpacity, linesAreaRectangle } = layerProps;

    const areas = getAreas({
      shouldHighlight: (xValue) => {
        const date = new Date(xValue);
        return isOrganizationWeekend(date);
      },
      xValues: x.all,
      getXCoordinateOfXValue: xScale
    });

    ctx.save();
    ctx.translate(linesAreaRectangle.xStart, linesAreaRectangle.yStart);

    ctx.globalAlpha = areaOpacity;

    areas.forEach(({ xStart, width }) => {
      ctx.beginPath();
      ctx.rect(xStart, 0, width, linesAreaRectangle.height);
      ctx.fillStyle = theme.palette.info.main;
      ctx.fill();
    });

    ctx.restore();
  };
};
