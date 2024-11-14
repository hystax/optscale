import {
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  RESOURCE_COUNT_ANOMALY,
  TAGGING_POLICY
} from "utils/constants";
import {
  subDays,
  addDays,
  getStartOfDayInUTCinSeconds,
  getEndOfDayInUTCinSeconds,
  getMonthRange,
  getRangeToToday,
  millisecondsToSeconds,
  subYears,
  getLast30DaysRange
} from "utils/datetime";
import { getLink } from "./getLink";

const getAnomalyDateRange = (constraint) => {
  const { definition: { threshold_days: thresholdDays } = {} } = constraint;

  const today = +new Date();

  return {
    startDate: getStartOfDayInUTCinSeconds(subDays(today, thresholdDays)),
    endDate: getEndOfDayInUTCinSeconds(today)
  };
};

const getResourceQuotaDateRange = () => getLast30DaysRange();

const getRecurrenceBudgetDateRange = () => getMonthRange(millisecondsToSeconds(+new Date()));

const getExpiringBudgetDateRange = (constraint) =>
  getRangeToToday(Math.max(constraint.definition.start_date, millisecondsToSeconds(addDays(subYears(+new Date(), 1), 2))));

const getTaggingPolicyDateRange = (constraint) =>
  getRangeToToday(Math.max(constraint.definition.start_date, millisecondsToSeconds(addDays(subYears(+new Date(), 1), 2))));

const getRangeFn = (constraint) =>
  ({
    [RESOURCE_COUNT_ANOMALY]: () => getAnomalyDateRange(constraint),
    [EXPENSE_ANOMALY]: () => getAnomalyDateRange(constraint),
    [QUOTA_POLICY]: () => getResourceQuotaDateRange(),
    [RECURRING_BUDGET_POLICY]: () => getRecurrenceBudgetDateRange(),
    [EXPIRING_BUDGET_POLICY]: () => getExpiringBudgetDateRange(constraint),
    [TAGGING_POLICY]: () => getTaggingPolicyDateRange(constraint)
  })[constraint.type];

export const getResourcesLink = (constraint) => {
  const dateRange = getRangeFn(constraint)();

  return getLink({
    dateRange,
    constraint
  });
};
