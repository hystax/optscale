import { useEffect, useMemo, useState } from "react";
import { Box, Stack } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { useIntl } from "react-intl";
import ChartLegendToggle from "components/ChartLegendToggle";
import BreakdownBy from "components/ExpensesDailyBreakdownBy/BreakdownBy";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { WITH_LEGEND_QUERY_PARAMETER_NAME } from "urls";
import { splitIntoTwoChunks, isEmptyArray } from "utils/arrays";
import { getColorsMap } from "utils/charts";
import { EMPTY_BREAKDOWN_KEY } from "utils/constants";
import { format, secondsToMilliseconds } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import ResourceCountBreakdownLineChart from "./ResourceCountBreakdownLineChart";
import ResourceCountBreakdownShowWeekendSwitch from "./ResourceCountBreakdownShowWeekendSwitch";
import ResourceCountBreakdownTable from "./ResourceCountBreakdownTable";

const OTHER_LINE_NAME = "otherLine";

const useTranslatedOtherLineName = () => {
  const intl = useIntl();

  return intl.formatMessage({ id: "other" });
};

const useColors = (countKeys) => {
  const theme = useTheme();

  const chartPalette = theme.palette.chart;

  return {
    tableColors: getColorsMap(countKeys, chartPalette),
    chartColors: getColorsMap([...countKeys, OTHER_LINE_NAME], chartPalette),
  };
};

const useLineData = (breakdown, countKeys) => {
  const intl = useIntl();

  const [topCountKeys, otherCountKeys] = splitIntoTwoChunks(countKeys, 10);

  const allDates = Object.keys(breakdown);

  const getDateString = (date) => format(secondsToMilliseconds(Number(date)));

  const getResourceTypeBreakdownByDate = (date, countKey) => breakdown[date][countKey];
  const getResourceBreakdownProperty = (resourceTypeBreakdown, property) => resourceTypeBreakdown[property];

  const getResourcesCount = (date, countKey) =>
    getResourceBreakdownProperty(getResourceTypeBreakdownByDate(date, countKey), "count");
  const getDeletedDayBeforeResourcesCount = (date, countKey) =>
    getResourceBreakdownProperty(getResourceTypeBreakdownByDate(date, countKey), "deleted_day_before");
  const getCreatedResourcesCount = (date, countKey) =>
    getResourceBreakdownProperty(getResourceTypeBreakdownByDate(date, countKey), "created");

  const topLines = topCountKeys
    .map((countKey) => ({
      id: countKey,
      data: allDates.map((date) => {
        const {
          created,
          deleted_day_before: deletedDayBefore,
          id = countKey,
          name,
          purpose,
          type,
        } = getResourceTypeBreakdownByDate(date, countKey);

        return {
          x: getDateString(date),
          y: getResourcesCount(date, countKey),
          translatedSerieId: countKey === EMPTY_BREAKDOWN_KEY.NULL ? intl.formatMessage({ id: "(not set)" }) : undefined,
          details: {
            id,
            created,
            deletedDayBefore,
            name,
            purpose,
            type,
          },
        };
      }),
    }))
    .reverse();

  const translatedOtherLineName = useTranslatedOtherLineName();

  const getOtherResourcesCountSum = (date) =>
    otherCountKeys.reduce((sum, countKey) => sum + getResourcesCount(date, countKey), 0);
  const getOtherDeletedDayBeforeResourcesCountSum = (date) =>
    otherCountKeys.reduce((sum, countKey) => sum + getDeletedDayBeforeResourcesCount(date, countKey), 0);
  const getOtherCreatedResourcesCountSum = (date) =>
    otherCountKeys.reduce((sum, countKey) => sum + getCreatedResourcesCount(date, countKey), 0);

  const getOtherLine = () => ({
    id: OTHER_LINE_NAME,
    data: allDates.map((date) => ({
      x: getDateString(date),
      y: getOtherResourcesCountSum(date),
      translatedSerieId: translatedOtherLineName,
      details: {
        deletedDayBefore: getOtherDeletedDayBeforeResourcesCountSum(date),
        created: getOtherCreatedResourcesCountSum(date),
      },
    })),
  });

  if (!isEmptyArray(otherCountKeys)) {
    return [getOtherLine(), ...topLines];
  }

  return topLines;
};

const getCountKeysSortedByAverageInDescendingOrder = (counts) =>
  Object.entries(counts)
    .sort(([, { average: averageA }], [, { average: averageB }]) => averageB - averageA)
    .map(([name]) => name);

const ResourceCountBreakdown = ({
  resourceCountBreakdown,
  breakdownByValue,
  onBreakdownByChange,
  isLoading = false,
  showTable = false,
}) => {
  const { breakdown = {}, start_date: startDate = 0, end_date: endDate = 0, counts = {} } = resourceCountBreakdown;

  const appliedRange = {
    startSecondsTimestamp: startDate,
    endSecondsTimestamp: endDate,
  };

  const countKeys = useMemo(() => getCountKeysSortedByAverageInDescendingOrder(counts), [counts]);

  const [hiddenLines, setHiddenLines] = useState<string[]>([]);

  useEffect(() => {
    setHiddenLines([]);
  }, [breakdown]);

  const { tableColors, chartColors } = useColors(countKeys);

  const lineData = useLineData(
    breakdown,
    countKeys.filter((key) => !hiddenLines.includes(key))
  );

  const [withLegend, setWithLegend] = useSyncQueryParamWithState({
    queryParamName: WITH_LEGEND_QUERY_PARAMETER_NAME,
    possibleStates: [true, false],
    defaultValue: true,
  });

  return (
    <Stack spacing={SPACING_1}>
      <Box display="flex">
        <BreakdownBy
          value={breakdownByValue}
          onChange={(newBreakdown) => {
            setHiddenLines([]);
            onBreakdownByChange(newBreakdown);
          }}
        />
        <ResourceCountBreakdownShowWeekendSwitch />
        <ChartLegendToggle checked={withLegend} onChange={setWithLegend} />
      </Box>
      <Box>
        <ResourceCountBreakdownLineChart
          data={lineData}
          colors={chartColors}
          isLoading={isLoading}
          breakdownBy={breakdownByValue}
          withLegend={withLegend}
          dataTestId="resource_count_breakdown_chart"
        />
      </Box>
      {showTable && (
        <Box>
          <ResourceCountBreakdownTable
            counts={counts}
            colors={tableColors}
            isLoading={isLoading}
            appliedRange={appliedRange}
            onToggleResourceCountDisplay={(key) => {
              setHiddenLines((currentHiddenLines) =>
                currentHiddenLines.includes(key)
                  ? currentHiddenLines.filter((lineKey) => lineKey !== key)
                  : [...currentHiddenLines, key]
              );
            }}
            onToggleAllResourceCountsDisplay={() => {
              setHiddenLines((currentHiddenLines) => {
                if (currentHiddenLines.length === countKeys.length) {
                  return [];
                }
                return countKeys;
              });
            }}
            hiddenLines={hiddenLines}
            breakdownBy={breakdownByValue}
          />
        </Box>
      )}
    </Stack>
  );
};

export default ResourceCountBreakdown;
