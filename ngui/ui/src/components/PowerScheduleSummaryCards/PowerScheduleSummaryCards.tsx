import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Box } from "@mui/material";
import { FormattedMessage } from "react-intl";
import IntervalTimeAgo from "components/IntervalTimeAgo";
import PowerScheduleValidityPeriod from "components/PowerScheduleValidityPeriod";
import QuestionMark from "components/QuestionMark";
import SummaryGrid from "components/SummaryGrid";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { isPowerScheduleExpired } from "utils/poweSchedules";

type PowerScheduleSummaryCardsProps = {
  timeZone: string;
  startDate: number;
  endDate: number;
  lastRun: number;
  lastRunError: string;
  resourcesOnSchedule: number;
  isLoading?: boolean;
};

const PowerScheduleSummaryCards = ({
  timeZone,
  startDate,
  endDate,
  lastRun,
  lastRunError,
  resourcesOnSchedule,
  isLoading = false,
}: PowerScheduleSummaryCardsProps) => (
  <SummaryGrid
    summaryData={[
      {
        key: "lastExecution",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => {
          if (lastRun === 0) {
            return <FormattedMessage id="never" />;
          }

          if (lastRunError) {
            return (
              <Box display="flex" alignItems="center">
                <IntervalTimeAgo secondsTimestamp={lastRun} precision={1} />
                <QuestionMark color="error" tooltipText={lastRunError} Icon={ErrorOutlineOutlinedIcon} />
              </Box>
            );
          }

          return <IntervalTimeAgo secondsTimestamp={lastRun} precision={1} />;
        },
        captionMessageId: "lastExecution",
        color: lastRunError ? "error" : "primary",
        dataTestIds: {
          cardTestId: "card_last_execution_time",
        },
        isLoading,
        renderCondition: () => lastRun !== undefined || lastRunError !== undefined,
      },
      {
        key: "resourcesOnSchedule",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => resourcesOnSchedule,
        captionMessageId: "resourcesOnSchedule",
        dataTestIds: {
          cardTestId: "card_resources_on_schedule",
        },
        isLoading,
      },
      {
        key: "timeZone",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => timeZone,
        captionMessageId: "timeZone",
        dataTestIds: {
          cardTestId: "card_time_zone",
        },
        isLoading,
      },
      {
        key: "validityPeriod",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => <PowerScheduleValidityPeriod startDate={startDate} endDate={endDate} />,
        captionMessageId: "validityPeriod",
        dataTestIds: {
          cardTestId: "card_time_zone",
        },
        color: isPowerScheduleExpired(endDate) ? "warning" : "primary",
        isLoading,
        renderCondition: () => !!startDate || !!endDate,
      },
    ]}
  />
);

export default PowerScheduleSummaryCards;
