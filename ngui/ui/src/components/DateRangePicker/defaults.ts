// TODO - see todo on optional time conversion in datetime util
import { v4 as uuidv4 } from "uuid";
import {
  startOfMonth,
  endOfMonth,
  subDays,
  subMonths,
  endOfDay,
  startOfDay,
  millisecondsToSeconds,
  performDateTimeFunction
} from "utils/datetime";

export const getCustomRange = (args) => ({
  key: uuidv4(),
  ...args
});

const getBasicRangesSetRawMS = (isUtc) => {
  const date = +new Date();

  const startOfToday = performDateTimeFunction(startOfDay, isUtc, date);
  const endOfToday = performDateTimeFunction(endOfDay, isUtc, date);

  const monthSubstracted = performDateTimeFunction(subMonths, isUtc, date, 1);
  return [
    {
      messageId: "thisMonth",
      startDate: performDateTimeFunction(startOfMonth, isUtc, date),
      endDate: endOfToday,
      dataTestId: "btn_this_month"
    },
    {
      messageId: "lastMonth",
      startDate: performDateTimeFunction(startOfMonth, isUtc, monthSubstracted),
      endDate: performDateTimeFunction(endOfMonth, isUtc, monthSubstracted),
      dataTestId: "btn_last_month"
    },
    {
      messageId: "last7Days",
      startDate: performDateTimeFunction(subDays, isUtc, startOfToday, 6),
      endDate: endOfToday,
      dataTestId: "btn_last_7_days"
    },
    {
      messageId: "last30Days",
      startDate: performDateTimeFunction(subDays, isUtc, startOfToday, 29),
      endDate: endOfToday,
      dataTestId: "btn_last_30_days"
    }
  ];
};

export const getBasicRangesSet = (isUtc = true) =>
  getBasicRangesSetRawMS(isUtc)
    .map(({ startDate, endDate, ...rest }) => ({
      startDate: millisecondsToSeconds(startDate),
      endDate: millisecondsToSeconds(endDate),
      ...rest
    }))
    .map((range) => getCustomRange(range));
