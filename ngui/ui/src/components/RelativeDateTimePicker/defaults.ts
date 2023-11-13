import { subDays, subMonths, subHours, subWeeks } from "date-fns";
import { millisecondsToSeconds, performDateTimeFunction, getCurrentUTCTimeInSec, getCurrentTimeInMsec } from "utils/datetime";

const getRelativePeriodItem = ({ id, messageId, xCount, fn, dataTestId, isUtc = true }) => ({
  id,
  messageId,
  messageValues: { x: xCount },
  startDateFn: () => millisecondsToSeconds(performDateTimeFunction(fn, isUtc, getCurrentTimeInMsec(), xCount)),
  endDateFn: () => getCurrentUTCTimeInSec(),
  dataTestId
});

const RELATIVE_PERIODS = Object.freeze({
  ALL: "all",
  ONE_HOUR: "oneHour",
  SIX_HOURS: "sixHours",
  ONE_DAY: "oneDay",
  ONE_WEEK: "oneWeek",
  TWO_WEEKS: "twoWeeks",
  ONE_MONTH: "oneMonth"
});

const all = getRelativePeriodItem({
  id: RELATIVE_PERIODS.ALL,
  messageId: "all",
  dataTestId: "btn_all"
});
const oneHour = getRelativePeriodItem({
  id: RELATIVE_PERIODS.ONE_HOUR,
  messageId: "xHours",
  xCount: 1,
  fn: subHours,
  dataTestId: "btn_one_hour"
});
const sixHours = getRelativePeriodItem({
  id: RELATIVE_PERIODS.SIX_HOURS,
  messageId: "xHours",
  xCount: 6,
  fn: subHours,
  dataTestId: "btn_six_hours"
});
const oneDay = getRelativePeriodItem({
  id: RELATIVE_PERIODS.ONE_DAY,
  messageId: "xDays",
  xCount: 1,
  fn: subDays,
  dataTestId: "btn_one_day"
});
const oneWeek = getRelativePeriodItem({
  id: RELATIVE_PERIODS.ONE_WEEK,
  messageId: "xWeeks",
  xCount: 1,
  fn: subWeeks,
  dataTestId: "btn_one_week"
});
const twoWeeks = getRelativePeriodItem({
  id: RELATIVE_PERIODS.TWO_WEEKS,
  messageId: "xWeeks",
  xCount: 2,
  fn: subWeeks,
  dataTestId: "btn_two_weeks"
});
const oneMonth = getRelativePeriodItem({
  id: RELATIVE_PERIODS.ONE_MONTH,
  messageId: "xMonth",
  xCount: 1,
  fn: subMonths,
  dataTestId: "btn_one_month"
});

export const k8sRightsizingRelativeDates = [oneHour, sixHours, oneDay, oneWeek, oneMonth];
export const mlExecutorsRelativeDates = [all, oneDay, oneWeek, twoWeeks, oneMonth];
