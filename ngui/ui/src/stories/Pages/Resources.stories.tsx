import { Provider } from "react-redux";
import configureMockStore from "redux-mock-store";
import { GET_RESOURCE_COUNT_BREAKDOWN } from "api/restapi/actionTypes";
import Resources from "components/Resources";
import { data } from "components/Resources/ResourcesMocked";
import { millisecondsToSeconds, addDays } from "utils/datetime";

export default {
  component: Resources
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
      filters={data.filters}
      filterValues={data.filterValues}
      onApply={() => console.log("onApply")}
      onFilterAdd={() => console.log("onFilterAdd")}
      onFiltersDelete={() => console.log("onFiltersDelete")}
      onFilterDelete={() => console.log("onFilterDelete")}
      requestParams={data.requestParams}
    />
  </Provider>
);

export const isLoading = () => (
  <Resources
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    filters={{}}
    requestParams={{
      startDate: firstDateRangePoint,
      endDate: lastDateRangePoint
    }}
    onApply={() => console.log("onApply")}
    onFilterAdd={() => console.log("onFilterAdd")}
    onFilterDelete={() => console.log("onFilterDelete")}
    onFiltersDelete={() => console.log("onFiltersDelete")}
  />
);
