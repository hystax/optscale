import React from "react";
import { Grid, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ResourceCountBreakdownLineChart from "components/ResourceCountBreakdown/ResourceCountBreakdownLineChart";
import { isEmpty } from "utils/arrays";
import { format, secondsToMilliseconds } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";

import TagsBreakdownTable from "./TagsBreakdownTable";

// count key is null due to we fetch resources breakdown without specifying breakdownBy
const COUNT_KEY = "null";

const useLineData = (breakdown) => {
  const allDates = Object.keys(breakdown);
  if (isEmpty(allDates)) {
    return [];
  }

  const getDateString = (date) => format(secondsToMilliseconds(Number(date)));

  const getResourceTypeBreakdownByDate = (date, countKey) => breakdown[date][countKey];
  const getResourceBreakdownProperty = (resourceTypeBreakdown, property) => resourceTypeBreakdown[property];

  const getResourcesCount = (date, countKey) =>
    getResourceBreakdownProperty(getResourceTypeBreakdownByDate(date, countKey), "count");

  return [
    {
      id: COUNT_KEY,
      data: allDates.map((date) => {
        const {
          created,
          deleted_day_before: deletedDayBefore,
          id = COUNT_KEY,
          name,
          purpose,
          type
        } = getResourceTypeBreakdownByDate(date, COUNT_KEY);

        return {
          x: getDateString(date),
          y: getResourcesCount(date, COUNT_KEY),
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

TagsBreakdown.propTypes = {
  data: PropTypes.array.isRequired,
  chartData: PropTypes.object.isRequired,
  isChartLoading: PropTypes.bool,
  isLoading: PropTypes.bool,
  selectedTag: PropTypes.string,
  updateSelectedTag: PropTypes.func.isRequired,
  appliedRange: PropTypes.shape({
    startSecondsTimestamp: PropTypes.number,
    endSecondsTimestamp: PropTypes.number
  }).isRequired
};

export default TagsBreakdown;
