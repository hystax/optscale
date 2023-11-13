import { Grid, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { FormattedMessage } from "react-intl";
import ResourceCountBreakdownLineChart from "components/ResourceCountBreakdown/ResourceCountBreakdownLineChart";
import { isEmpty } from "utils/arrays";
import { format, secondsToMilliseconds } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import TagsBreakdownTable from "./TagsBreakdownTable";

// count key is null due to we fetch resources breakdown without specifying breakdownBy
export const BREAKDOWN_COUNT_KEY = "null";

const useLineData = (breakdown = {}) => {
  const allDates = Object.keys(breakdown);
  if (isEmpty(allDates)) {
    return [];
  }

  const getDateString = (date) => format(secondsToMilliseconds(Number(date)));

  /**
   * Optional chaining and nullish coalescing are required to prevent reading properties
   * of undefined in cases when the data has not yet been fully loaded
   *
   * -> https://gitlab.com/hystax/ngui/-/merge_requests/2865
   */
  const getResourceTypeBreakdownByDate = (date, countKey) => breakdown[date]?.[countKey] ?? {};
  const getResourceBreakdownProperty = (resourceTypeBreakdown, property) => resourceTypeBreakdown[property];

  const getResourcesCount = (date, countKey) =>
    getResourceBreakdownProperty(getResourceTypeBreakdownByDate(date, countKey), "count");

  return [
    {
      id: BREAKDOWN_COUNT_KEY,
      data: allDates.map((date) => {
        const {
          created,
          deleted_day_before: deletedDayBefore,
          id = BREAKDOWN_COUNT_KEY,
          name,
          purpose,
          type
        } = getResourceTypeBreakdownByDate(date, BREAKDOWN_COUNT_KEY);

        return {
          x: getDateString(date),
          y: getResourcesCount(date, BREAKDOWN_COUNT_KEY),
          translatedSerieId: <FormattedMessage id="count" />,
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
    }
  ];
};

const TagsBreakdown = ({
  data,
  chartData,
  appliedRange,
  selectedTag,
  updateSelectedTag,
  isLoading = false,
  isChartLoading = false
}) => {
  const theme = useTheme();

  const chartColors = { null: theme.palette.chart };

  const getChartHeader = (tag) => {
    const chartHeader = {
      null: <FormattedMessage id="untaggedResources" />,
      undefined: <FormattedMessage id="allResources" />
    };
    if (isChartLoading) {
      return <FormattedMessage id="loadingResourceData" />;
    }
    return (
      chartHeader[tag] ?? (
        <FormattedMessage id="resourcesForTag" values={{ tag, strong: (chunks) => <strong>{chunks}</strong> }} />
      )
    );
  };

  const lineData = useLineData(chartData);
  return (
    <Grid container spacing={SPACING_1}>
      <Grid item xs={12}>
        <Typography>{getChartHeader(selectedTag)}</Typography>
      </Grid>
      <Grid item xs={12}>
        <ResourceCountBreakdownLineChart
          data={lineData}
          colors={chartColors}
          isLoading={isChartLoading}
          style={{ height: 25 }}
          dataTestId="tags_breakdown_chart"
        />
      </Grid>
      <Grid item xs={12}>
        <TagsBreakdownTable
          data={data}
          isLoading={isLoading}
          appliedRange={appliedRange}
          onShowOnChartClick={updateSelectedTag}
          selectedTag={selectedTag}
        />
      </Grid>
    </Grid>
  );
};

export default TagsBreakdown;
