import { useMemo, useState } from "react";
import AddchartOutlinedIcon from "@mui/icons-material/AddchartOutlined";
import GridOnIcon from "@mui/icons-material/GridOn";
import GridViewIcon from "@mui/icons-material/GridView";
import SplitscreenIcon from "@mui/icons-material/Splitscreen";
import { Grid, ToggleButton, ToggleButtonGroup, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { Box } from "@mui/system";
import { extent } from "d3-array";
import { FormattedNumber, useIntl } from "react-intl";
import { useParams } from "react-router-dom";
import Button from "components/Button";
import DynamicFractionDigitsValue, { useFormatDynamicFractionDigitsValue } from "components/DynamicFractionDigitsValue";
import FormattedDigitalUnit, { IEC_UNITS, formatDigitalUnit } from "components/FormattedDigitalUnit";
import IconButton from "components/IconButton";
import LineChart from "components/LineChart";
import { RenameMlRunChartModal, SelectStageOrMilestoneModal } from "components/SideModalManager/SideModals";
import TypographyLoader from "components/TypographyLoader";
import { ChartsTooltipContextProvider } from "contexts/ChartsTooltipContext";
import { BREAKDOWN_LINE_UNIT } from "hooks/useMlBreakdownLines";
import { GRID_TYPES, useModelRunChartState } from "hooks/useModelRunChartState";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { getColorsMap } from "utils/charts";
import { SPACING_1, SPACING_2, SPACING_4 } from "utils/layouts";
import ChartContainer from "./ChartContainer";
import ChartSwitch from "./ChartSwitch";
import DashboardControls from "./DashboardControls";
import TimerangeSlider, { formatToChartTime } from "./TimerangeSlider";
import { getMilestoneTuplesGroupedByTime } from "./utils";

const MILESTONES_LINE_ID = "milestones";

const MUI_GRID_VALUES = Object.freeze({
  [GRID_TYPES.ONE_COLUMN]: 12,
  [GRID_TYPES.TWO_COLUMN]: 6,
  [GRID_TYPES.THREE_COLUMNS]: 4
});

const GridButton = ({ gridType, onClick }) => (
  <ToggleButtonGroup
    size="small"
    value={gridType}
    exclusive
    onChange={(_, value) => {
      if (value !== null) {
        onClick(value);
      }
    }}
  >
    <ToggleButton value={GRID_TYPES.ONE_COLUMN}>
      <SplitscreenIcon fontSize="small" />
    </ToggleButton>
    <ToggleButton value={GRID_TYPES.TWO_COLUMN}>
      <GridViewIcon fontSize="small" />
    </ToggleButton>
    <ToggleButton value={GRID_TYPES.THREE_COLUMNS}>
      <GridOnIcon fontSize="small" />
    </ToggleButton>
  </ToggleButtonGroup>
);

const ExecutionBreakdown = ({ breakdown, milestones, reachedGoals = {}, taskId }) => {
  const milestonesGroupedByTimeTuples = getMilestoneTuplesGroupedByTime(milestones);

  const theme = useTheme();
  const intl = useIntl();

  const formatDynamicFractionDigitsValue = useFormatDynamicFractionDigitsValue();

  const metricsBreakdownConfig = useMemo(
    () => [
      {
        name: "host_ram",
        renderBreakdownName: () => intl.formatMessage({ id: "hostRAM" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "hostCPU" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "processCPU" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "processRAM" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "gpu" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "gpuMemory" }),
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
        renderBreakdownName: () => intl.formatMessage({ id: "diskRead" }),
        getPointValue: (data) => data.metrics?.disc_read ?? null,
        formatValue: (value) => value,
        formatAxis: (value) => value
      },
      {
        name: "disc_write",
        isNotImplemented: true,
        renderBreakdownName: () => intl.formatMessage({ id: "diskWrite" }),
        getPointValue: (data) => data.metrics?.disc_write ?? null,
        formatValue: (value) => value,
        formatAxis: (value) => value
      },
      {
        name: "network_input",
        isNotImplemented: true,
        renderBreakdownName: () => intl.formatMessage({ id: "networkReceive" }),
        getPointValue: (data) => data.metrics?.network_input ?? null,
        formatValue: (value) => value,
        formatAxis: (value) => value
      },
      {
        name: "network_output",
        isNotImplemented: true,
        renderBreakdownName: () => intl.formatMessage({ id: "networkSend" }),
        getPointValue: (data) => data.metrics?.network_output ?? null,
        formatValue: (value) => value,
        formatAxis: (value) => value
      }
    ],
    [intl]
  );

  const goalsBreakdownConfig = useMemo(
    () =>
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
      })),
    [formatDynamicFractionDigitsValue, reachedGoals]
  );

  const breakdownConfig = [...metricsBreakdownConfig, ...goalsBreakdownConfig];

  const implementedMetricsBreakdownNames = useMemo(
    () =>
      metricsBreakdownConfig
        // TODO ML: Get rid of «isNotImplemented» flag as soon as all breakdowns are implemented
        .filter(({ isNotImplemented }) => !isNotImplemented)
        .map(({ name }) => name),
    [metricsBreakdownConfig]
  );

  const breakdownNames = useMemo(
    () => [...implementedMetricsBreakdownNames, ...goalsBreakdownConfig.map(({ name }) => name)],
    [implementedMetricsBreakdownNames, goalsBreakdownConfig]
  );

  const colorsMap = {
    [MILESTONES_LINE_ID]: "transparent",
    ...getColorsMap(breakdownNames, theme.palette.chart)
  };

  const breakdownSeconds = Object.keys(breakdown).map(Number);
  const milestoneSeconds = milestonesGroupedByTimeTuples.map(([second]) => second);

  const xValuesRange = extent([...breakdownSeconds, ...milestoneSeconds]);

  const milestonesLine = {
    id: MILESTONES_LINE_ID,
    data: milestonesGroupedByTimeTuples.map(([time, milestoneNames]) => ({
      x: Number(time),
      y: 0,
      names: milestoneNames
    }))
  };

  const openSideModal = useOpenSideModal();
  const { runId } = useParams();

  const [highlightedStage, setHighlightedStage] = useState(null);
  const [selectedSegment, setSelectedSegment] = useState(null);

  const onStageSelectClick = () =>
    openSideModal(SelectStageOrMilestoneModal, {
      runId,
      highlightedStage,
      setHighlightedStage,
      setSelectedSegment,
      secondsTimeRange: xValuesRange
    });

  const getSelectedSegment = () => selectedSegment ?? xValuesRange;
  const [fromFormatted, toFormatted] = getSelectedSegment().map(formatToChartTime);
  const chartsTimerangeMessage = intl.formatMessage({ id: "timerange" }, { from: fromFormatted, to: toFormatted });

  const {
    currentEmployeeId,
    dashboard,
    onDashboardChange,
    dashboards,
    saved,
    updateDashboard,
    removeDashboard,
    createDashboard,
    addChart,
    updateChartName,
    updateChartBreakdowns,
    removeChart,
    cloneChart,
    enableMilestones,
    disableMilestones,
    enableTooltipSync,
    disableTooltipSync,
    updateGridType,
    isLoadingProps
  } = useModelRunChartState({
    taskId,
    implementedMetricsBreakdownNames,
    breakdownNames
  });

  const {
    data: { charts, show_milestones: showMilestones, sync_tooltips: syncTooltips, grid_type: gridType }
  } = dashboard;

  const [mousePosition, setMousePosition] = useState(undefined);

  return (
    <>
      <Box
        sx={{
          mb: SPACING_2,
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          flexDirection: { md: "row", xs: "column" }
        }}
      >
        <Box
          sx={{
            flexGrow: 1,
            maxWidth: { md: "60%" },
            mr: { md: SPACING_4 },
            ml: { xs: SPACING_1, md: SPACING_2 }
          }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              alignItems: "center",
              flexWrap: "wrap",
              marginBottom: theme.spacing(1)
            }}
          >
            <Typography>
              {chartsTimerangeMessage}
              <Button
                sx={{ ml: { xs: 0, md: SPACING_1 }, mr: SPACING_2 }}
                messageId="selectStageOrMilestone"
                onClick={onStageSelectClick}
              />
            </Typography>
            <ChartSwitch
              messageId="showMilestones"
              onChange={(newChecked) => (newChecked ? enableMilestones() : disableMilestones())}
              checked={showMilestones}
            />
            <ChartSwitch
              messageId="syncTooltips"
              onChange={(newChecked) => (newChecked ? enableTooltipSync() : disableTooltipSync())}
              checked={syncTooltips}
            />
            <GridButton onClick={updateGridType} gridType={gridType} />
            <IconButton
              icon={<AddchartOutlinedIcon />}
              onClick={addChart}
              tooltip={{
                show: true,
                messageId: "addChart"
              }}
            />
            <TimerangeSlider
              selectedSegment={selectedSegment}
              setSelectedSegment={setSelectedSegment}
              xValuesRange={xValuesRange}
              milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
            />
          </Box>
        </Box>
        <Box display="flex" alignItems="center" sx={{ ml: { md: 0, xs: SPACING_1 } }}>
          <DashboardControls
            currentEmployeeId={currentEmployeeId}
            dashboard={dashboard}
            dashboards={dashboards}
            onDashboardChange={onDashboardChange}
            saved={saved}
            updateDashboard={({ name, shared }) => updateDashboard({ name, shared })}
            createDashboard={({ name, shared }) => createDashboard({ name, shared })}
            removeDashboard={(id) => removeDashboard(id)}
            isLoadingProps={isLoadingProps}
          />
        </Box>
      </Box>
      <Grid spacing={SPACING_2} container>
        <ChartsTooltipContextProvider
          setMousePosition={syncTooltips ? setMousePosition : undefined}
          mousePosition={syncTooltips ? mousePosition : undefined}
        >
          {charts.map(({ id: chartId, breakdowns, name }) => (
            <Grid item xs={12} md={MUI_GRID_VALUES[gridType] ?? 12} key={chartId}>
              <ChartContainer
                showMilestones={showMilestones}
                domain={getSelectedSegment()}
                milestonesGroupedByTimeTuples={milestonesGroupedByTimeTuples}
                highlightedStage={highlightedStage}
                milestonesLine={milestonesLine}
                colorsMap={colorsMap}
                breakdownConfig={breakdownConfig}
                breakdown={breakdown}
                id={chartId}
                onRemove={charts.length === 1 ? undefined : removeChart}
                onClone={cloneChart}
                onRename={() =>
                  openSideModal(RenameMlRunChartModal, {
                    chartName: name,
                    onRename: (newName) => {
                      updateChartName(chartId, newName);
                    }
                  })
                }
                selectedBreakdowns={breakdowns}
                onSelectedBreakdownsChange={(newBreakdowns) => updateChartBreakdowns(chartId, newBreakdowns)}
                name={name}
              />
            </Grid>
          ))}
        </ChartsTooltipContextProvider>
      </Grid>
    </>
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
