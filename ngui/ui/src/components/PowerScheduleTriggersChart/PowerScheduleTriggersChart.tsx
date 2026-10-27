import { useEffect, useRef, useState } from "react";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import { Box, Typography } from "@mui/material";
import Skeleton from "@mui/material/Skeleton";
import { lighten, useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import Tooltip from "components/Tooltip";
import { isEmptyArray } from "utils/arrays";
import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import {
  differenceInMinutes,
  EN_TIME_FORMAT,
  EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
  formatTimeString,
  minutesFromStartOfDay,
  parse,
} from "utils/datetime";
import { ObjectValues } from "utils/types";

type PowerAction = ObjectValues<typeof POWER_SCHEDULE_ACTIONS>;

type TimePoint = {
  time: string;
  action: PowerAction;
};

type TimeSegment = {
  segment: string;
  action: PowerAction;
  durationInMinutes: number;
};

type ChartProps = {
  triggers?: TimePoint[];
};

type PreparedData = TimeSegment[];

type PowerScheduleTriggersChartProps = {
  triggers?: TimePoint[];
  isLoading?: boolean;
};

/**
 * Ensures the schedule covers a full 24-hour period by adding start/end points if needed
 * Input: array of time triggers with actions (on/off)
 * Output: normalized array starting at 00:00 and ending at 23:59
 */
const normalizeTriggers = (triggers: TimePoint[]): TimePoint[] => {
  const fullSchedule = [...triggers];

  const lastTriggerAction = fullSchedule[fullSchedule.length - 1].action;

  // Add a trigger at midnight (00:00) if the first trigger starts later
  if (fullSchedule[0].time !== "00:00") {
    fullSchedule.unshift({ time: "00:00", action: lastTriggerAction });
  }

  // Add end of day trigger to complete the 24-hour cycle
  fullSchedule.push({ time: "23:59", action: lastTriggerAction });

  return fullSchedule;
};

const prepareSegments = (triggers: TimePoint[]): PreparedData => {
  // Sort triggers chronologically
  const sortedTriggers = triggers.toSorted((triggerA, triggerB) => {
    const timeA = parse(triggerA.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());
    const timeB = parse(triggerB.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());

    return timeA.getTime() - timeB.getTime();
  });

  const normalizedTriggers = normalizeTriggers(sortedTriggers);

  // Convert triggers into ranges with start/end times and durations
  return normalizedTriggers.slice(0, -1).map((current, index) => {
    const rangeStart = formatTimeString({
      timeString: current.time,
      timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
      parsedTimeStringFormat: EN_TIME_FORMAT,
    });
    const rangeEnd = formatTimeString({
      timeString: normalizedTriggers[index + 1].time,
      timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
      parsedTimeStringFormat: EN_TIME_FORMAT,
    });

    return {
      segment: `${rangeStart} - ${rangeEnd}`,
      action: current.action,
      durationInMinutes: differenceInMinutes(
        parse(rangeEnd, EN_TIME_FORMAT, new Date()),
        parse(rangeStart, EN_TIME_FORMAT, new Date())
      ),
    };
  });
};

const MINUTES_IN_A_DAY = 1440;
const START_TIME = "00:00";
const END_TIME = "23:59";

const BAR_HEIGHT = 40;

const TIME_MARKER_WIDTH = 1;
const TIME_MARKER_VERTICAL_PADDING = 4;
const TIME_MARKER_HEIGHT = BAR_HEIGHT + 2 * TIME_MARKER_VERTICAL_PADDING;
const TIME_LABEL_MIN_SPACING = 60; // Minimum space between time labels in pixels
const TIME_LABEL_HEIGHT = 14;
const TIME_LABEL_MARGIN_TOP = 2;

const Y_PADDING = 2;
const PADDING_TOP = TIME_MARKER_VERTICAL_PADDING + Y_PADDING;
const PADDING_BOTTOM = TIME_MARKER_VERTICAL_PADDING + TIME_LABEL_HEIGHT + Y_PADDING;

const FULL_HEIGHT = BAR_HEIGHT + PADDING_TOP + PADDING_BOTTOM + TIME_LABEL_MARGIN_TOP;

const Loader = () => <Skeleton height={FULL_HEIGHT} />;

const Chart = ({ triggers = [] }: ChartProps) => {
  const theme = useTheme();

  const chartRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState<number | null>(null);

  const segments = isEmptyArray(triggers) ? [] : prepareSegments(triggers);

  useEffect(() => {
    if (!chartRef.current) {
      return;
    }

    // Get initial width
    const initialWidth = chartRef.current.getBoundingClientRect().width;
    if (initialWidth > 0) {
      setChartWidth(initialWidth);
    }

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        if (width > 0) {
          setChartWidth(width);
        }
      }
    });

    resizeObserver.observe(chartRef.current);

    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  const formattedStartTime = formatTimeString({
    timeString: START_TIME,
    timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
    parsedTimeStringFormat: EN_TIME_FORMAT,
  });

  const formattedEndTime = formatTimeString({
    timeString: END_TIME,
    timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
    parsedTimeStringFormat: EN_TIME_FORMAT,
  });

  // Calculate which labels should be visible
  const calculateVisibleLabels = (triggersList: TimePoint[]) => {
    // If we don't have a valid width yet, show no labels
    if (!chartWidth) {
      return triggersList.map(() => false);
    }

    let lastVisiblePixelPosition = -TIME_LABEL_MIN_SPACING; // Start before the chart

    return triggersList.map((_, index) => {
      const currentMinutes = minutesFromStartOfDay(triggersList[index].time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM);
      const currentPixelPosition = (currentMinutes / MINUTES_IN_A_DAY) * chartWidth;

      // If this label would overlap with the last visible label, skip it
      if (currentPixelPosition - lastVisiblePixelPosition < TIME_LABEL_MIN_SPACING) {
        return false;
      }

      // This label has enough space, mark it as visible
      lastVisiblePixelPosition = currentPixelPosition;
      return true;
    });
  };

  const visibleLabels = calculateVisibleLabels(triggers);

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        pt: `${PADDING_TOP}px`,
        pb: `${PADDING_BOTTOM}px`,
        height: `${FULL_HEIGHT}px`,
      }}
    >
      <Box position="relative">
        {/* Left time label */}
        <Box
          sx={{
            position: "absolute",
            left: 0,
            top: "50%",
            transform: "translateY(-50%)",
            fontSize: "12px",
            color: theme.palette.text.primary,
          }}
        >
          {formattedStartTime}
        </Box>
        {/* Right time label */}
        <Box
          sx={{
            position: "absolute",
            right: 0,
            top: "50%",
            transform: "translateY(-50%)",
            fontSize: "12px",
            color: theme.palette.text.primary,
          }}
        >
          {formattedEndTime}
        </Box>
        <Box
          ref={chartRef}
          sx={{
            mx: "60px",
            height: `${BAR_HEIGHT}px`,
            display: "flex",
            position: "relative",
          }}
        >
          {/* Power schedule segments */}
          {segments.map(({ segment, action, durationInMinutes }) => {
            const isOn = action === POWER_SCHEDULE_ACTIONS.POWER_ON;
            const widthPercentage = (durationInMinutes / MINUTES_IN_A_DAY) * 100;

            return (
              <Box
                key={segment}
                sx={{
                  width: `${widthPercentage}%`,
                  height: "100%",
                  bgcolor: isOn ? lighten(theme.palette.success.main, 0.8) : lighten(theme.palette.error.main, 0.8),
                }}
              />
            );
          })}

          {/* Trigger markers with integrated labels */}
          {triggers.map((trigger, index) => {
            const minutes = minutesFromStartOfDay(trigger.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM);
            const position = (minutes / MINUTES_IN_A_DAY) * 100;
            const formattedTime = formatTimeString({
              timeString: trigger.time,
              timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
              parsedTimeStringFormat: EN_TIME_FORMAT,
            });

            const isOn = trigger.action === POWER_SCHEDULE_ACTIONS.POWER_ON;

            return (
              <Tooltip
                placement="top"
                key={`marker-${trigger.time}`}
                title={
                  <Box>
                    <KeyValueLabel keyMessageId="time" value={formattedTime} />
                    <Box display="flex" alignItems="center">
                      <Typography>
                        <FormattedMessage id="state" />
                        :&nbsp;{" "}
                      </Typography>
                      <IconLabel
                        icon={<PowerSettingsNewOutlinedIcon fontSize="small" color={isOn ? "success" : "error"} />}
                        label={
                          <Typography variant="body2" fontWeight="bold">
                            <FormattedMessage id={isOn ? "on" : "off"} />
                          </Typography>
                        }
                      />
                    </Box>
                  </Box>
                }
              >
                <Box
                  sx={{
                    position: "absolute",
                    left: `${position}%`,
                    width: `${TIME_MARKER_WIDTH}px`,
                    height: `${TIME_MARKER_HEIGHT}px`,
                    top: `-${TIME_MARKER_VERTICAL_PADDING}px`,
                    backgroundColor: theme.palette.common.black,
                    transform: "translateX(-50%)",
                    transition: "all 0.2s",
                    "&::after": {
                      content: visibleLabels[index] ? `"${formattedTime}"` : '""',
                      position: "absolute",
                      top: "100%",
                      left: "50%",
                      transform: "translateX(-50%)",
                      fontSize: "12px",
                      color: theme.palette.text.primary,
                      whiteSpace: "nowrap",
                      borderRadius: `${TIME_LABEL_MARGIN_TOP}px`,
                      transition: "all 0.2s",
                      marginTop: "2px",
                      padding: "0px 4px",
                      opacity: visibleLabels[index] ? 1 : 0,
                    },
                    "&:hover": {
                      backgroundColor: theme.palette.primary.main,
                      width: `${TIME_MARKER_WIDTH + 1}px`,
                      "&::after": {
                        color: theme.palette.text.primary,
                        backgroundColor: theme.palette.action.hover,
                      },
                    },
                  }}
                />
              </Tooltip>
            );
          })}
        </Box>
      </Box>
    </Box>
  );
};

const PowerScheduleTriggersChart = ({ triggers = [], isLoading = false }: PowerScheduleTriggersChartProps) =>
  isLoading ? <Loader /> : <Chart triggers={triggers} />;

export default PowerScheduleTriggersChart;
