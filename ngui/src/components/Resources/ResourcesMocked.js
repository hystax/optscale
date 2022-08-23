import React from "react";
import PropTypes from "prop-types";
import { PageMockupContextProvider } from "contexts/PageMockupContext";
import { getLastWeekRange } from "utils/datetime";
import Resources from "./Resources";

const data = {
  filterValues: {
    active: [false, true]
  },
  filters: {
    start_date: 1600905600,
    end_date: 1600991999,
    resource_type: [
      {
        name: "Instance",
        type: null
      }
    ]
  },
  requestParams: { startDate: 1637452800, endDate: 1638057599, limit: 5000 }
};

const ResourcesMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  return (
    <PageMockupContextProvider>
      <Resources
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
        filterValues={data.filterValues}
        filters={data.filters}
        requestParams={data.requestParams}
        onApply={() => console.log("onApply")}
        onFilterAdd={() => console.log("onFilterAdd")}
        onFilterDelete={() => console.log("onFilterDelete")}
        onFiltersDelete={() => console.log("onFiltersDelete")}
        fromMainMenu
        isInScopeOfPageMockup
      />
    </PageMockupContextProvider>
  );
};

ResourcesMocked.propTypes = {
  isInScopeOfStory: PropTypes.bool
};

export default ResourcesMocked;
