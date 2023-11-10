/* eslint-disable import/no-duplicates */
import {
  addDays as addDaysFNS,
  addMonths,
  addHours,
  addYears,
  differenceInCalendarMonths,
  getDate,
  subDays,
  isAfter,
  isBefore,
  isEqual,
  isValid,
  startOfDay,
  formatDistanceStrict,
  getTime,
  getUnixTime,
  parseISO,
  format as formatFNS,
  getMonth,
  setMonth,
  getYear,
  getHours,
  getMinutes,
  setMinutes,
  setHours,
  setYear,
  endOfDay,
  subMinutes,
  addMinutes,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  subMonths,
  isPast,
  isToday,
  isSameDay,
  isWithinInterval,
  isSameMonth,
  min,
  max,
  millisecondsToSeconds,
  secondsToMilliseconds,
  secondsToHours,
  endOfYear,
  startOfYear,
  differenceInHours,
  areIntervalsOverlapping,
  roundToNearestMinutes
} from "date-fns";

import { enUS } from "date-fns/locale";
import { objectMap } from "./objects";

/**
 * @typedef {Object} DateRange
 * @property {number} startDate - start date timestamp in seconds
 * @property {number} endDate - end date timestamp in seconds
 */

const MILLISECONDS_IN_SECOND = 1000;
const MILLISECONDS_IN_MINUTE = 60 * MILLISECONDS_IN_SECOND;
const MILLISECONDS_IN_HOUR = 60 * MILLISECONDS_IN_MINUTE;
const MILLISECONDS_IN_DAY = 24 * MILLISECONDS_IN_HOUR;
const MILLISECONDS_IN_WEEK = 7 * MILLISECONDS_IN_DAY;

const SECOND = 1;
export const SECONDS_IN_MINUTE = 60 * SECOND;
const SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE;

export const MAX_UTC_DATE_TIMESTAMP = +new Date("01/01/2071 GMT+0");

export const SHORT_MONTHS = [...Array(12).keys()].map((i) => enUS.localize.month(i, { width: "abbreviated" }));

export const SHORT_WEEK_DAYS = [...Array(7).keys()].map((i) => enUS.localize.day(i, { width: "short" }));

export const ABBREVIATED_WEEK_DAYS = [...Array(7).keys()].map((i) => enUS.localize.day(i, { width: "abbreviated" }));

export const EN_FULL_FORMAT = "MM/dd/yyyy hh:mm a";
export const EN_FORMAT = "MM/dd/yyyy";
export const EN_TIME_FORMAT_HH_MM = "hh:mm";
export const EN_TIME_FORMAT_A = "a";
export const EN_TIME_FORMAT = "hh:mm a";
export const EN_FORMAT_SHORT_YEAR = "MM/dd/yy";
export const FORMAT_MMM_DD_YYYY = "MMM dd, yyyy";
export const FORMAT_MMM_DD = "MMM dd";
export const FORMAT_MMM_YYYY = "MMM, yyyy";
export const EN_PICKER_FORMAT = "LLL dd, yyyy";
export const FORMAT_YYYY_MM_DD = "yyyyMMdd";
export const FORMAT_YYYY = "yyyy";

const getDateTimezoneOffset = (date) => new Date(date).getTimezoneOffset();
export const HOURS_PER_DAY = 24;

export const AMOUNT_30_MINUTES = 30;
export const AMOUNT_15_MINUTES = 15;
export const INTERVAL_ENVIRONMENT = AMOUNT_30_MINUTES;
export const INTERVAL_TTL_CONSTRAINT = AMOUNT_15_MINUTES;

export const getNYearsFromToday = (n) => +addYears(new Date(), n);

// if we should show time in UTC, BUT problems with DST https://github.com/date-fns/date-fns/issues/1401#issuecomment-621897094
export const moveDateToUTC = (date) => {
  // todo: rename everywhere both functions
  // for GMT+3 its -180, so adding offset
  const timezoneOffset = getDateTimezoneOffset(date);
  return getTime(addMinutes(date, timezoneOffset));
};

export const moveDateFromUTC = (date) => {
  // for GMT+3 its -180, so substracting offset
  const timezoneOffset = getDateTimezoneOffset(date);
  return getTime(subMinutes(date, timezoneOffset));
};

export const performDateTimeFunction = (...args) => {
  const [fn, isUtc, date, ...rest] = args;
  if (!isUtc) return +fn(date, ...rest);

  return moveDateFromUTC(fn(moveDateToUTC(date), ...rest));
};

export const getMinPickerDateSec = (isUtc) =>
  millisecondsToSeconds(isUtc ? Date.UTC(2020, 0, 1, 0, 0, 0, 0) : new Date(2020, 0, 1, 0, 0, 0, 0));
export const getMaxPickerDateSec = (isUtc) => millisecondsToSeconds(performDateTimeFunction(endOfDay, isUtc, new Date()));
export const getMaxPickerDateMsec = (isUtc) => performDateTimeFunction(endOfDay, isUtc, new Date());

export const formatUTC = (timestamp, dateFormat = EN_FORMAT) =>
  formatFNS(moveDateToUTC(secondsToMilliseconds(timestamp)), dateFormat);

/**
 * Returns the month short name of the specified date according to universal time (in international 3-letter format)
 * Note: formatFNS returns timestamp formatted as local (adding timezone difference).
 * Due to timestamp is already in utc, we need to add difference with moveDateToUTC, which will be removed by formatFNS
 * @param { number} timestamp - timestamp in seconds
 *
 * @returns {String} name of the month
 */
export const getUTCShortMonthFromTimestamp = (timestamp) => formatUTC(timestamp, "MMM");

/**
 * Return the formatted date string in the given format.
 *
 * @param date	Date | Number	- the original date
 * @param dateFormat	String - the string of tokens, "MM/dd/yyyy" by default
 * @returns { String } the formatted date string
 */
export const format = (date, dateFormat = EN_FORMAT) => formatFNS(date, dateFormat);

/**
 * Return the formatted date string in the given format from ISO string
 * Note: parseISO return local date object, so formatFNS works fine here without any thinking about timezones
 * @param string	- the original date in ISO format
 * @param dateFormat	String - the string of tokens, "MM/dd/yyyy" by default
 * @returns { String } the formatted date string
 */
export const formatISO = (string, dateFormat = EN_FORMAT) => formatFNS(parseISO(string), dateFormat);

/**
 * Get a date/time string from a unix timestamp
 *
 * @param { number } timestamp Unix timestamp
 *
 * @returns string
 */
// TODO: rename to formatUTC
export const unixTimestampToDateTime = formatUTC;

/**
 * Get a seconds timestamp from a date/time object
 *
 * @param dateTime date/time object
 *
 * @returns { number } seconds timestamp
 */
// TODO: maybe rename to dateObjectToSecondsTimestamp
export const datetimeToUnix = (dateTime) => getUnixTime(dateTime);

export const getCurrentTimeInMsec = () => getTime(new Date());

export const getCurrentUTCTimeInSec = () => millisecondsToSeconds(getCurrentTimeInMsec());

// addDays from date-fns, but returns ms
export const addDays = (date, amount) => getTime(addDaysFNS(date, amount));

// Return the distance between the given timestamp and current timestamp in words.
export const getTimeDistance = (timestampInSeconds) => {
  const currentTime = getCurrentTimeInMsec();
  return formatDistanceStrict(secondsToMilliseconds(timestampInSeconds), currentTime);
};

export const getStartOfDayInUTCinSeconds = (date) => millisecondsToSeconds(performDateTimeFunction(startOfDay, true, date));
export const getEndOfDayInUTCinSeconds = (date) => millisecondsToSeconds(performDateTimeFunction(endOfDay, true, date));

export const getStartOfTodayInUTCinSeconds = () => getStartOfDayInUTCinSeconds(new Date());
export const getEndOfTodayInUTCinSeconds = () => getEndOfDayInUTCinSeconds(new Date());

export const addDaysToTimestamp = (timestamp, days) => millisecondsToSeconds(+addDays(secondsToMilliseconds(timestamp), days));
/**
 * Get 'lastWeekStart' and 'lastWeekEnd' age dates
 * @returns {Object} start of the last week (Date object) and end of the last week (Date objects)
 */
export const getLastWeekRange = (isUtc = true) => {
  const today = new Date();
  const sevenDaysAgo = subDays(today, 7);
  const lastWeekStart = performDateTimeFunction(startOfWeek, isUtc, sevenDaysAgo);
  const lastWeekEnd = performDateTimeFunction(endOfWeek, isUtc, sevenDaysAgo);
  return objectMap(
    {
      lastWeekStart,
      lastWeekEnd
    },
    millisecondsToSeconds
  );
};

/**
 * Get 'today' and 'start of the current month' dates
 * @returns {Object} today (Date object) and start of the current month (Date objects)
 */
export const getCurrentMonthRange = (isUtc = true) => {
  const today = new Date();

  return {
    today: millisecondsToSeconds(performDateTimeFunction(endOfDay, isUtc, today)),
    startOfMonth: millisecondsToSeconds(performDateTimeFunction(startOfMonth, isUtc, today))
  };
};

/**
 * Generates range [date-radius, min(date+radius, today)]
 * @param {number} dateSecondsTimestamp Center of range in seconds
 * @param {number} radius how much days we need to substract and add to the center
 * @param {boolean} isUtc using utc zone or local time
 * @returns {DateRange} Date range
 */
export const getRangeAroundDay = (dateSecondsTimestamp, radius = 1, isUtc = true) => {
  const millisecondsDate = secondsToMilliseconds(dateSecondsTimestamp);

  // start date
  const startOfTheDateDay = performDateTimeFunction(startOfDay, isUtc, millisecondsDate);
  const startDate = millisecondsToSeconds(subDays(startOfTheDateDay, radius));

  // end date (today end or timestamp+radius)
  const dayAfter = performDateTimeFunction(addDays, isUtc, millisecondsDate, radius);
  const today = new Date();
  const endOfToday = performDateTimeFunction(endOfDay, isUtc, today);
  const endDate = millisecondsToSeconds(Math.min(dayAfter, endOfToday));

  return {
    startDate,
    endDate
  };
};

/**
 * Generates range for date: [startOfMonth(date), min(endOfMonth(date), today)]
 * @param {number} anyMonthDaySecondsTimestamp Date to base month range on
 * @param {boolean} isUtc using utc zone or local time
 * @returns {DateRange} Date range
 */
export const getMonthRange = (anyMonthDaySecondsTimestamp, isUtc = true) => {
  const millisecondsDate = secondsToMilliseconds(anyMonthDaySecondsTimestamp);

  // start of month
  const startDate = millisecondsToSeconds(performDateTimeFunction(startOfMonth, isUtc, millisecondsDate));

  // end of month or today
  const today = new Date();
  const endOfToday = performDateTimeFunction(endOfDay, isUtc, today);
  const endOfMonthForTimestamp = performDateTimeFunction(endOfMonth, isUtc, millisecondsDate);
  const endDate = millisecondsToSeconds(Math.min(endOfMonthForTimestamp, endOfToday));

  return {
    startDate,
    endDate
  };
};

/**
 * Generates range from start date to today
 * @param {number} startSecondsTimestamp range start
 * @param {boolean} isUtc using utc zone or local time
 * @returns {DateRange} Date range
 */
export const getRangeToToday = (startSecondsTimestamp, isUtc = true) => {
  const millisecondsDate = secondsToMilliseconds(startSecondsTimestamp);

  // start of month
  const startDate = millisecondsToSeconds(performDateTimeFunction(startOfDay, isUtc, millisecondsDate));

  // today
  const today = new Date();
  const endOfToday = performDateTimeFunction(endOfDay, isUtc, today);
  const endDate = millisecondsToSeconds(endOfToday);

  return {
    startDate,
    endDate
  };
};

export const getLast30DaysRange = () => {
  const today = new Date();
  const start = subDays(today, 29);

  return {
    endDate: millisecondsToSeconds(endOfDay(today)),
    startDate: millisecondsToSeconds(startOfDay(start))
  };
};

/**
 * Get 'start of the previous month' and 'end of the previous month' dates
 * @returns {Object} start and end dates of the previous month (Date objects)
 */
export const getLastMonthRange = (isUtc = true) => {
  const today = new Date();
  const previousMonth = subMonths(today, 1);
  const startOfPreviousMonth = performDateTimeFunction(startOfMonth, isUtc, previousMonth);
  const endOfPreviousMonth = performDateTimeFunction(endOfMonth, isUtc, previousMonth);

  return objectMap(
    {
      start: startOfPreviousMonth,
      end: endOfPreviousMonth
    },
    millisecondsToSeconds
  );
};

/**
 * Generates array of full incremented years(integers). If 'from' > 'to', swaps them.
 * @param { Number } to - last year
 * @param { Number } from - first year
 * @returns {Array}
 */
export const generateYears = (to, from = 2020) => {
  let future = to;
  let past = from;

  if (past > future) {
    [future, past] = [past, future];
  }
  return Array.from({ length: future - past + 1 }, (v, i) => past + i);
};

export const getDaysInMonth = (date) => {
  const startWeek = +startOfWeek(startOfMonth(date));
  const endWeek = endOfWeek(endOfMonth(date));
  const days = [];
  for (let curr = startWeek; isBefore(curr, endWeek); curr = addDays(curr, 1)) {
    days.push(curr);
  }
  return days;
};

export const isStartOfRange = ({ startDate }, day) => startDate && isSameDay(day, startDate);

export const isEndOfRange = ({ endDate }, day) => endDate && isSameDay(day, endDate);

export const inDateRange = ({ startDate, endDate }, day) =>
  startDate && endDate && startDate <= endDate && isWithinInterval(day, { start: startDate, end: endDate });

export const isRangeSameDay = ({ startDate, endDate }) => {
  if (startDate && endDate) {
    return isSameDay(startDate, endDate);
  }
  return false;
};

// probably obsolete, used only at HalfHourPopoverContent
export const parseOptionalDate = (date, defaultValue) => {
  if (date && isValid(date)) {
    return date;
  }
  return getTime(defaultValue);
};

export const getValidatedMonths = (range, minDate, maxDate) => {
  const { startDate, endDate } = range;
  if (startDate && endDate) {
    const newStart = max([startDate, minDate]);
    const newEnd = min([endDate, maxDate]);

    // set previous month for left part if range in same month
    return [isSameMonth(newStart, newEnd) ? subMonths(newEnd, 1) : newStart, newEnd];
  }
  return [startDate, endDate];
};

// probably obsolete, used only at HalfHourPopoverContent
export const MIN_PICKER_DATE = getTime(startOfDay(new Date(2020, 0, 1)));

export const fitDateIntoInterval = ({ minDate, maxDate, date }) => Math.min(Math.max(minDate, date), maxDate);

export const fitRangeIntoInterval = ({ minDate, maxDate }, { startDate, endDate }) => ({
  startDate: startDate ? fitDateIntoInterval({ minDate, maxDate, date: startDate }) : startDate,
  endDate: endDate ? fitDateIntoInterval({ minDate, maxDate, date: endDate }) : endDate
});

export const formatRangeToShortNotation = (startDateTimestamp, endDateTimestamp, showInUTC = true) => {
  const formatterFunction = showInUTC
    ? formatUTC
    : (timestamp, formatString) => format(secondsToMilliseconds(timestamp), formatString);

  const currentYear = formatterFunction(millisecondsToSeconds(+new Date()), FORMAT_YYYY);

  const startDateYear = formatterFunction(startDateTimestamp, FORMAT_YYYY);
  const endDateYear = formatterFunction(endDateTimestamp, FORMAT_YYYY);

  const rangeInCurrentYear = startDateYear === currentYear && endDateYear === currentYear;

  const dateFormat = rangeInCurrentYear ? FORMAT_MMM_DD : FORMAT_MMM_DD_YYYY;

  const isOneDayRange =
    differenceInHours(secondsToMilliseconds(endDateTimestamp), secondsToMilliseconds(startDateTimestamp)) <= HOURS_PER_DAY;

  if (isOneDayRange) {
    return formatterFunction(startDateTimestamp, dateFormat);
  }

  return `${formatterFunction(startDateTimestamp, dateFormat)} - ${formatterFunction(endDateTimestamp, dateFormat)}`;
};

export const roundTimeToInterval = (value, intervalMinutes = AMOUNT_30_MINUTES) => {
  let nearest = +roundToNearestMinutes(value, { nearestTo: intervalMinutes });
  if (nearest < value) {
    nearest = +addMinutes(nearest, intervalMinutes);
  }

  return nearest;
};

export const INTERVAL_DURATION_VALUE_TYPES = Object.freeze({
  WEEKS: "weeks",
  DAYS: "days",
  HOURS: "hours",
  MINUTES: "minutes",
  SECONDS: "seconds",
  MILLISECONDS: "milliseconds"
});

export const intervalToDuration = ({ start, end }) => {
  let delta = Math.abs(end - start);

  const weeks = Math.floor(delta / MILLISECONDS_IN_WEEK);
  delta -= weeks * MILLISECONDS_IN_WEEK;

  const days = Math.floor(delta / MILLISECONDS_IN_DAY);
  delta -= days * MILLISECONDS_IN_DAY;

  const hours = Math.floor(delta / MILLISECONDS_IN_HOUR);
  delta -= hours * MILLISECONDS_IN_HOUR;

  const minutes = Math.floor(delta / MILLISECONDS_IN_MINUTE);
  delta -= minutes * MILLISECONDS_IN_MINUTE;

  const seconds = Math.floor(delta / MILLISECONDS_IN_SECOND);
  delta -= seconds * MILLISECONDS_IN_SECOND;

  return {
    [INTERVAL_DURATION_VALUE_TYPES.WEEKS]: weeks,
    [INTERVAL_DURATION_VALUE_TYPES.DAYS]: days,
    [INTERVAL_DURATION_VALUE_TYPES.HOURS]: hours,
    [INTERVAL_DURATION_VALUE_TYPES.MINUTES]: minutes,
    [INTERVAL_DURATION_VALUE_TYPES.SECONDS]: seconds,
    [INTERVAL_DURATION_VALUE_TYPES.MILLISECONDS]: delta
  };
};

// TODO: Try date-fns utils
export const formatSecondsToHHMMSS = (seconds) => {
  let delta = seconds;

  const hours = Math.floor(delta / SECONDS_IN_HOUR);
  delta -= hours * SECONDS_IN_HOUR;

  const minutes = Math.floor(delta / SECONDS_IN_MINUTE);
  delta -= minutes * SECONDS_IN_MINUTE;

  return [hours, minutes, delta].map((value) => String(value).padStart(2, "0")).join(":");
};

// TODO: Try date-fns utils
export const millisecondsToHHMMSSMSFormat = (ms) => {
  const milliseconds = ms % 1000;
  let seconds = Math.floor(ms / 1000);
  let minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  seconds %= 60;
  minutes %= 60;

  return `${[hours, minutes, seconds].map((value) => String(value).padStart(2, "0")).join(":")},${String(milliseconds).padStart(
    3,
    "0"
  )}`;
};

/**
 * Converts given day and hour pair to local values based on a timezone

 * @param { number } hour
 * @param { number } dayOfWeek
 *
 * @returns object
 *
 * Known limitations:
 * - Does not work with locales, weekdays are generated from a enUS list (starts with Su, but accepts Mo as a first day, hence, +1 index shift)
 * - Does not handle DST
 */
export const convertToLocalNumericDayAndHour = (hour, dayOfWeek) => {
  const timezoneOffsetInHours = getDateTimezoneOffset(new Date()) / 60;
  const localHour = hour - timezoneOffsetInHours;
  const localDayIndexOffset = Math.floor(localHour / 24);

  return { dayOfWeek: (dayOfWeek + 1 + localDayIndexOffset) % SHORT_WEEK_DAYS.length, hour: localHour % 24 };
};

/**
 * Converts given day and hour object pair to string format
 * ```
 *    {
 *      "dayOfWeek": 4,
 *      "hour": 18
 *    }
 * ```
 * to
 * `Mo 2:00 PM`

 * @param { object }
 *
 * @returns string
 *
 */
export const formatNumericDayAndHour = (hour, dayOfWeek, options = {}) => {
  const { isBeginningOfHour = true, weekDaysFormat = SHORT_WEEK_DAYS } = options;

  const localTime = format(new Date(null, null, null, hour, isBeginningOfHour ? 0 : 59), EN_TIME_FORMAT);

  return `${weekDaysFormat[dayOfWeek]} ${localTime}`;
};

const convertMinutesToSeconds = (minutes) => minutes * SECONDS_IN_MINUTE;

const convertSecondsToMinutes = (seconds) => seconds / SECONDS_IN_MINUTE;

export {
  addMonths,
  addHours,
  subMonths,
  getDate,
  isSameDay,
  isToday,
  isWithinInterval,
  isAfter,
  isBefore,
  getMonth,
  setMonth,
  getYear,
  setYear,
  getHours,
  getMinutes,
  setMinutes,
  setHours,
  min,
  max,
  isSameMonth,
  differenceInCalendarMonths,
  endOfDay,
  millisecondsToSeconds,
  secondsToMilliseconds,
  secondsToHours,
  endOfYear,
  startOfYear,
  differenceInHours,
  endOfMonth,
  startOfMonth,
  startOfWeek,
  endOfWeek,
  getTime,
  subMinutes,
  addMinutes,
  startOfDay,
  addYears,
  subDays,
  isEqual,
  isValid,
  isPast,
  areIntervalsOverlapping,
  convertMinutesToSeconds,
  convertSecondsToMinutes
};
