import React from "react";
import ListAltOutlinedIcon from "@mui/icons-material/ListAltOutlined";
import { FormattedMessage } from "react-intl";
import Filters from "components/Filters";
import { RESOURCE_FILTERS } from "components/Filters/constants";
import IconButton from "components/IconButton";
import TextWithDataTestId from "components/TextWithDataTestId";
import { RESOURCES, RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME } from "urls";
import {
  END_DATE_FILTER,
  EXPENSE_ANOMALY,
  EXPIRING_BUDGET_POLICY,
  QUOTA_POLICY,
  RECURRING_BUDGET_POLICY,
  TAGGING_POLICY,
  RESOURCE_COUNT_ANOMALY,
  START_DATE_FILTER,
  CLEAN_EXPENSES_BREAKDOWN_TYPES
} from "utils/constants";
import {
  secondsToMilliseconds,
  subDays,
  addDays,
  getStartOfDayInUTCinSeconds,
  getEndOfDayInUTCinSeconds,
  getRangeAroundDay,
  getMonthRange,
  getRangeToToday
} from "utils/datetime";

const mapConstraintTypeToResourcesBreakdown = (type) =>
  ({
    [EXPENSE_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
    [RESOURCE_COUNT_ANOMALY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
    [QUOTA_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.RESOURCE_COUNT,
    [RECURRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
    [EXPIRING_BUDGET_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
    [TAGGING_POLICY]: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES
  }[type]);

const getAnomalyDateRange = (hitDate, thresholdDays) => ({
  startDate: getStartOfDayInUTCinSeconds(subDays(secondsToMilliseconds(hitDate), thresholdDays)),
  endDate: getEndOfDayInUTCinSeconds(addDays(secondsToMilliseconds(hitDate), 1))
});

const getTaggingPolicyDateRange = (hitDate) => ({
  startDate: getStartOfDayInUTCinSeconds(secondsToMilliseconds(hitDate)),
  endDate: getEndOfDayInUTCinSeconds(secondsToMilliseconds(hitDate))
});

const getDateRangeForHit = (hitDate, constraint) => {
  const { definition: { start_date: startDate, threshold_days: thresholdDays } = {} } = constraint;
  return {
    [RESOURCE_COUNT_ANOMALY]: getAnomalyDateRange(hitDate, thresholdDays),
    [EXPENSE_ANOMALY]: getAnomalyDateRange(hitDate, thresholdDays),
    [QUOTA_POLICY]: getRangeAroundDay(hitDate),
    [RECURRING_BUDGET_POLICY]: getMonthRange(hitDate),
    [EXPIRING_BUDGET_POLICY]: getRangeToToday(startDate),
    [TAGGING_POLICY]: getTaggingPolicyDateRange(hitDate)
  }[constraint.type];
};

const constraintHitActions = ({ navigate, constraint }) => {
  // Implicit filters might be returned in conditions, since they are excluded in available filters, e.g. tagging policies
  const allFilters = {
    ...constraint.filters,
    ...Object.entries(constraint.definition?.conditions ?? {}).reduce(
      (result, [key, value]) => ({ ...result, [key]: [value] }),
      {}
    )
  };

  return {
    header: (
      <TextWithDataTestId dataTestId="lbl_actions">
        <FormattedMessage id="actions" />
      </TextWithDataTestId>
    ),
    enableSorting: false,
    id: "actions",
    cell: ({
      row: {
        original: { created_at: createdAt },
        index
      }
    }) => (
      <IconButton
        dataTestId={`actions_column_link_${index}`}
        icon={<ListAltOutlinedIcon />}
        onClick={() => {
          const { startDate, endDate } = getDateRangeForHit(createdAt, constraint);

          const filtersInstance = new Filters({
            filters: RESOURCE_FILTERS,
            filterValues: allFilters
          });

          const filtersQueryParams = filtersInstance.toQueryParametersString();

          const dateRangeQueryParams = [`${START_DATE_FILTER}=${startDate}`, `${END_DATE_FILTER}=${endDate}`].join("&");

          const breakdownByQueryParam = `${RESOURCES_BREAKDOWN_BY_QUERY_PARAMETER_NAME}=${mapConstraintTypeToResourcesBreakdown(
            constraint.type
          )}`;

          const queryParams = [filtersQueryParams, dateRangeQueryParams, breakdownByQueryParam].join("&");

          // TODO: Use getResourcesExpensesUrl util to get a link
          const link = `${RESOURCES}?${queryParams}`;

          navigate(link);
        }}
        tooltip={{
          show: true,
          value: <FormattedMessage id="showResources" />
        }}
      />
    )
  };
};

export default constraintHitActions;
