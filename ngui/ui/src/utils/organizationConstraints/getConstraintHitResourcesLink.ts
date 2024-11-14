import {
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  RESOURCE_COUNT_ANOMALY,
  TAGGING_POLICY
} from "utils/constants";
import {
  secondsToMilliseconds,
  subDays,
  addDays,
  getStartOfDayInUTCinSeconds,
  getEndOfDayInUTCinSeconds,
  getRangeAroundDay,
  getMonthRange,
  getRangeToToday,
  millisecondsToSeconds,
  subYears
} from "utils/datetime";
import { getLink } from "./getLink";

const getAnomalyDateRange = (hitDate, constraint) => {
  const { definition: { threshold_days: thresholdDays } = {} } = constraint;

  return {
    startDate: getStartOfDayInUTCinSeconds(subDays(secondsToMilliseconds(hitDate), thresholdDays)),
    endDate: getEndOfDayInUTCinSeconds(addDays(secondsToMilliseconds(hitDate), 1))
  };
};

const getResourceQuotaDateRange = (hitDate) => getRangeAroundDay(hitDate);

const getRecurringBudgetDateRange = (hitDate) => getMonthRange(hitDate);

const getExpiringBudgetDateRange = (constraint) =>
  getRangeToToday(Math.max(constraint.definition.start_date, millisecondsToSeconds(addDays(subYears(+new Date(), 1), 2))));

const getTaggingPolicyDateRange = (hitDate) => ({
  startDate: getStartOfDayInUTCinSeconds(secondsToMilliseconds(hitDate)),
  endDate: getEndOfDayInUTCinSeconds(secondsToMilliseconds(hitDate))
});

const getRangeFn = ({ hitDate, constraint }) =>
  ({
    [RESOURCE_COUNT_ANOMALY]: () => getAnomalyDateRange(hitDate, constraint),
    [EXPENSE_ANOMALY]: () => getAnomalyDateRange(hitDate, constraint),
    [QUOTA_POLICY]: () => getResourceQuotaDateRange(hitDate),
    [RECURRING_BUDGET_POLICY]: () => getRecurringBudgetDateRange(hitDate),
    [EXPIRING_BUDGET_POLICY]: () => getExpiringBudgetDateRange(constraint),
    [TAGGING_POLICY]: () => getTaggingPolicyDateRange(hitDate)
  })[constraint.type];

export const getConstraintHitResourcesLink = (hitDate, constraint) => {
  const dateRange = getRangeFn({ hitDate, constraint })();

  return getLink({
    dateRange,
    constraint
  });
};
