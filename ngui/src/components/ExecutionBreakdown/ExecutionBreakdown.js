import React, { useMemo, useRef, useState } from "react";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import { Divider, Typography, Stack } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import { extent } from "d3-array";
import PropTypes from "prop-types";
import { FormattedMessage, FormattedNumber } from "react-intl";
import { useParams } from "react-router-dom";
import ChartBrush from "components/ChartBrush";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import FormattedDigitalUnit, { IEC_UNITS } from "components/FormattedDigitalUnit";
import IconButton from "components/IconButton";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import MlBreakdownCheckboxes from "components/MlBreakdownCheckboxes";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import TypographyLoader from "components/TypographyLoader";
import { useApplicationBreakdown } from "hooks/useApplicationBreakdown";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { useMlBreakdownLines } from "hooks/useMlBreakdownLines";
import { createGroupsObjectFromArray, isEmpty as isEmptyArray } from "utils/arrays";
import { getColorsMap } from "utils/charts";
import { formatSecondsToHHMMSS, millisecondsToSeconds } from "utils/datetime";

const BREAKDOWN_BY_QUERY_PARAMETER = "breakdownBy";

const MILESTONES_LINE_ID = "milestones";

const ZOOM_MILESTONE_SECONDS_RANGE = 5;

const MilestonesTable = ({ milestones, onMilestoneZoom }) => {
  const tableData = useMemo(
    () =>
      milestones.map(([second, milestoneNames]) => ({
        second,
        milestoneNames
      })),
    [milestones]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_milestones">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "milestoneNames",
        disableSortBy: true,
        cell: ({ cell, row: { original }, index }) => (
          <Box display="flex" alignItems="center">
            <div>
              {cell.getValue().map((name) => (
                <div key={name}>{name}</div>
              ))}
            </div>
            <IconButton
              icon={<ZoomInIcon />}
              onClick={() => onMilestoneZoom(original.second)}
              dataTestId={`btn_select_milestone_${index}`}
              tooltip={{
                show: true,
                messageId: "zoom"
              }}
            />
          </Box>
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_time">
            <FormattedMessage id="time" />
          </TextWithDataTestId>
        ),
        accessorKey: "second",
        cell: ({ cell }) => formatSecondsToHHMMSS(cell.getValue()),
        defaultSort: "asc"
      }
    ],
    [onMilestoneZoom]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noMilestones"
      }}
    />
  );
};

const StagesTable = ({ stages, onStageZoom, onStageHighlight, isStageHighlighted }) => {
  const tableData = useMemo(() => stages, [stages]);

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_name">
            <FormattedMessage id="name" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        cell: ({ cell, row: { original }, index }) => {
          const value = cell.getValue();
          const isHighlighted = isStageHighlighted(original);
          return (
            <IconLabel
              endIcon={
                original.end ? (
                  <>
                    <IconButton
                      icon={<ZoomInIcon />}
                      onClick={() => onStageZoom(original.start, original.end)}
                      dataTestId={`btn_zoom_stage_${index}`}
                      tooltip={{
                        show: true,
                        messageId: "zoom"
                      }}
                    />
                    <IconButton
                      icon={<VisibilityOutlinedIcon color={isHighlighted ? "secondary" : "info"} />}
                      onClick={() =>
                        onStageHighlight(
                          isHighlighted
                            ? null
                            : {
                                name: value,
                                start: original.start,
                                end: original.end
                              }
                        )
                      }
                      dataTestId={`btn_highlight_stage_${index}`}
                      tooltip={{
                        show: true,
                        messageId: isHighlighted ? "removeHighlight" : "highlight"
                      }}
                    />
                  </>
                ) : null
              }
              label={value}
            />
          );
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_time">
            <FormattedMessage id="time" />
          </TextWithDataTestId>
        ),
        accessorKey: "start",
        cell: ({
          row: {
            original: { start, end, startTimestamp }
          }
        }) => {
          const formattedStart = formatSecondsToHHMMSS(start);
          const formattedEnd = end ? formatSecondsToHHMMSS(end) : null;

          return end ? (
            <>
              <div>
                <FormattedMessage
                  id="value - value"
                  values={{
                    value1: formattedStart,
                    value2: formattedEnd
                  }}
                />
              </div>
              <div>{formatSecondsToHHMMSS(end - start)}</div>
            </>
          ) : (
            <>
              <div>{formattedStart}</div>
              <div>
                <FormattedMessage
                  id="runningForX"
                  values={{
                    x: formatSecondsToHHMMSS(millisecondsToSeconds(+new Date()) - startTimestamp)
                  }}
                />
              </div>
            </>
          );
        },
        defaultSort: "asc"
      }
    ],
    [isStageHighlighted, onStageHighlight, onStageZoom]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      localization={{
        emptyMessageId: "noStages"
      }}
    />
  );
};

const CHART_MARGIN_STYLES = Object.freeze({ top: 20, right: 70, left: 70, bottom: 22 });
const BRUSH_HEIGHT = 12;
const BRUSH_MILESTONE_MARKER_RADIUS = 3;
// Add 1 to a marker radius in order to allocate enough space for the marker
const BRUSH_CHART_BOTTOM_MARGIN = BRUSH_MILESTONE_MARKER_RADIUS + 1;

const getMilestoneTuplesGroupedByTime = (milestones) => {
  const milestonesGroupedByTime = createGroupsObjectFromArray(milestones, (milestone) => milestone.time);

  const milestonesTuplesGroupedByTime = Object.entries(milestonesGroupedByTime).map((el) => [
    Number(el[0]),
    el[1].map(({ milestone }) => milestone)
  ]);

  return milestonesTuplesGroupedByTime;
};

const Tables = ({ milestonesGroupedByTimeTuples, resetBrushTo, stages, highlightedStage, setHighlightedStage }) => {
  const isUpSm = useIsUpMediaQuery("sm");

  return (
    <Stack
      sx={{ width: "100%" }}
      direction={isUpSm ? "row" : "column"}
      spacing={2}
      divider={isUpSm ? <Divider orientation="vertical" flexItem /> : null}
    >
      <div
        style={{
          width: isUpSm ? "50%" : "100%"
        }}
      >
        <SubTitle>
          <FormattedMessage id="stages" />
        </SubTitle>
        <StagesTable
          stages={stages}
          onStageZoom={(start, end) => resetBrushTo(start, end)}
          isStageHighlighted={(stage) => {
            if (highlightedStage === null) {
              return false;
            }
            return (
              stage.name === highlightedStage.name &&
              stage.start === highlightedStage.start &&
              stage.end === highlightedStage.end
            );
          }}
          onStageHighlight={(stage) => setHighlightedStage(stage)}
        />
      </div>
      <div
        style={{
          width: isUpSm ? "50%" : "100%"
        }}
      >
        <SubTitle>
          <FormattedMessage id="milestones" />
        </SubTitle>
        <MilestonesTable
          milestones={milestonesGroupedByTimeTuples}
          onMilestoneZoom={(second) =>
            resetBrushTo(second - ZOOM_MILESTONE_SECONDS_RANGE, second + ZOOM_MILESTONE_SECONDS_RANGE)
          }
        />
      </div>
    </Stack>
  );
};

const getBreakdownConfig = ({ goals = [] }) => ({
  host_ram: {
    renderBreakdownName: () => <FormattedMessage id="hostRAM" />,
    getPointValue: (data) => data.metrics.ram ?? null,
    formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
    formatAxis: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />
  },
  host_cpu: {
    renderBreakdownName: () => <FormattedMessage id="hostCPU" />,
    getPointValue: (data) => data.metrics.cpu ?? null,
    formatValue: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
    formatAxis: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
    maxValue: 100
  },
  process_cpu: {
    renderBreakdownName: () => <FormattedMessage id="processCPU" />,
    getPointValue: (data) => data.metrics.process_cpu ?? null,
    formatValue: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
    formatAxis: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
    maxValue: 100
  },
  process_ram: {
    renderBreakdownName: () => <FormattedMessage id="processRAM" />,
    getPointValue: (data) => data.metrics.process_ram ?? null,
    formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
    formatAxis: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />
  },
  disc_read: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="diskRead" />,
    getPointValue: (data) => data.metrics.disc_read ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  disc_write: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="diskWrite" />,
    getPointValue: (data) => data.metrics.disc_write ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  network_input: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="networkReceive" />,
    getPointValue: (data) => data.metrics.network_input ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  network_output: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="networkSend" />,
    getPointValue: (data) => data.metrics.network_output ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  gpu: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="gpu" />,
    getPointValue: (data) => data.metrics.gpu ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  gpu_memory: {
    isNotImplemented: true,
    renderBreakdownName: () => <FormattedMessage id="gpuMemory" />,
    getPointValue: (data) => data.metrics.gpu_memory ?? null,
    formatValue: (value) => value,
    formatAxis: (value) => value
  },
  ...Object.fromEntries(
    goals.map(({ name, key }) => [
      key,
      {
        renderBreakdownName: () => name,
        getPointValue: (data) => data.data?.[key] ?? null,
        formatValue: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} />,
        formatAxis: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} notation="compact" />
      }
    ])
  )
});

const ExecutionBreakdown = ({ breakdown, milestones, stages, goals }) => {
  const milestonesGroupedByTimeTuples = getMilestoneTuplesGroupedByTime(milestones);

  const theme = useTheme();
  const { modelId } = useParams();
  const brushRef = useRef(null);

  const breakdownConfig = getBreakdownConfig({ goals });

  const breakdownNames = Object.keys(breakdownConfig);
  const implementedBreakdownNames = Object.entries(breakdownConfig)
    // TODO ML: Get rid of «isNotImplemented» flag as soon as all breakdowns are implemented
    .filter(([, { isNotImplemented }]) => !isNotImplemented)
    .map(([name]) => name);

  const colorsMap = {
    [MILESTONES_LINE_ID]: "transparent",
    ...getColorsMap(breakdownNames, theme.palette.chart)
  };

  const { selectedBreakdowns, onBreakdownChange } = useApplicationBreakdown({
    modelId,
    queryParamName: BREAKDOWN_BY_QUERY_PARAMETER,
    breakdownNames: implementedBreakdownNames,
    storeId: "execution"
  });

  const breakdownSeconds = Object.keys(breakdown).map(Number);

  const xValuesRange = extent(breakdownSeconds);

  const [domain, setDomain] = useState(xValuesRange);

  const isValueInDomain = (x) => {
    const [min, max] = domain;

    return x <= max && x >= min;
  };

  const onBrushChange = (brushDomain) => {
    if (!brushDomain) {
      setDomain(xValuesRange);
      return;
    }

    const { x0, x1 } = brushDomain;

    setDomain([x0, x1]);
  };

  const breakdownLines = useMlBreakdownLines({
    breakdown,
    breakdownConfig,
    selectedBreakdowns
  });

  const milestonesLine = {
    id: MILESTONES_LINE_ID,
    data: milestonesGroupedByTimeTuples.map(([time, milestoneNames]) => ({
      x: Number(time),
      y: 0,
      names: milestoneNames
    }))
  };

  const lines = isEmptyArray(breakdownLines) ? [] : [milestonesLine, ...breakdownLines];

  const filterLineData = (lineData) => lineData.filter(({ x }) => isValueInDomain(x));

  const filteredMilestonesLine = {
    ...milestonesLine,
    data: filterLineData(milestonesLine.data)
  };

  const filteredBreakdownLines = breakdownLines.map((line) => ({
    ...line,
    data: filterLineData(line.data)
  }));

  const filteredLines = isEmptyArray(filteredBreakdownLines) ? [] : [filteredMilestonesLine, ...filteredBreakdownLines];

  const filteredMilestonesGroupedByTimeTuples = milestonesGroupedByTimeTuples.filter(
    ([time]) => time <= domain[1] && time >= domain[0]
  );

  const shouldShowMilestoneLabels = filteredMilestonesLine.data.length < 4;

  const [highlightedStage, setHighlightedStage] = useState(null);

  const resetBrushTo = (startPosition, endPosition) => {
    if (brushRef && brushRef.current !== null && typeof brushRef.current.resetTo === "function") {
      brushRef.current.resetTo(startPosition, endPosition);
    }
  };

  return (
    <div>
      <MlBreakdownCheckboxes
        selectedBreakdowns={selectedBreakdowns}
        colorsMap={colorsMap}
        breakdownConfig={breakdownConfig}
        onChange={onBreakdownChange}
      />
      {/* 
        TODO ML: Split «Brush chart» and «Line chart» into separate components
        This should help simplify the code in this file
      */}
      <LineChart
        data={filteredLines}
        xScale={{
          type: "linear",
          min: "auto"
        }}
        renderTooltipBody={({ slice = {} }) => {
          const { points } = slice;

          const { milestonePoints = [], restPoints = [] } = createGroupsObjectFromArray(points, (point) =>
            point.serieId === MILESTONES_LINE_ID ? "milestonePoints" : "restPoints"
          );

          const pointsList = restPoints.map((point) => (
            <KeyValueLabel
              key={point.id}
              renderKey={() => (
                <CircleLabel figureColor={point.serieColor} label={point.data.formattedLineName} textFirst={false} />
              )}
              value={point.data.formattedY}
              typographyProps={{
                gutterBottom: true
              }}
            />
          ));

          return (
            <>
              {isEmptyArray(milestonePoints) ? null : (
                <Box mb={isEmptyArray(pointsList) ? 0 : 1}>
                  <Typography>
                    <strong>
                      <FormattedMessage id="milestones" />
                    </strong>
                  </Typography>
                  {milestonePoints.map((milestonePoint) =>
                    milestonePoint.data.names.map((milestoneName) => (
                      <Typography key={`${milestonePoint.id}-${milestoneName}`}>{milestoneName}</Typography>
                    ))
                  )}
                  {!isEmptyArray(pointsList) && <Divider />}
                </Box>
              )}
              {pointsList}
            </>
          );
        }}
        colors={({ id }) => colorsMap[id]}
        style={{
          margin: CHART_MARGIN_STYLES
        }}
        verticalThresholdsLayer={(chartOptions) => {
          const { xScale: getXCoordinateOfXValue, innerHeight } = chartOptions;

          let namesCounter = 0;

          return (
            <g>
              {filteredMilestonesGroupedByTimeTuples.map(([time, payload]) => {
                const x = getXCoordinateOfXValue(time);

                return (
                  <g key={time}>
                    <line
                      x1={x}
                      y1={0}
                      x2={x}
                      y2={innerHeight}
                      stroke="black"
                      strokeWidth={1}
                      strokeOpacity={0.75}
                      strokeDasharray="6 6"
                    />
                    {shouldShowMilestoneLabels
                      ? payload.map((milestoneName) => {
                          namesCounter += 1;

                          return (
                            <text key={milestoneName} x={x + 5} y={namesCounter * 16}>
                              {milestoneName}
                            </text>
                          );
                        })
                      : null}
                  </g>
                );
              })}
            </g>
          );
        }}
        highlightsLayer={(chartOptions) => {
          const { xScale: getXCoordinateOfXValue, innerHeight, areaOpacity } = chartOptions;

          if (highlightedStage) {
            /**
             * Highlight should be rendered only between currently rendered points,
             * thus need to get min and max coordinates depending on currently rendered points (breakdowns seconds)
             */
            /**
             * TODO ML: Get currently rendered points into account
             * There is a corner case where there is less rendered points than seconds in a domain
             * E.g: seconds go from 12 to 24, but actual points are rendered between 12 to 23
             * In such cases highlighted area goes outside of the chart bounds
             */
            const breakdownSecondsInDomain = breakdownSeconds.filter((second) => isValueInDomain(second));
            const minMaxBreakdownSecondsInDomain = extent(breakdownSecondsInDomain);

            const start = getXCoordinateOfXValue(Math.max(minMaxBreakdownSecondsInDomain[0], highlightedStage.start));
            const end = getXCoordinateOfXValue(Math.min(minMaxBreakdownSecondsInDomain[1], highlightedStage.end));

            const width = end - start;

            return width !== 0 ? (
              <g>
                <text x={start + width / 2} y={-8} dominantBaseline="middle" textAnchor="middle">
                  {highlightedStage.name}
                </text>
                <rect x={start} width={end - start} height={innerHeight} opacity={areaOpacity} fill={theme.palette.info.main} />
              </g>
            ) : null;
          }

          return null;
        }}
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
        animate={false}
      />
      <ChartBrush
        ref={brushRef}
        xScaleType="linear"
        content={
          <LineChart
            pointSize={0}
            enableGridY={false}
            animate={false}
            data={lines}
            xScale={{
              type: "linear",
              min: "auto"
            }}
            renderTooltipBody={() => {}}
            colors={({ id }) => colorsMap[id]}
            style={{
              margin: {
                ...CHART_MARGIN_STYLES,
                bottom: BRUSH_CHART_BOTTOM_MARGIN,
                top: 0
              },
              height: BRUSH_HEIGHT
            }}
            axisBottom={null}
            highlightsLayer={(chartOptions) => {
              const { xScale: getXCoordinateOfXValue, innerHeight, areaOpacity } = chartOptions;

              if (highlightedStage) {
                const startCoordinate = getXCoordinateOfXValue(highlightedStage.start);
                const endCoordinate = getXCoordinateOfXValue(highlightedStage.end);
                const width = endCoordinate - startCoordinate;

                return (
                  <rect
                    x={startCoordinate}
                    width={width}
                    height={innerHeight}
                    opacity={areaOpacity}
                    fill={theme.palette.info.main}
                  />
                );
              }

              return null;
            }}
            verticalThresholdsLayer={(chartOptions) => {
              const { xScale: getXCoordinateOfXValue, innerHeight } = chartOptions;

              return (
                <g>
                  {milestonesGroupedByTimeTuples.map(([time]) => {
                    const x = getXCoordinateOfXValue(time);

                    return (
                      <g key={time}>
                        <circle
                          cx={x}
                          cy={innerHeight}
                          r={BRUSH_MILESTONE_MARKER_RADIUS}
                          stroke="black"
                          strokeWidth="1"
                          fill="white"
                        />
                      </g>
                    );
                  })}
                </g>
              );
            }}
          />
        }
        height={BRUSH_HEIGHT}
        marginLeft={CHART_MARGIN_STYLES.left}
        marginRight={CHART_MARGIN_STYLES.right}
        xRange={xValuesRange}
        onChange={onBrushChange}
      />
      <Tables
        milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
        resetBrushTo={resetBrushTo}
        stages={stages}
        highlightedStage={highlightedStage}
        setHighlightedStage={setHighlightedStage}
      />
    </div>
  );
};

/**
 * TODO ML: Improve loading state - it should include cards, lists, charts, and tables
 */
export const ExecutionBreakdownLoader = () => (
  <div>
    <TypographyLoader />
    <LineChart isLoading />
  </div>
);

ExecutionBreakdown.propTypes = {
  breakdown: PropTypes.object.isRequired,
  milestones: PropTypes.array.isRequired,
  stages: PropTypes.array.isRequired,
  goals: PropTypes.array.isRequired
};

export default ExecutionBreakdown;
