import { useState } from "react";
import { Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CanvasBarChart from "components/CanvasBarChart";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { useAllRecommendations } from "hooks/useAllRecommendations";
import { ARCHIVATION_REASON_MESSAGE_ID } from "utils/constants";
import { EN_FORMAT_SHORT_YEAR, formatUTC, getEndOfDayInUTCinSeconds, secondsToMilliseconds } from "utils/datetime";
import { isEmpty as isEmptyObject } from "utils/objects";
import useStyles from "./ArchivedResourcesCountBarChart.styles";

const NOT_SELECTED = undefined;

const ChartTooltip = ({ sectionData }) => {
  const { classes } = useStyles();

  const allRecommendations = useAllRecommendations();

  return (
    <div className={classes.tooltip}>
      {Object.entries(sectionData.data.breakdown).map(([recommendationType, counts]) => {
        const recommendationMessageId = new allRecommendations[recommendationType]({}, "active").title;

        return (
          <div key={recommendationType}>
            <Typography variant="body2">
              <FormattedMessage id={recommendationMessageId} />
            </Typography>
            <Stack>
              {Object.entries(counts).map(([archivationReason, count]) => (
                <KeyValueLabel
                  key={archivationReason}
                  variant="caption"
                  keyMessageId={ARCHIVATION_REASON_MESSAGE_ID[archivationReason]}
                  value={count}
                />
              ))}
            </Stack>
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
      dataTestId="archived_recommendations_chart"
      indexBy="date"
      data={getChartData(breakdown)}
      keys={["count"]}
      selectedBar={selected}
      onClick={onClick}
      renderTooltipBody={(sectionData) => <ChartTooltip sectionData={sectionData} />}
    />
  );
};

export default ArchivedResourcesCountBarChart;
