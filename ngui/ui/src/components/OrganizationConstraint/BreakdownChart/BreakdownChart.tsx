import { useMemo } from "react";
import { Skeleton } from "@mui/material";
import ExpensesDailyBreakdownBy from "components/ExpensesDailyBreakdownBy";
import ResourceCountBreakdown from "components/ResourceCountBreakdown";
import { useGetExpensesDailyBreakdownQuery, useGetResourceCountBreakdownQuery } from "graphql/__generated__/hooks/restapi";
import { useBreakdownBy } from "hooks/useBreakdownBy";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { mapFiltersToApiParams } from "services/AvailableFiltersService";
import { DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME, DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME } from "urls";
import { reformatBreakdown } from "utils/api";
import { EXPENSE_ANOMALY, RESOURCE_COUNT_ANOMALY } from "utils/constants";
import { isEmptyObject } from "utils/objects";
import { getResourcesDateRange } from "utils/organizationConstraints/getResourcesDateRange";

const ResourceCountBreakdownContainer = ({ constraint }) => {
  const { organizationId } = useOrganizationInfo();

  const [{ value: breakdownByValue }, onBreakdownByChange] = useBreakdownBy({
    queryParamName: DAILY_RESOURCE_COUNT_BREAKDOWN_BY_PARAMETER_NAME,
  });

  const resourceCountBreakdownRequestParams = useMemo(() => {
    if (isEmptyObject(constraint)) {
      return {};
    }

    const dateRange = getResourcesDateRange(constraint);

    return {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      breakdown_by: breakdownByValue,
      ...mapFiltersToApiParams(constraint.filters),
    };
  }, [breakdownByValue, constraint]);

  const { data: { resourceCountBreakdown = {} } = {}, loading } = useGetResourceCountBreakdownQuery({
    skip: isEmptyObject(constraint),
    variables: {
      organizationId,
      params: resourceCountBreakdownRequestParams,
    },
  });

  return (
    <ResourceCountBreakdown
      resourceCountBreakdown={resourceCountBreakdown}
      breakdownByValue={breakdownByValue}
      onBreakdownByChange={onBreakdownByChange}
      isLoading={loading}
    />
  );
};

const ExpensesDailyBreakdownByContainer = ({ constraint }) => {
  const { organizationId } = useOrganizationInfo();

  const [{ value: breakdownByValue }, onBreakdownByChange] = useBreakdownBy({
    queryParamName: DAILY_EXPENSES_BREAKDOWN_BY_PARAMETER_NAME,
  });

  const expensesDailyBreakdownRequestParams = useMemo(() => {
    if (isEmptyObject(constraint)) {
      return {};
    }

    const dateRange = getResourcesDateRange(constraint);

    return {
      start_date: dateRange.startDate,
      end_date: dateRange.endDate,
      breakdown_by: breakdownByValue,
      ...mapFiltersToApiParams(constraint.filters),
    };
  }, [breakdownByValue, constraint]);

  const { data: { expensesDailyBreakdown = {} } = {}, loading } = useGetExpensesDailyBreakdownQuery({
    skip: isEmptyObject(constraint),
    variables: {
      organizationId,
      params: expensesDailyBreakdownRequestParams,
    },
  });

  const breakdown = useMemo(() => reformatBreakdown(expensesDailyBreakdown?.breakdown ?? {}), [expensesDailyBreakdown]);

  return (
    <ExpensesDailyBreakdownBy
      isLoading={loading}
      breakdown={breakdown}
      counts={expensesDailyBreakdown?.counts ?? {}}
      breakdownByValue={breakdownByValue}
      onBreakdownByChange={onBreakdownByChange}
    />
  );
};

const BreakdownChart = ({ constraint, isGetConstraintLoading }) => {
  if (isGetConstraintLoading) {
    return <Skeleton variant="rectangular" height="320px" />;
  }

  if (constraint.type === RESOURCE_COUNT_ANOMALY) {
    return <ResourceCountBreakdownContainer constraint={constraint} />;
  }

  if (constraint.type === EXPENSE_ANOMALY) {
    return <ExpensesDailyBreakdownByContainer constraint={constraint} />;
  }

  return null;
};

export default BreakdownChart;
