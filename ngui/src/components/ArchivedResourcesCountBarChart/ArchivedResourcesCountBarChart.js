import React, { useState } from "react";
import { Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import KeyValueLabel from "components/KeyValueLabel";
import { getRecommendationInstanceByType } from "components/RelevantRecommendations";
import { ARCHIVATION_REASON_MESSAGE_ID, BE_TO_FE_MAP_RECOMMENDATION_TYPES } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC, getEndOfDayInUTCinSeconds, secondsToMilliseconds } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import useStyles from "./ArchivedResourcesCountBarChart.styles";

const NOT_SELECTED = undefined;

const ChartTooltip = ({ sectionData }) => {
  const { classes } = useStyles();

  return (
    <div className={classes.tooltip}>
      {Object.entries(sectionData.data.breakdown).map(([recommendationType, counts]) => {
        const recommendationMessageId = getRecommendationInstanceByType(
          BE_TO_FE_MAP_RECOMMENDATION_TYPES[recommendationType]
        ).messageId;

        return (
          <div key={recommendationType}>
            <Typography variant="body2">
              <FormattedMessage id={recommendationMessageId} />
            </Typography>
            {Object.entries(counts).map(([archivationReason, count]) => (
              <KeyValueLabel
                key={archivationReason}
                variant="caption"
                messageId={ARCHIVATION_REASON_MESSAGE_ID[archivationReason]}
                value={count}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
};

const getChartData = (breakdown) => {
  if (Object.values(breakdown).every(isEmptyObject)) {
    return [];
  }

  const chartData = Object.entries(breakdown).map(([date, dateBreakdown]) => ({
    date: formatUTC(date, EN_FORMAT_SHORT_YEAR),
    dateTimestamp: Number(date),
    breakdown: dateBreakdown,
    count: Object.values(dateBreakdown).reduce(
      (dailyRecommendationsSum, dailyRecommendationsCountBreakdown) =>
        dailyRecommendationsSum +
        Object.values(dailyRecommendationsCountBreakdown).reduce(
          (sum, archivedRecommendationsCount) => sum + archivedRecommendationsCount,
          0
        ),
      0
    )
  }));

  return chartData;
};

const ArchivedResourcesCountBarChart = ({ onSelect, breakdown }) => {
  const [selected, setSelected] = useState(NOT_SELECTED);

  const onClick = ({ data }, barName) => {
    const { selectionState, dateRange } =
      barName === selected
        ? {
            selectionState: NOT_SELECTED,
            dateRange: null
          }
        : {
            selectionState: barName,
            dateRange: {
              startDate: data.dateTimestamp,
              endDate: getEndOfDayInUTCinSeconds(secondsToMilliseconds(data.dateTimestamp))
            }
          };

    setSelected(selectionState);
    onSelect(dateRange);
  };

  return (
    <CanvasBarChart
      indexBy="date"
      data={getChartData(breakdown)}
      keys={["count"]}
      selectedBar={selected}
      onClick={onClick}
      renderTooltipBody={(sectionData) => <ChartTooltip sectionData={sectionData} />}
    />
  );
};

ArchivedResourcesCountBarChart.propTypes = {
  onSelect: PropTypes.func.isRequired,
  breakdown: PropTypes.object
};

export default ArchivedResourcesCountBarChart;
