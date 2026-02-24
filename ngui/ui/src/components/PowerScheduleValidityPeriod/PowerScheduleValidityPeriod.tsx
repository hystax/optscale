import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";
import { Box, SvgIconProps } from "@mui/material";
import { FormattedMessage } from "react-intl";
import QuestionMark from "components/QuestionMark";
import { intl } from "translations/react-intl-config";
import { EN_FORMAT, unixTimestampToDateTime } from "utils/datetime";
import { isPowerScheduleExpired } from "utils/poweSchedules";

type PowerScheduleValidityPeriodProps = {
  startDate: number;
  endDate: number;
  iconFontSize?: SvgIconProps["fontSize"];
};

const stringifiedPowerScheduleValidityPeriod = ({ startDate, endDate }: PowerScheduleValidityPeriodProps) => {
  if (!endDate) {
    return `${intl.formatMessage({ id: "since" })} ${unixTimestampToDateTime(startDate, EN_FORMAT)}`;
  }

  return intl.formatMessage(
    {
      id: "value - value",
    },
    {
      value1: unixTimestampToDateTime(startDate, EN_FORMAT),
      value2: unixTimestampToDateTime(endDate, EN_FORMAT),
    }
  );
};

const PowerScheduleValidityPeriod = ({ startDate, endDate, iconFontSize = "medium" }: PowerScheduleValidityPeriodProps) => {
  if (!endDate) {
    return `${intl.formatMessage({ id: "since" })} ${unixTimestampToDateTime(startDate, EN_FORMAT)}`;
  }

  return (
    <Box display="flex" alignItems="center">
      <FormattedMessage
        id="value - value"
        values={{
          value1: unixTimestampToDateTime(startDate, EN_FORMAT),
          value2: unixTimestampToDateTime(endDate, EN_FORMAT),
        }}
      />
      {isPowerScheduleExpired(endDate) && (
        <QuestionMark
          Icon={WarningAmberOutlinedIcon}
          messageId="powerScheduleExpired"
          color="warning"
          fontSize={iconFontSize}
        />
      )}
    </Box>
  );
};

export { stringifiedPowerScheduleValidityPeriod };

export default PowerScheduleValidityPeriod;
