import { useTheme } from "@mui/material/styles";

export const useRenderStagesLayer = () => {
  const theme = useTheme();

  return ({ highlightedStage, withHeader = false }) =>
    (ctx, layerProps) => {
      const { xScale, areaOpacity, linesAreaRectangle, theme: chartTheme } = layerProps;

      const stageStartCoordinate = linesAreaRectangle.xStart + xScale(highlightedStage.start);
      const stageEndCoordinate = linesAreaRectangle.xStart + xScale(highlightedStage.end);

      // Get start and end coordinates inside of the lines area rectangle
      const start = Math.min(Math.max(stageStartCoordinate, linesAreaRectangle.xStart), linesAreaRectangle.xEnd);
      const end = Math.max(Math.min(stageEndCoordinate, linesAreaRectangle.xEnd), linesAreaRectangle.xStart);
      const stageWidth = end - start;

      ctx.save();
      ctx.globalAlpha = areaOpacity;
      ctx.fillStyle = theme.palette.info.main;
      ctx.beginPath();
      ctx.rect(start, linesAreaRectangle.yStart, stageWidth, linesAreaRectangle.height);
      ctx.fill();
      ctx.restore();

      if (withHeader && stageWidth > 0) {
        ctx.save();
        ctx.fillStyle = theme.palette.text.primary;
        ctx.textBaseline = "bottom";
        ctx.textAlign = "center";
        ctx.font = chartTheme.canvas.text.font;
        ctx.fillText(highlightedStage.name, start + stageWidth / 2, linesAreaRectangle.yStart - 6);
        ctx.restore();
      }
    };
};
