import { PageMockupContextProvider } from "contexts/PageMockupContext";
import { CLEAN_EXPENSES_BREAKDOWN_TYPES, END_DATE_FILTER, START_DATE_FILTER } from "utils/constants";
import { getLastWeekRange } from "utils/datetime";
import { FILTER_CONFIGS } from "./filterConfigs";
import Resources from "./Resources";

export const data = {
  filterValues: {},
  requestParams: { [START_DATE_FILTER]: 1637452800, [END_DATE_FILTER]: 1638057599, limit: 5000 },
};

const ResourcesMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  return (
    <PageMockupContextProvider>
      <Resources
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        filterValues={data.filterValues}
        onApply={() => console.log("onApply")}
        requestParams={data.requestParams}
        activeBreakdown={CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES}
        selectedPerspectiveName={undefined}
        perspectives={{}}
        onPerspectiveApply={() => console.log("onPerspectiveApply")}
        appliedFilters={Object.fromEntries(
          Object.values(FILTER_CONFIGS).map((filterConfig) => {
            const { id, getDefaultValue } = filterConfig;
            return [id, getDefaultValue()];
          })
        )}
        onAppliedFiltersChange={() => console.log("onAppliedFiltersChange")}
        isFilterValuesLoading={false}
        onBreakdownChange={() => console.log("onBreakdownChange")}
      />
    </PageMockupContextProvider>
  );
};

export default ResourcesMocked;
