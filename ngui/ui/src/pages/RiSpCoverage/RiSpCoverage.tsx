import { useMemo } from "react";
import { Link } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Stack from "@mui/material/Stack";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import PageContentWrapper from "components/PageContentWrapper";
import RiSpCoverageComponent from "components/RiSpCoverage";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { useAllDataSources } from "hooks/coreData/useAllDataSources";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { useRiSpBreakdowns } from "hooks/useRiSpBreakdowns";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { RECOMMENDATIONS, RI_SP_QUERY_PARAMETERS } from "urls";
import { isEmptyArray } from "utils/arrays";
import { DATE_RANGE_TYPE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const filterBreakdownByIds = (breakdown, dataSourceIds) => {
  if (!dataSourceIds || isEmptyArray(dataSourceIds)) {
    return breakdown;
  }

  return Object.fromEntries(
    Object.entries(breakdown).map(([date, entries]) => [
      date,
      entries.filter((entry) => dataSourceIds.includes(entry.cloud_account_id)),
    ])
  );
};

const getDataSourcesTypes = (usageBreakdown, expensesBreakdown) => [
  ...new Set(
    [...Object.values(usageBreakdown).flat(), ...Object.values(expensesBreakdown).flat()].map((b) => b.cloud_account_type)
  ),
];

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
      <FormattedMessage id="recommendations" />
    </Link>,
  ],
  title: {
    messageId: "riSpCoverageTitle",
  },
};

const RiSpCoverage = () => {
  const dataSources = useAllDataSources();

  const [selectedDataSourceIds, setSelectedDataSources] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.DATA_SOURCE_ID,
    defaultValue: [],
    parameterIsArray: true,
  });

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const [selectedStartDate, setSelectedStartDate] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.START_DATE,
    defaultValue: startDateTimestamp,
  });

  const [selectedEndDate, setSelectedEndDate] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.END_DATE,
    defaultValue: endDateTimestamp,
  });

  const onApply = ({ startDate, endDate }) => {
    setSelectedStartDate(startDate);
    setSelectedEndDate(endDate);
  };

  const params = useMemo(
    () => ({
      startDate: selectedStartDate,
      endDate: selectedEndDate,
      dataSourceIds: [],
    }),
    [selectedStartDate, selectedEndDate]
  );

  const { isLoading, expensesBreakdown, usageBreakdown } = useRiSpBreakdowns(params);

  const targetDataSourceTypes = getDataSourcesTypes(usageBreakdown, expensesBreakdown);
  const allDataSources = dataSources.filter((dataSource) => targetDataSourceTypes.includes(dataSource.type));

  const filteredUsage = filterBreakdownByIds(usageBreakdown, selectedDataSourceIds);
  const filteredExpenses = filterBreakdownByIds(expensesBreakdown, selectedDataSourceIds);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <Stack direction="row" spacing={SPACING_2}>
            <div>
              <DataSourceMultiSelect
                allDataSources={allDataSources}
                dataSourceIds={selectedDataSourceIds}
                onChange={setSelectedDataSources}
                displayEmpty
              />
            </div>
            <div>
              {/* TODO: migrate FormControl into RangePickerFormContainer to avoid misalignment and additional styles */}
              <FormControl>
                <RangePickerFormContainer
                  onApply={onApply}
                  initialStartDateValue={selectedStartDate}
                  initialEndDateValue={selectedEndDate}
                  rangeType="expenses"
                  selectedEndDate
                  definedRanges={getBasicRangesSet()}
                />
              </FormControl>
            </div>
          </Stack>
          <div>
            <RiSpCoverageComponent
              usageBreakdown={filteredUsage}
              expensesBreakdown={filteredExpenses}
              isLoadingProps={{
                isGetUsageBreakdownLoading: isLoading,
                isGetExpensesBreakdownLoading: isLoading,
              }}
            />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default RiSpCoverage;
