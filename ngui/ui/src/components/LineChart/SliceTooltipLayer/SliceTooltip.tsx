import { ReactNode } from "react";
import { useMeasure } from "@nivo/core";

export const TOOLTIP_ANCHOR = Object.freeze({
  LEFT: "left",
  RIGHT: "right"
});

type SliceTooltipProps = {
  chartWrapperWidth: number;
  mousePosition: { x: number; y: number };
  anchor: (typeof TOOLTIP_ANCHOR)[keyof typeof TOOLTIP_ANCHOR];
  children: ReactNode;
};

const TOOLTIP_OFFSET = 14;

const getTooltipTopLeftCornerCoordinates = (
  mousePosition: SliceTooltipProps["mousePosition"],
  tooltipBounds: ReturnType<typeof useMeasure>[1],
  anchor: SliceTooltipProps["anchor"]
) => {
  let x = Math.round(mousePosition.x);
  let y = Math.round(mousePosition.y);

  const hasDimension = tooltipBounds.width > 0 && tooltipBounds.height > 0;

  if (hasDimension) {
    if (anchor === TOOLTIP_ANCHOR.RIGHT) {
      x += TOOLTIP_OFFSET;
      y -= tooltipBounds.height / 2;
    }
    if (anchor === TOOLTIP_ANCHOR.LEFT) {
      x -= tooltipBounds.width + TOOLTIP_OFFSET;
      y -= tooltipBounds.height / 2;
    }
  }

  return {
    x,
    y
  };
};

const getXOffset = (xTopLeftCorner: number, tooltipWidth: number, chartWrapperWidth: number) => {
  const isFitOnLeft = xTopLeftCorner > 0;
  const isFitOnTheRight = xTopLeftCorner + tooltipWidth < chartWrapperWidth;

  if (!isFitOnLeft) {
    // move tooltip to the right back to the chart area
    return -xTopLeftCorner;
  }
  if (!isFitOnTheRight) {
    // move tooltip to the left back to the chart area
    return chartWrapperWidth - (xTopLeftCorner + tooltipWidth);
  }

  return 0;
};

const SliceTooltip = ({ chartWrapperWidth, mousePosition, anchor, children }: SliceTooltipProps) => {
  const [tooltipRef, tooltipBounds] = useMeasure();

  const { x: tooltipTopLeftCornerXCoordinate, y: tooltipTopLeftCornerYCoordinate } = getTooltipTopLeftCornerCoordinates(
    mousePosition,
    tooltipBounds,
    anchor
  );

  return (
    <div
      ref={tooltipRef}
      style={{
        position: "absolute",
        pointerEvents: "none",
        left:
          tooltipTopLeftCornerXCoordinate + getXOffset(tooltipTopLeftCornerXCoordinate, tooltipBounds.width, chartWrapperWidth),
        top: tooltipTopLeftCornerYCoordinate,
        maxWidth: chartWrapperWidth
      }}
    >
      {children}
    </div>
  );
};

export default SliceTooltip;
