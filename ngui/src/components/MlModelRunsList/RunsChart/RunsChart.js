import React from "react";
import { Stack, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage, useIntl } from "react-intl";
import { useParams } from "react-router-dom";
import CircleLabel from "components/CircleLabel";
import DynamicFractionDigitsValue from "components/DynamicFractionDigitsValue";
import FormattedDigitalUnit, { SI_UNITS } from "components/FormattedDigitalUnit";
import FormattedMoney from "components/FormattedMoney";
import KeyValueLabel from "components/KeyValueLabel";
import LineChart from "components/LineChart";
import MlBreakdownCheckboxes from "components/MlBreakdownCheckboxes";
import { useApplicationBreakdown } from "hooks/useApplicationBreakdown";
import { useFormatIntervalDuration } from "hooks/useFormatIntervalDuration";
import { useMlBreakdownLines } from "hooks/useMlBreakdownLines";
import { getColorsMap } from "utils/charts";
import { FORMATTED_MONEY_TYPES } from "utils/constants";
import { intervalToDuration, INTERVAL_DURATION_VALUE_TYPES } from "utils/datetime";

const BREAKDOWN_BY_QUERY_PARAMETER = "breakdownBy";

const FormattedDuration = ({ value, compact }) => {
  const formatInterval = useFormatIntervalDuration();

  const intl = useIntl();

  return value === 0
    ? intl.formatMessage({ id: compact ? "xSecondsCompact" : "xSeconds" }, { x: 0 })
    : formatInterval({
        formatTo: [
          INTERVAL_DURATION_VALUE_TYPES.WEEKS,
          INTERVAL_DURATION_VALUE_TYPES.DAYS,
          INTERVAL_DURATION_VALUE_TYPES.HOURS,
          INTERVAL_DURATION_VALUE_TYPES.MINUTES,
          INTERVAL_DURATION_VALUE_TYPES.SECONDS
        ],
        duration: intervalToDuration({
          start: 0,
          end: value * 1000
        }),
        compact
      });
};

const CHART_MARGIN_STYLES = Object.freeze({ top: 20, right: 60, left: 60, bottom: 50 });

const getBreakdownConfig = ({ runs }) => {
  const goalBreakdownNameKeyMap = Object.fromEntries(
    runs.filter(({ goals }) => !!goals).flatMap((run) => run.goals.map(({ key, name }) => [name, key]))
  );

  const goalBreakdownNames = Object.keys(goalBreakdownNameKeyMap);

  return {
    duration: {
      renderBreakdownName: () => <FormattedMessage id="duration" />,
      getPointValue: (run) => run.duration,
      formatValue: (value) => <FormattedDuration value={value} />,
      formatAxis: (value) => <FormattedDuration value={value} compact />
    },
    expenses: {
      renderBreakdownName: () => <FormattedMessage id="expenses" />,
      getPointValue: (run) => run.cost ?? null,
      formatValue: (value) => <FormattedMoney value={value} />,
      formatAxis: (value) => <FormattedMoney value={value} type={FORMATTED_MONEY_TYPES.COMPACT} />
    },
    task_cpu: {
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="tasksCPU" />,
      getPointValue: (run) => run.task_cpu ?? null,
      formatValue: (value) => <FormattedDuration value={value} />,
      formatAxis: (value) => <FormattedDuration value={value} compact />
    },
    cpu_uptime: {
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="cpuUptime" />,
      getPointValue: (run) => run.cpu_uptime ?? null,
      formatValue: (value) => <FormattedDuration value={value} />,
      formatAxis: (value) => <FormattedDuration value={value} compact />
    },
    data_read: {
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="dataRead" />,
      getPointValue: (run) => run.data_read ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={SI_UNITS.MEGABYTE} maximumFractionDigits={2} />,
      formatAxis: (value) => <FormattedDigitalUnit value={value} baseUnit={SI_UNITS.MEGABYTE} maximumFractionDigits={2} />
    },
    data_written: {
      isNotImplemented: true,
      renderBreakdownName: () => <FormattedMessage id="dataWritten" />,
      getPointValue: (run) => run.data_written ?? null,
      formatValue: (value) => <FormattedDigitalUnit value={value} baseUnit={SI_UNITS.MEGABYTE} maximumFractionDigits={2} />,
      formatAxis: (value) => <FormattedDigitalUnit value={value} baseUnit={SI_UNITS.MEGABYTE} maximumFractionDigits={2} />
    },
    ...Object.fromEntries(
      goalBreakdownNames.map((name) => [
        name,
        {
          renderBreakdownName: () => name,
          getPointValue: (run) => {
            const dataKey = goalBreakdownNameKeyMap[name];
            return run.data?.[dataKey] ?? null;
          },
          formatValue: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} />,
          formatAxis: (value) => <DynamicFractionDigitsValue value={value} maximumFractionDigits={2} notation="compact" />
        }
      ])
    )
  };
};

const formatRunNumber = (number) => `#${number}`;
const formatRunFullName = (number, name) => `${formatRunNumber(number)}_${name}`;

const RunsChart = ({ runs, isLoading }) => {
  const theme = useTheme();

  const { modelId } = useParams();

  const breakdownConfig = getBreakdownConfig({ runs });

  const runNumberToRunNameMap = Object.fromEntries(runs.map((run) => [run.number, run.name]));

  const getRunNameByNumber = (number) => runNumberToRunNameMap[number];

  const runsBreakdownNames = Object.keys(breakdownConfig);
  const implementedBreakdownNames = Object.entries(breakdownConfig)
    .filter(([, { isNotImplemented }]) => !isNotImplemented)
    .map(([name]) => name);

  const colorsMap = getColorsMap(runsBreakdownNames, theme.palette.chart);

  const { selectedBreakdowns, onBreakdownChange } = useApplicationBreakdown({
    modelId,
    queryParamName: BREAKDOWN_BY_QUERY_PARAMETER,
    breakdownNames: implementedBreakdownNames,
    storeId: "application_runs"
  });

  const breakdownLines = useMlBreakdownLines({
    breakdown: Object.fromEntries(runs.map((run) => [run.number, run])),
    breakdownConfig,
    selectedBreakdowns
  });

  return (
    <Stack>
      <div>
        <MlBreakdownCheckboxes
          selectedBreakdowns={selectedBreakdowns}
          colorsMap={colorsMap}
          breakdownConfig={breakdownConfig}
          onChange={onBreakdownChange}
          isLoading={isLoading}
        />
      </div>
      <div>
        <LineChart
          isLoading={isLoading}
          data={breakdownLines}
          xScale={{
            type: "linear",
            min: "auto"
          }}
          renderTooltipBody={({ slice = {} }) => {
            const { points } = slice;

            const { x: runNumber } = points[0].data;

            return (
              <div>
                <Typography fontWeight="bold" gutterBottom>
                  {formatRunFullName(runNumber, getRunNameByNumber(runNumber))}
                </Typography>
                {points.map((point) => (
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
                ))}
              </div>
            );
          }}
          colors={({ id }) => colorsMap[id]}
          style={{
            margin: CHART_MARGIN_STYLES
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
          animate={false}
          axisBottom={{
            format: (runNumber) => formatRunNumber(runNumber),
            formatString: (runNumber) => formatRunNumber(runNumber)
          }}
        />
      </div>
    </Stack>
  );
};

RunsChart.propTypes = {
  runs: PropTypes.array,
  isLoading: PropTypes.bool
};

export default RunsChart;
