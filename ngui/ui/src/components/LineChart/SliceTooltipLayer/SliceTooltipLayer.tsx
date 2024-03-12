import { useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useInheritedColor, useOrdinalColorScale } from "@nivo/colors";
import { useTheme, useValueFormatter } from "@nivo/core";
import { ChartsTooltipContext } from "contexts/ChartsTooltipContext";
import { usePoints, useSlices } from "./hooks";
import SliceTooltip, { TOOLTIP_ANCHOR } from "./SliceTooltip";

const useMousePosition = () => {
  const { setMousePosition: setExternalMousePosition, mousePosition: externalMousePosition } = useContext(ChartsTooltipContext);

  const [mousePositionState, setMousePositionState] = useState(undefined);

  const mousePosition = useMemo(() => externalMousePosition ?? mousePositionState, [externalMousePosition, mousePositionState]);

  const setMousePosition = useCallback(
    (coordinates) => {
      if (typeof setExternalMousePosition === "function") {
        setExternalMousePosition(coordinates);
      } else {
        setMousePositionState(coordinates);
      }
    },
    [setExternalMousePosition]
  );

  return [mousePosition, setMousePosition];
};

export const SliceTooltipLayer = ({
  wrapperDimensions,
  sliceTooltip,
  xFormat,
  yFormat,
  data,
  colors,
  series: rawSeries,
  pointColor,
  pointBorderColor,
  enableSlices,
  layerProps
}) => {
  const { outerHeight, outerWidth, linesAreaRectangle } = layerProps;
  const theme = useTheme();

  const getColor = useOrdinalColorScale(colors, "id");
  const getPointColor = useInheritedColor(pointColor, theme);
  const getPointBorderColor = useInheritedColor(pointBorderColor, theme);
  const formatX = useValueFormatter(xFormat);
  const formatY = useValueFormatter(yFormat);

  const series = useMemo(() => {
    const dataWithColor = data.map((line) => ({
      id: line.id,
      label: line.id,
      color: getColor(line)
    }));

    return dataWithColor
      .map((datum) => ({
        ...rawSeries.find((serie) => serie.id === datum.id),
        color: datum.color
      }))
      .filter((item) => Boolean(item.id));
  }, [data, rawSeries, getColor]);

  const points = usePoints({
    series,
    getPointColor,
    getPointBorderColor,
    formatX,
    formatY
  });

  const slices = useSlices({
    enableSlices,
    points,
    width: linesAreaRectangle.width,
    height: linesAreaRectangle.height
  });

  const canvasRef = useRef();
  const containerRef = useRef();

  const [mousePosition, setMousePosition] = useMousePosition();

  const getSliceAndTooltipSettings = () => {
    if (mousePosition) {
      const { x, y } = mousePosition;

      const cursorXRelativeToLinesAres = x - linesAreaRectangle.xStart;
      const cursorYRelativeToLinesAres = y - linesAreaRectangle.yStart;

      const sliceUnderCursor = slices.find(
        ({ x0, width, height }) =>
          cursorXRelativeToLinesAres <= x0 + width && cursorXRelativeToLinesAres >= x0 && cursorYRelativeToLinesAres <= height
      );

      if (sliceUnderCursor) {
        return {
          slice: sliceUnderCursor,
          tooltipSettings: {
            position: {
              x,
              y
            },
            anchor: cursorXRelativeToLinesAres > linesAreaRectangle.width / 2 ? TOOLTIP_ANCHOR.LEFT : TOOLTIP_ANCHOR.RIGHT
          }
        };
      }
    }

    return {
      slice: null,
      tooltipSettings: {
        position: {
          x: 0,
          y: 0
        },
        anchor: "right"
      }
    };
  };

  const { slice, tooltipSettings } = getSliceAndTooltipSettings();

  useEffect(() => {
    function mouseMoveHandler(event) {
      const { clientX, clientY } = event;
      const bounds = event.target.getBoundingClientRect();
      const cursorX = clientX - bounds.left;
      const cursorY = clientY - bounds.top;

      setMousePosition({
        x: cursorX,
        y: cursorY
      });
    }

    function mouseLeaveHandler() {
      setMousePosition(undefined);
    }

    const element = canvasRef.current;
    element.addEventListener("mousemove", mouseMoveHandler);
    element.addEventListener("mouseleave", mouseLeaveHandler);

    return () => {
      element.removeEventListener("mousemove", mouseMoveHandler);
      element.removeEventListener("mouseleave", mouseLeaveHandler);
    };
  }, [setMousePosition]);

  useEffect(() => {
    const ctx = canvasRef.current.getContext("2d");

    ctx.save();
    ctx.translate(linesAreaRectangle.xStart, linesAreaRectangle.yStart);

    if (slice) {
      ctx.beginPath();
      ctx.setLineDash([6, 6]);
      ctx.moveTo(slice.x, 0);
      ctx.lineTo(slice.x, linesAreaRectangle.height);
      ctx.stroke();
    }
    ctx.restore();

    return () => ctx.clearRect(0, 0, outerWidth, outerHeight);
  }, [linesAreaRectangle.height, linesAreaRectangle.xStart, linesAreaRectangle.yStart, outerHeight, outerWidth, slice]);

  return (
    <div
      ref={containerRef}
      style={{
        position: "absolute",
        zIndex: 3
      }}
    >
      {slice && (
        <SliceTooltip
          chartWrapperWidth={wrapperDimensions.width}
          mousePosition={tooltipSettings.position}
          anchor={tooltipSettings.anchor}
        >
          {sliceTooltip({
            slice
          })}
        </SliceTooltip>
      )}
      <canvas ref={canvasRef} height={outerHeight} width={outerWidth} />
    </div>
  );
};

export default SliceTooltipLayer;
