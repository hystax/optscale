import { renderLegendToCanvas } from "@nivo/legends";
import { truncateCanvasText } from "utils/charts";
import { MAX_LEGEND_LABEL_WIDTH } from "utils/constants";

const DEFAULT_LAYERS = ["grid", "axes", "bars", "annotations", "totals"];

export const selectedBarLayer = (ctx: CanvasRenderingContext2D, layerContext, { selectedBar, drawBar, getBarSettings }) => {
  if (selectedBar) {
    layerContext.bars.forEach((bar) => {
      drawBar(ctx, getBarSettings(bar));
    });
  }
};

export const barsRefLayer = (ctx: CanvasRenderingContext2D, { bars }, { barsRef, getBarSettings }) => {
  // eslint-disable-next-line no-param-reassign
  barsRef.current = bars.map((bar) => getBarSettings(bar));
};

export const thresholdMarkerLayer = (ctx: CanvasRenderingContext2D, layerContext, { thresholdMarker, chartTheme }) => {
  const { innerWidth, yScale } = layerContext;

  const yTotal = yScale(thresholdMarker.value);

  const x0 = 0;
  const x1 = innerWidth;
  const y0 = yTotal;
  const y1 = yTotal;

  ctx.save();
  ctx.strokeStyle = chartTheme.canvas.marker.color;
  ctx.lineWidth = chartTheme.canvas.marker.lineWidth;

  ctx.beginPath();
  ctx.setLineDash(chartTheme.canvas.marker.lineDash);
  ctx.moveTo(x0, y0);
  ctx.lineTo(x1, y1);
  ctx.stroke();

  const textX0 = innerWidth - chartTheme.canvas.marker.xOffset;
  const textY0 = yTotal - chartTheme.canvas.marker.yOffset;

  ctx.textAlign = "right";
  ctx.fillStyle = chartTheme.canvas.marker.color;
  const text = thresholdMarker.format?.(thresholdMarker.value) ?? thresholdMarker.value;
  ctx.font = chartTheme.canvas.marker.font;
  ctx.fillText(text, textX0, textY0);
  ctx.restore();
};

export const legendLayer = (ctx: CanvasRenderingContext2D, layerContext, { chartTheme, legendLabel }) => {
  const { legendData, innerWidth, innerHeight } = layerContext;

  // Explicitly set font to correctly measure text width
  ctx.save();
  ctx.font = `${chartTheme.legends.text.fontSize}px ${chartTheme.legends.text.fontFamily}`;

  legendData.forEach(([legend, data]) => {
    renderLegendToCanvas(ctx, {
      ...legend,
      data: data.map((item) => {
        const { label, shouldTruncate } =
          typeof legendLabel === "function"
            ? legendLabel(item, ctx, {
                maxWidth: MAX_LEGEND_LABEL_WIDTH,
              })
            : {
                label: item.id,
                shouldTruncate: true,
              };

        return {
          ...item,
          label: shouldTruncate ? truncateCanvasText(ctx, label, MAX_LEGEND_LABEL_WIDTH) : label,
        };
      }),
      containerWidth: innerWidth,
      containerHeight: innerHeight,
      theme: chartTheme,
    });
  });

  ctx.restore();
};

export const getChartLayers = ({
  selectedBar,
  barsRef,
  thresholdMarker,
  withLegend,
  chartTheme,
  drawBar,
  getBarSettings,
  legendLabel,
}) => {
  const selectedBarLayerFn = (ctx: CanvasRenderingContext2D, layerContext) =>
    selectedBarLayer(ctx, layerContext, { selectedBar, drawBar, getBarSettings });

  const barsRefLayerFn = (ctx: CanvasRenderingContext2D, layerContext) =>
    barsRefLayer(ctx, layerContext, { barsRef, getBarSettings });

  const thresholdMarkerLayerFn = (ctx: CanvasRenderingContext2D, layerContext) =>
    thresholdMarkerLayer(ctx, layerContext, { thresholdMarker, chartTheme });

  const legendLayerFn = (ctx: CanvasRenderingContext2D, layerContext) =>
    legendLayer(ctx, layerContext, { chartTheme, legendLabel });

  return [
    ...DEFAULT_LAYERS,
    selectedBarLayerFn,
    barsRefLayerFn,
    ...(thresholdMarker ? [thresholdMarkerLayerFn] : []),
    ...(withLegend ? [legendLayerFn] : []),
  ];
};
