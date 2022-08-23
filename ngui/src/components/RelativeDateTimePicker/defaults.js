import { subDays, subMonths, subHours, subWeeks } from "date-fns";
import { v4 as uuidv4 } from "uuid";
import { performDateTimeFunction } from "utils/datetime";

export const getCustomRange = (args) => ({
  key: uuidv4(),
  ...args
});

const getBasicRangesSetRawMS = (isUtc) => [
  {
    messageId: "xHours",
    messageValues: { x: 1 },
    startDateFn: (endDate) => performDateTimeFunction(subHours, isUtc, endDate, 1),
    dataTestId: "btn_one_hour"
  },
  {
    messageId: "xHours",
    messageValues: { x: 6 },
    startDateFn: (endDate) => performDateTimeFunction(subHours, isUtc, endDate, 6),
    dataTestId: "btn_six_hours"
  },
  {
    messageId: "xDays",
    messageValues: { x: 1 },
    startDateFn: (endDate) => performDateTimeFunction(subDays, isUtc, endDate, 1),
    dataTestId: "btn_one_day"
  },
  {
    messageId: "xWeeks",
    messageValues: { x: 1 },
    startDateFn: (endDate) => performDateTimeFunction(subWeeks, isUtc, endDate, 1),
    dataTestId: "btn_one_week"
  },
  {
    messageId: "xMonth",
    messageValues: { x: 1 },
    startDateFn: (endDate) => performDateTimeFunction(subMonths, isUtc, endDate, 1),
    dataTestId: "btn_one_month"
  }
];

export const getBasicRelativeRangesSet = (isUtc = true) => getBasicRangesSetRawMS(isUtc).map((range) => getCustomRange(range));
