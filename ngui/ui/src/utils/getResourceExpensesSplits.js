import { createGroupsObjectFromArray, splitIntoChunks } from "utils/arrays";
import { EXPENSES_SPLIT_PERIODS, WEEK_LENGTH } from "utils/constants";
import { formatUTC, EN_FORMAT_SHORT_YEAR, FORMAT_MMM_YYYY } from "utils/datetime";
import { isObject } from "utils/objects";

/**
 * @typedef {number | {id: string, cost: number}} CostRecord
 * @typedef {{date: string, dateMonthYear?: string} | {[key: string]: CostRecord}} ResourceExpenseCostBreakdownItem
 * union above is wrong, must be intersection, but https://github.com/microsoft/TypeScript/issues/17867
 */

export const SPLITS = Object.values(EXPENSES_SPLIT_PERIODS);

/**
 * Creates one resource expenses cost breakdown item from many
 * @example
 * const breakdown = [
 *   {
 *     "date": unixtimestamptoday,
 *     "Compute Engine": 0.5,
 *     "Compute Engine_DETAILS": {
 *       "id": "Compute Engine",
 *       "cost": 0.5
 *   },
 *   {
 *     "date": unixtimestamdaybefore,
 *     "Compute Engine": 1,
 *     "Compute Engine_DETAILS": {
 *       "id": "Compute Engine",
 *       "cost": 1
 *   },
 * ];
 *
 * summarize(breakdown, "foo bar");
 * // returns {
 * //     "date": "foo bar",
 * //     "Compute Engine": 1.5,
 * //     "Compute Engine_DETAILS": {
 * //       "id": "Compute Engine",
 * //       "cost": 1.5
 * // }
 * //
 *
 * @param {ResourceExpenseCostBreakdownItem[]} chunk
 * @param {string} dateIntervalLabel
 * @returns {ResourceExpenseCostBreakdownItem}
 */
const summarize = (chunk, dateIntervalLabel) =>
  chunk.reduce(
    (acc, current) => {
      Object.entries(current).forEach(([key, value]) => {
        if (isObject(value)) {
          acc[key] = { ...value, cost: (acc[key]?.cost || 0) + value.cost };
        }
        if (typeof value === "number") {
          acc[key] = (acc[key] || 0) + value;
        }
      });
      return acc;
    },
    { date: dateIntervalLabel }
  );

export const getResourceExpensesSplits = (breakdown) => {
  const withDates = breakdown.map((b) => ({
    ...b,
    // Date to show in daily and weekly breakdowns as bar label
    date: formatUTC(b.date, EN_FORMAT_SHORT_YEAR),
    // Used to group items by months and to show date below chart as bar label
    dateMonthYear: formatUTC(b.date, FORMAT_MMM_YYYY)
  }));

  // each item represents one day, to get week ranges
  // 1. splitting array into 7 items chunks
  // 2. summarizing each chunk into one item, with date equals "weekStartDate — weekEndDate"
  // to get monthly split, due to month have different amount of days:
  // 1. Creating object with keys dateMonthYear, each key content is expenses items array from that one month
  // 2. summarizing each array into one item, giving it dateMonthYear date
  return {
    [EXPENSES_SPLIT_PERIODS.DAILY]: withDates,
    [EXPENSES_SPLIT_PERIODS.WEEKLY]: splitIntoChunks(withDates, WEEK_LENGTH).map((weeklyChunk) =>
      summarize(weeklyChunk, `${weeklyChunk[0].date} - ${weeklyChunk.slice(-1)[0].date}`)
    ),
    [EXPENSES_SPLIT_PERIODS.MONTHLY]: Object.entries(createGroupsObjectFromArray(withDates, "dateMonthYear")).flatMap(
      ([date, monthData]) => summarize(monthData, date)
    )
  };
};
