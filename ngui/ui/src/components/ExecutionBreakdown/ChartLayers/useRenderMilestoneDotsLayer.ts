export const useRenderMilestoneDotsLayer =
  () =>
  ({ milestones, markerRadius }) =>
  (ctx, layerProps) => {
    const { xScale, linesAreaRectangle } = layerProps;

    ctx.save();
    ctx.translate(linesAreaRectangle.xStart, linesAreaRectangle.yStart);

    milestones.forEach(([time]) => {
      const milestoneX = xScale(time);

      ctx.beginPath();
      ctx.arc(milestoneX, linesAreaRectangle.height, markerRadius, 0, 2 * Math.PI);
      ctx.stroke();
    });

    ctx.restore();
  };
