import React from "react";
import { Provider } from "react-redux";
import configureMockStore from "redux-mock-store";
import { GET_RESOURCE_COUNT_BREAKDOWN } from "api/restapi/actionTypes";
import Resources, { data } from "components/Resources";
import { KINDS } from "stories";
import { millisecondsToSeconds, addDays } from "utils/datetime";

export default {
  title: `${KINDS.PAGES}/Resources`
};

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

const mockStore = configureMockStore();
const store = mockStore({
  api: {
    [GET_RESOURCE_COUNT_BREAKDOWN]: {
      isLoading: false,
      timestamp: addDays(Date.now(), 30)
    }
  },
  restapi: {
    [GET_RESOURCE_COUNT_BREAKDOWN]: {
      breakdown: {
        1633046400: {
          Instance: 3,
          Volume: 5
        },
        1633132800: {
          Instance: 3,
          Volume: 6,
          Snapshot: 2,
          "SomeCluster/cluster": 1
        }
      }
    }
  }
});

export const basic = () => (
  <Provider store={store}>
    <Resources
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      filterValues={data.filterValues}
      expenses={data.expenses}
      filters={data.filters}
      entities={data.entities}
      requestParams={data.requestParams}
      totalExpenses={data.totalExpenses}
      totalSaving={data.totalSaving}
      onApply={() => console.log("onApply")}
      onFilterAdd={() => console.log("onFilterAdd")}
      onFilterDelete={() => console.log("onFilterDelete")}
      onFiltersDelete={() => console.log("onFiltersDelete")}
    />
  </Provider>
);

export const isLoading = () => (
  <Resources
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    filterValues={{}}
    expenses={[]}
    filters={{}}
    entities={{}}
    requestParams={{
      startDate: firstDateRangePoint,
      endDate: lastDateRangePoint
    }}
    totalExpenses={0}
    totalSaving={0}
    isLoadingProps={{ isLoading: true, isFilterValuesLoading: true }}
    onApply={() => console.log("onApply")}
    onFilterAdd={() => console.log("onFilterAdd")}
    onFilterDelete={() => console.log("onFilterDelete")}
    onFiltersDelete={() => console.log("onFiltersDelete")}
  />
);
