import { Box, Stack } from "@mui/material";
import { useAvailableFiltersQuery, useMetaBreakdownQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { mapAvailableFilterKeys } from "services/AvailableFiltersService";
import {
  APPLY_FILTER_BY_CATEGORY_QUERY_PARAMETER_NAME,
  DAILY_META_BREAKDOWN_BY_PARAMETER_NAME,
  DAILY_META_BREAKDOWN_TYPE_PARAMETER_NAME,
  WITH_LEGEND_QUERY_PARAMETER_NAME,
} from "urls";
import { isEmptyArray } from "utils/arrays";
import { SPACING_1 } from "utils/layouts";
import BreakdownChart from "./BreakdownChart";
import { BREAKDOWN_TYPE, BREAKDOWN_FIELD_NAME } from "./constants";
import Heading from "./Heading";
import TabContentLoader from "./TabContentLoader";
import TotalsTable from "./TotalsTable";
import { AvailableMetaFiltersProps, MetaProps } from "./types";

const MetaTab = ({ dateRange, requestParams, metaNames = [] }: MetaProps) => {
  const { organizationId } = useOrganizationInfo();

  const [breakdownBy, setBreakdownBy] = useSyncQueryParamWithState({
    queryParamName: DAILY_META_BREAKDOWN_BY_PARAMETER_NAME,
    defaultValue: metaNames[0] ?? "",
    possibleStates: metaNames,
  });

  const [breakdownType, setBreakdownType] = useSyncQueryParamWithState({
    queryParamName: DAILY_META_BREAKDOWN_TYPE_PARAMETER_NAME,
    defaultValue: BREAKDOWN_TYPE.EXPENSES,
    possibleStates: Object.values(BREAKDOWN_TYPE),
  });

  const [withLegend, setWithLegend] = useSyncQueryParamWithState({
    queryParamName: WITH_LEGEND_QUERY_PARAMETER_NAME,
    possibleStates: [true, false],
    defaultValue: true,
  });

  const [applyFilterByCategory, setApplyFilterByCategory] = useSyncQueryParamWithState({
    queryParamName: APPLY_FILTER_BY_CATEGORY_QUERY_PARAMETER_NAME,
    possibleStates: [true, false],
    defaultValue: false,
  });

  const filters = mapAvailableFilterKeys(requestParams);

  const { data: metaBreakdownData, loading: isLoadingMetaBreakdown } = useMetaBreakdownQuery({
    variables: {
      organizationId,
      params: {
        ...filters,
        meta: applyFilterByCategory ? Array.from(new Set([breakdownBy, ...filters.meta])) : filters.meta,
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
        breakdown_by: breakdownBy,
      },
    },
    skip: isEmptyArray(metaNames),
  });

  const field =
    breakdownType === BREAKDOWN_TYPE.EXPENSES || breakdownType === BREAKDOWN_TYPE.EXPENSES_PERCENT
      ? BREAKDOWN_FIELD_NAME.COST
      : BREAKDOWN_FIELD_NAME.COUNT;

  const isPercentBreakdownType =
    breakdownType === BREAKDOWN_TYPE.EXPENSES_PERCENT || breakdownType === BREAKDOWN_TYPE.COUNT_PERCENT;

  return (
    <Stack spacing={SPACING_1}>
      <Heading
        breakdownBy={breakdownBy}
        onBreakdownChange={setBreakdownBy}
        metaNames={metaNames}
        breakdownType={breakdownType}
        onBreakdownTypeChange={setBreakdownType}
        applyFilterByCategory={applyFilterByCategory}
        onApplyFilterByCategoryChange={setApplyFilterByCategory}
        withLegend={withLegend}
        onWithLegendChange={setWithLegend}
      />
      <Box>
        <BreakdownChart
          breakdownBy={breakdownBy}
          breakdown={metaBreakdownData?.metaBreakdown?.breakdown ?? {}}
          totals={metaBreakdownData?.metaBreakdown?.totals ?? {}}
          field={field}
          withLegend={withLegend}
          isLoading={isLoadingMetaBreakdown}
          isPercentBreakdownType={isPercentBreakdownType}
        />
      </Box>
      <Box>
        <TotalsTable
          metaName={breakdownBy}
          startDate={dateRange.startDate}
          endDate={dateRange.endDate}
          totals={metaBreakdownData?.metaBreakdown?.totals ?? {}}
          isLoading={isLoadingMetaBreakdown}
        />
      </Box>
    </Stack>
  );
};

const AvailableMetaFilters = ({ requestParams }: AvailableMetaFiltersProps) => {
  const { organizationId } = useOrganizationInfo();

  const { startDate: startDateString, endDate: endDateString, ...restRequestParams } = requestParams;

  const dateRange = {
    startDate: Number(startDateString),
    endDate: Number(endDateString),
  };

  const { data: availableFiltersData, loading: isAvailableFiltersLoading } = useAvailableFiltersQuery({
    variables: {
      organizationId,
      params: {
        ...mapAvailableFilterKeys(restRequestParams),
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
      },
    },
  });

  const metaNames =
    (availableFiltersData?.availableFilters?.meta as string[])?.toSorted((nameA, nameB) => nameA.localeCompare(nameB)) ?? [];

  if (isAvailableFiltersLoading) {
    return <TabContentLoader />;
  }

  return <MetaTab dateRange={dateRange} requestParams={restRequestParams} metaNames={metaNames} />;
};

export default AvailableMetaFilters;
