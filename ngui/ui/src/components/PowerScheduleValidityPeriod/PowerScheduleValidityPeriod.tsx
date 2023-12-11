import React from "react";
import { FormattedMessage } from "react-intl";
import { intl } from "translations/react-intl-config";
import { EN_FORMAT, unixTimestampToDateTime } from "utils/datetime";

type PowerScheduleValidityPeriodProps = {
  startDate: number;
  endDate: number;
};

const stringifiedPowerScheduleValidityPeriod = ({ startDate, endDate }: PowerScheduleValidityPeriodProps) => {
  if (!endDate) {
    return `${intl.formatMessage({ id: "since" })} ${unixTimestampToDateTime(startDate, EN_FORMAT)}`;
  }

  return intl.formatMessage(
    {
      id: "value - value"
    },
    {
      value1: unixTimestampToDateTime(startDate, EN_FORMAT),
      value2: unixTimestampToDateTime(endDate, EN_FORMAT)
    }
  );
};

const PowerScheduleValidityPeriod = ({ startDate, endDate }: PowerScheduleValidityPeriodProps) => {
  console.log({
    startDate,
    endDate
  });

  if (!endDate) {
    return `${intl.formatMessage({ id: "since" })} ${unixTimestampToDateTime(startDate, EN_FORMAT)}`;
  }

  return (
    <FormattedMessage
      id="value - value"
      values={{
        value1: unixTimestampToDateTime(startDate, EN_FORMAT),
        value2: unixTimestampToDateTime(endDate, EN_FORMAT)
      }}
    />
  );
};

export { stringifiedPowerScheduleValidityPeriod };

export default PowerScheduleValidityPeriod;
