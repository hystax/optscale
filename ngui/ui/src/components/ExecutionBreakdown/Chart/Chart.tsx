import { Fragment } from "react";
import { Divider, Typography } from "@mui/material";
import { Box } from "@mui/system";
import { FormattedMessage } from "react-intl";
import CircleLabel from "components/CircleLabel";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import { createGroupsObjectFromArray, isEmpty as isEmptyArray } from "utils/arrays";
import { formatSecondsToHHMMSS } from "utils/datetime";
import { useRenderMilestonesLayer, useRenderStagesLayer } from "../ChartLayers";

const MILESTONES_LINE_ID = "milestones";
export const CHART_MARGIN_STYLES = Object.freeze({ top: 20, right: 70, left: 70, bottom: 22 });

const formatToChartTime = (x) => formatSecondsToHHMMSS(Number(x));

const Chart = ({
  domain,
  showMilestones,
  milestonesGroupedByTimeTuples,
  breakdownLines,
  highlightedStage,
  milestonesLine,
  colors
}) => {
  const renderMilestonesLayer = useRenderMilestonesLayer();
  const renderStagesLayer = useRenderStagesLayer();

  const isValueInDomain = (x) => {
    const [min, max] = domain;

    return x <= max && x >= min;
  };

  const filterLineData = (lineData) => lineData.filter(({ x }) => isValueInDomain(x));

  const filteredMilestonesGroupedByTimeTuples = milestonesGroupedByTimeTuples.filter(([time]) => isValueInDomain(time));

  const shouldShowMilestoneLabels = filteredMilestonesGroupedByTimeTuples.length < 4;

  const filteredMilestonesLine = {
    ...milestonesLine,
    data: filterLineData(milestonesLine.data)
  };

  const filteredBreakdownLines = breakdownLines.map((line) => ({
    ...line,
    data: filterLineData(line.data)
  }));

  const filteredLines = [filteredMilestonesLine, ...filteredBreakdownLines].filter(({ data }) => !isEmptyArray(data));

  return (
    <LineChart
      data={filteredLines}
      {...(isEmptyArray(breakdownLines)
        ? {
            emptyMessageId: "noDataToDisplay"
          }
        : {
            emptyMessageId: "noDataIsAvailableWithinTheSelectedBrushRange",
            emptyMessageValues: { br: <br /> }
          })}
      xScale={{
        type: "linear",
        min: "auto"
      }}
      yScale={{
        max: 1
      }}
      renderTooltipBody={({ slice: { points: allPoints = [] } = {} }) => {
        const { milestonePoints = [], ...restPoints } = createGroupsObjectFromArray(allPoints, (point) =>
          point.serieId === MILESTONES_LINE_ID ? "milestonePoints" : point.data.x
        );

        const pointsEntries = Object.entries(restPoints);

        const showZoomDataWarning = pointsEntries.length > 1;

        const renderPointData = () => {
          const point = pointsEntries[0];

          if (!point) {
            return null;
          }

          const [time, data] = point;

          return (
            <Fragment key={time}>
              <Typography component="div" fontWeight="bold">
                {formatToChartTime(time)}
              </Typography>
              {data.map(({ id, serieColor, data: { formattedLineName, formattedY } }) => (
                <KeyValueLabel
                  key={id}
                  renderKey={() => <CircleLabel figureColor={serieColor} label={formattedLineName} textFirst={false} />}
                  value={formattedY}
                  typographyProps={{
                    gutterBottom: true
                  }}
                />
              ))}
            </Fragment>
          );
        };

        const pointData = renderPointData();

        return (
          <>
            {showZoomDataWarning ? (
              <Box mb={1}>
                <Typography sx={{ maxWidth: "200px" }}>
                  <FormattedMessage id="considerZoomingForMoreDetailedInformation" />
                </Typography>
                <Divider />
              </Box>
            ) : null}
            {isEmptyArray(milestonePoints) ? null : (
              <Box mb={pointData ? 1 : 0}>
                <Typography fontWeight="bold">
                  <FormattedMessage id="milestones" />
                </Typography>
                {milestonePoints.map((milestonePoint) =>
                  milestonePoint.data.names.map((milestoneName) => (
                    <Typography key={`${milestonePoint.id}-${milestoneName}`}>{milestoneName}</Typography>
                  ))
                )}
                {pointData && <Divider />}
              </Box>
            )}
            {pointData}
          </>
        );
      }}
      colors={colors}
      style={{
        margin: CHART_MARGIN_STYLES
      }}
      overlayLayers={[
        showMilestones
          ? {
              key: "milestonesLayer",
              renderCanvasContent: renderMilestonesLayer({
                milestones: filteredMilestonesGroupedByTimeTuples,
                shouldShowMilestoneLabels
              })
            }
          : undefined,
        highlightedStage
          ? {
              key: "stagesHighlightLayer",
              renderCanvasContent: renderStagesLayer({
                highlightedStage,
                withHeader: true
              })
            }
          : undefined
      ].filter(Boolean)}
      axisLeft={
        [1, 2].includes(breakdownLines.length)
          ? {
              format: breakdownLines[0].formatAxis
            }
          : null
      }
      axisRight={
        breakdownLines.length === 2
          ? {
              format: breakdownLines[1].formatAxis
            }
          : null
      }
      axisBottom={{
        format: (value) => formatSecondsToHHMMSS(value),
        formatString: (value) => formatSecondsToHHMMSS(value)
      }}
    />
  );
};

export default Chart;
