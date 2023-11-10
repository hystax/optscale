import { useEffect, useState } from "react";
import { Grid } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage, useIntl } from "react-intl";
import BreakdownBy from "components/ExpensesDailyBreakdownBy/BreakdownBy";
import WrapperCard from "components/WrapperCard";
import { splitIntoTwoChunks, isEmpty as isEmptyArray } from "utils/arrays";
import { getColorScale } from "utils/charts";
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

const createColorsMap = (arrayToColorize, colorScale) =>
  arrayToColorize.reduce(
    (map, key) => ({
      ...map,
      [key]: colorScale(key)
    }),
    {}
  );

const useColors = (countKeys) => {
  const theme = useTheme();

  const colorScale = getColorScale(theme.palette.chart);

  const resourceTypesColorsMap = createColorsMap(countKeys, colorScale);

  const getTableColors = () => ({ ...resourceTypesColorsMap });
  const getChartColors = () => ({
    ...resourceTypesColorsMap,
    [OTHER_LINE_NAME]: colorScale(OTHER_LINE_NAME)
  });

  return {
    tableColors: getTableColors(),
    chartColors: getChartColors()
  };
};

const useLineData = (breakdown, countKeys) => {
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
          type
        } = getResourceTypeBreakdownByDate(date, countKey);

        return {
          x: getDateString(date),
          y: getResourcesCount(date, countKey),
          translatedSerieId: countKey === "null" ? <FormattedMessage id="(not set)" /> : undefined,
          details: {
            id,
            created,
            deletedDayBefore,
            name,
            purpose,
            type
          }
        };
      })
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
        created: getOtherCreatedResourcesCountSum(date)
      }
    }))
  });

  if (!isEmptyArray(otherCountKeys)) {
    return [getOtherLine(), ...topLines];
  }

  return topLines;
};

const useChartLinesDisplaySettings = (countKeys) => {
  const [chartLinesDisplaySettings, setChartLinesDisplaySettings] = useState({});

  const updateLineDisplaySettings = (key) => {
    setChartLinesDisplaySettings((currentSettings) => ({
      ...currentSettings,
      [key]: !currentSettings[key]
    }));
  };

  const updateAllLinesDisplaySettings = (isVisible) => {
    setChartLinesDisplaySettings((currentSettings) =>
      Object.fromEntries(Object.keys(currentSettings).map((key) => [key, isVisible]))
    );
  };

  useEffect(() => {
    const showAllLinesByDefault = () => Object.fromEntries(countKeys.map((key) => [key, true]));
    setChartLinesDisplaySettings(showAllLinesByDefault());
  }, [countKeys]);

  return {
    chartLinesDisplaySettings,
    updateLineDisplaySettings,
    updateAllLinesDisplaySettings
  };
};

const ResourceCountBreakdown = ({
  countKeys,
  breakdownByValue,
  onBreakdownByChange,
  counts,
  breakdown,
  appliedRange,
  isLoading = false
}) => {
  const { chartLinesDisplaySettings, updateLineDisplaySettings, updateAllLinesDisplaySettings } =
    useChartLinesDisplaySettings(countKeys);

  const { tableColors, chartColors } = useColors(countKeys);

  const excludeHiddenResourceTypes = () => countKeys.filter((type) => chartLinesDisplaySettings[type]);

  const lineData = useLineData(breakdown, excludeHiddenResourceTypes());

  return (
    <WrapperCard>
      <Grid container spacing={SPACING_1}>
        <Grid xs={12} sx={{ display: "flex" }}>
          <BreakdownBy value={breakdownByValue} onChange={onBreakdownByChange} />
          <ResourceCountBreakdownShowWeekendSwitch />
        </Grid>
        <Grid item xs={12}>
          <ResourceCountBreakdownLineChart
            data={lineData}
            colors={chartColors}
            isLoading={isLoading}
            breakdownBy={breakdownByValue}
            dataTestId="resource_count_breakdown_chart"
          />
        </Grid>
        <Grid item xs={12}>
          <ResourceCountBreakdownTable
            counts={counts}
            colors={tableColors}
            isLoading={isLoading}
            appliedRange={appliedRange}
            onToggleResourceCountDisplay={updateLineDisplaySettings}
            onToggleAllResourceCountsDisplay={updateAllLinesDisplaySettings}
            resourceCountBreakdownChartDisplaySettings={chartLinesDisplaySettings}
            breakdownBy={breakdownByValue}
          />
        </Grid>
      </Grid>
    </WrapperCard>
  );
};

export default ResourceCountBreakdown;
