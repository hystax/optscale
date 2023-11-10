import { RESOURCE_FILTERS_NAMES } from "components/Filters/constants";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import {
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  END_DATE_FILTER,
  RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY,
  START_DATE_FILTER
} from "utils/constants";
import { getLastWeekRange } from "utils/datetime";
import Resources from "./Resources";

const data = {
  filterValues: {
    active: [false, true]
  },
  filters: Object.fromEntries(RESOURCE_FILTERS_NAMES.map((name) => [name, undefined])),
  requestParams: { [START_DATE_FILTER]: 1637452800, [END_DATE_FILTER]: 1638057599, limit: 5000 }
};

const ResourcesMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  return (
    <PageMockupContextProvider>
      <Resources
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        filters={data.filters}
        filterValues={data.filterValues}
        onApply={() => console.log("onApply")}
        onFilterAdd={() => console.log("onFilterAdd")}
        onFilterDelete={() => console.log("onFilterDelete")}
        onFiltersDelete={() => console.log("onFiltersDelete")}
        requestParams={data.requestParams}
        activeBreakdown={{
          name: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
          value: "expenses"
        }}
        selectedPerspective={undefined}
        isFilterValuesLoading={false}
        expensesBreakdownPageState={{
          breakdownBy: [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID, null],
          groupBy: [{}, null]
        }}
        resourceCountBreakdownPageState={{
          breakdownBy: [RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID, null]
        }}
        perspectives={{}}
        onBreakdownChange={() => console.log("onBreakdownChange")}
        onPerspectiveApply={() => console.log("onPerspectiveApply")}
      />
    </PageMockupContextProvider>
  );
};

export default ResourcesMocked;
