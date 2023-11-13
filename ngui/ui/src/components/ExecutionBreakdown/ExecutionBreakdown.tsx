import { Fragment, useMemo, useRef, useState } from "react";
import VisibilityOutlinedIcon from "@mui/icons-material/VisibilityOutlined";
import ZoomInIcon from "@mui/icons-material/ZoomIn";
import { Divider, Typography, Stack } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import { extent } from "d3-array";
import { FormattedMessage, FormattedNumber, useIntl } from "react-intl";
import { useParams } from "react-router-dom";
import ChartBrush from "components/ChartBrush";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue, { useFormatDynamicFractionDigitsValue } from "components/DynamicFractionDigitsValue";
import FormattedDigitalUnit, { IEC_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import IconButton from "components/IconButton";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import MlBreakdownCheckboxes from "components/MlBreakdownCheckboxes";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import TypographyLoader from "components/TypographyLoader";
import { useIsUpMediaQuery } from "hooks/useMediaQueries";
import { BREAKDOWN_LINE_UNIT, useMlBreakdownLines } from "hooks/useMlBreakdownLines";
import { useModelBreakdownState } from "reducers/modelBreakdown/useModelBreakdownState";
import { createGroupsObjectFromArray, isEmpty as isEmptyArray } from "utils/arrays";
import { getColorsMap } from "utils/charts";
import { formatSecondsToHHMMSS, millisecondsToSeconds } from "utils/datetime";
import { useRenderMilestoneDotsLayer, useRenderStagesLayer, useRenderMilestonesLayer } from "./ChartLayers";

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

const Chart = ({ domain, milestonesGroupedByTimeTuples, breakdownLines, highlightedStage, milestonesLine, colors }) => {
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
                {formatSecondsToHHMMSS(Number(time))}
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
        {
          key: "milestonesLayer",
          renderCanvasContent: renderMilestonesLayer({
            milestones: filteredMilestonesGroupedByTimeTuples,
            shouldShowMilestoneLabels
          })
        },
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

const Brush = ({ brushRef, lines, colors, milestones, xRange, highlightedStage, onBrushChange }) => {
  const renderMilestoneDotsLayer = useRenderMilestoneDotsLayer();
  const renderStagesLayer = useRenderStagesLayer();

  return (
    <ChartBrush
      ref={brushRef}
      xScaleType="linear"
      content={
        <LineChart
          pointSize={0}
          enableGridY={false}
          data={lines}
          xScale={{
            type: "linear",
            min: "auto"
          }}
          yScale={{
            max: 1
          }}
          renderTooltipBody={() => {}}
          colors={colors}
          style={{
            margin: {
              ...CHART_MARGIN_STYLES,
              bottom: BRUSH_CHART_BOTTOM_MARGIN,
              top: 0
            },
            height: BRUSH_HEIGHT
          }}
          axisBottom={null}
          overlayLayers={[
            {
              key: "milestoneDotsLayer",
              renderCanvasContent: renderMilestoneDotsLayer({
                milestones,
                markerRadius: BRUSH_MILESTONE_MARKER_RADIUS
              })
            },
            highlightedStage
              ? {
                  key: "stagesHighlightLayer",
                  renderCanvasContent: renderStagesLayer({
                    highlightedStage
                  })
                }
              : undefined
          ].filter(Boolean)}
        />
      }
      height={BRUSH_HEIGHT}
      marginLeft={CHART_MARGIN_STYLES.left}
      marginRight={CHART_MARGIN_STYLES.right}
      xRange={xRange}
      onChange={onBrushChange}
    />
  );
};

const ExecutionBreakdown = ({ breakdown, milestones, stages, reachedGoals = {} }) => {
  const milestonesGroupedByTimeTuples = getMilestoneTuplesGroupedByTime(milestones);

  const theme = useTheme();
  const intl = useIntl();
  const brushRef = useRef(null);

  const { modelId } = useParams();

  const formatDigitalUnit = useFormatDigitalUnit();
  const formatDynamicFractionDigitsValue = useFormatDynamicFractionDigitsValue();

  const getMetricsBreakdownConfig = () => [
    {
      name: "host_ram",
      renderBreakdownName: () => <FormattedMessage id="hostRAM" />,
      getPointValue: (data) => data.metrics?.ram ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDigitalUnit({
          value,
          baseUnit: IEC_UNITS.MEBIBYTE,
          maximumFractionDigits: 2
        }),
      unit: BREAKDOWN_LINE_UNIT.MEBIBYTE
    },
    {
      name: "host_cpu",
      renderBreakdownName: () => <FormattedMessage id="hostCPU" />,
      getPointValue: (data) => data.metrics?.cpu ?? null,
      formatValue: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
      formatAxis: (value) =>
        intl.formatNumber(value / 100, {
          format: "percentage2"
        }),
      unit: BREAKDOWN_LINE_UNIT.PERCENT
    },
    {
      name: "process_cpu",
      renderBreakdownName: () => <FormattedMessage id="processCPU" />,
      getPointValue: (data) => data.metrics?.process_cpu ?? null,
      formatValue: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
      formatAxis: (value) =>
        intl.formatNumber(value / 100, {
          format: "percentage2"
        }),
      unit: BREAKDOWN_LINE_UNIT.PERCENT
    },
    {
      name: "process_ram",
      renderBreakdownName: () => <FormattedMessage id="processRAM" />,
      getPointValue: (data) => data.metrics?.process_ram ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDigitalUnit({
          value,
          baseUnit: IEC_UNITS.MEBIBYTE,
          maximumFractionDigits: 2
        }),
      unit: BREAKDOWN_LINE_UNIT.MEBIBYTE
    },
    {
      name: "gpu_load",
      renderBreakdownName: () => <FormattedMessage id="gpu" />,
      getPointValue: (data) => data.metrics?.gpu_load ?? null,
      formatValue: (value) => <FormattedNumber format="percentage2" value={value / 100} />,
      formatAxis: (value) =>
        intl.formatNumber(value / 100, {
          format: "percentage2"
        }),
      unit: BREAKDOWN_LINE_UNIT.PERCENT
    },
    {
      name: "gpu_memory_used",
      renderBreakdownName: () => <FormattedMessage id="gpuMemory" />,
      getPointValue: (data) => data.metrics?.gpu_memory_used ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={IEC_UNITS.MEBIBYTE} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDigitalUnit({
          value,
          baseUnit: IEC_UNITS.MEBIBYTE,
          maximumFractionDigits: 2
        }),
      unit: BREAKDOWN_LINE_UNIT.MEBIBYTE
    },
    {
      name: "disc_read",
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="diskRead" />,
      getPointValue: (data) => data.metrics?.disc_read ?? null,
      formatValue: (value) => value,
      formatAxis: (value) => value
    },
    {
      name: "disc_write",
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="diskWrite" />,
      getPointValue: (data) => data.metrics?.disc_write ?? null,
      formatValue: (value) => value,
      formatAxis: (value) => value
    },
    {
      name: "network_input",
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="networkReceive" />,
      getPointValue: (data) => data.metrics?.network_input ?? null,
      formatValue: (value) => value,
      formatAxis: (value) => value
    },
    {
      name: "network_output",
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="networkSend" />,
      getPointValue: (data) => data.metrics?.network_output ?? null,
      formatValue: (value) => value,
      formatAxis: (value) => value
    }
  ];

  const getGoalsBreakdownConfig = () =>
    Object.entries(reachedGoals).map(([key, { name }]) => ({
      name: key,
      renderBreakdownName: () => name,
      getPointValue: (data) => data.data?.[key] ?? null,
      formatValue: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} />,
      formatAxis: (value) =>
        formatDynamicFractionDigitsValue({
          value,
          maximumFractionDigits: 2,
          notation: "compact"
        })
    }));

  const metricsBreakdownConfig = getMetricsBreakdownConfig();
  const goalsBreakdownConfig = getGoalsBreakdownConfig();

  const breakdownConfig = [...metricsBreakdownConfig, ...goalsBreakdownConfig];

  const implementedMetricsBreakdownNames = metricsBreakdownConfig
    // TODO ML: Get rid of «isNotImplemented» flag as soon as all breakdowns are implemented
    .filter(({ isNotImplemented }) => !isNotImplemented)
    .map(({ name }) => name);
  const goalsBreakdownNames = goalsBreakdownConfig.map(({ name }) => name);

  const breakdownNames = [...implementedMetricsBreakdownNames, ...goalsBreakdownNames];

  const colorsMap = {
    [MILESTONES_LINE_ID]: "transparent",
    ...getColorsMap(breakdownNames, theme.palette.chart)
  };

  const { selectedBreakdowns, addBreakdown, removeBreakdown } = useModelBreakdownState({
    modelId,
    queryParamName: BREAKDOWN_BY_QUERY_PARAMETER,
    breakdownNames,
    initialSelectedBreakdowns: implementedMetricsBreakdownNames,
    storeId: "execution"
  });

  const breakdownSeconds = Object.keys(breakdown).map(Number);
  const milestoneSeconds = milestonesGroupedByTimeTuples.map(([second]) => second);

  const xValuesRange = extent([...breakdownSeconds, ...milestoneSeconds]);

  const [domain, setDomain] = useState(xValuesRange);
  const [highlightedStage, setHighlightedStage] = useState(null);

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

  const lines = [milestonesLine, ...breakdownLines].filter(({ data }) => !isEmptyArray(data));

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
        onAddBreakdown={addBreakdown}
        onRemoveBreakdown={removeBreakdown}
      />
      <Chart
        domain={domain}
        milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
        highlightedStage={highlightedStage}
        breakdownLines={breakdownLines}
        milestonesLine={milestonesLine}
        colors={({ id }) => colorsMap[id]}
      />
      <Brush
        brushRef={brushRef}
        lines={lines}
        colors={({ id }) => colorsMap[id]}
        highlightedStage={highlightedStage}
        milestones={milestonesGroupedByTimeTuples}
        xRange={xValuesRange}
        onBrushChange={onBrushChange}
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

export default ExecutionBreakdown;
