import { useTheme } from "@mui/material/styles";

const SPACING_BETWEEN_MILESTONE_LINE_AND_NAME = 5;
const Y_AXIS_SHIFT_COEFFICIENT = 16;

export const useRenderMilestonesLayer = () => {
  const theme = useTheme();

  return ({ milestones, shouldShowMilestoneLabels = false }) =>
    (ctx, layerProps) => {
      const { xScale, linesAreaRectangle, theme: chartTheme } = layerProps;

      let namesCounter = 0;

      ctx.save();
      ctx.translate(linesAreaRectangle.xStart, linesAreaRectangle.yStart);

      milestones.forEach(([time, milestoneNames]) => {
        const milestoneX = xScale(time);

        ctx.beginPath();
        ctx.setLineDash([6, 6]);
        ctx.moveTo(milestoneX, 0);
        ctx.lineTo(milestoneX, linesAreaRectangle.height);
        ctx.stroke();

        if (shouldShowMilestoneLabels) {
          ctx.fillStyle = theme.palette.text.primary;
          ctx.font = chartTheme.canvas.text.font;

          milestoneNames.forEach((milestoneName) => {
            const { width: milestoneNameWidth } = ctx.measureText(milestoneName);

            const position = {
              x:
                /**
                 * Place the name of the milestone to the left of the vertical
                 * line if it goes beyond the rectangle
                 */
                milestoneX + SPACING_BETWEEN_MILESTONE_LINE_AND_NAME + milestoneNameWidth > linesAreaRectangle.xEnd
                  ? milestoneX - SPACING_BETWEEN_MILESTONE_LINE_AND_NAME - milestoneNameWidth
                  : milestoneX + SPACING_BETWEEN_MILESTONE_LINE_AND_NAME,
              y: linesAreaRectangle.yStart + namesCounter * Y_AXIS_SHIFT_COEFFICIENT
            };

            ctx.fillText(milestoneName, position.x, position.y);
            namesCounter += 1;
          });
        }
      });

      ctx.restore();
    };
};
