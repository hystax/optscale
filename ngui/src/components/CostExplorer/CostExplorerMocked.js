import React from "react";
import { getLastWeekRange, addDaysToTimestamp } from "utils/datetime";
import CostExplorer from "./CostExplorer";

const CostExplorerMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  const breakdown = {
    [firstDateRangePoint]: [
      {
        name: "expenses",
        expense: 4627.5326954293
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 1)]: [
      {
        name: "expenses",
        expense: 4172.8897778029
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 2)]: [
      {
        name: "expenses",
        expense: 4721.1260492347
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 3)]: [
      {
        name: "expenses",
        expense: 3345.0090466069
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 4)]: [
      {
        name: "expenses",
        expense: 3321.3196469359
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 5)]: [
      {
        name: "expenses",
        expense: 3778.3216464526
      }
    ],
    [lastDateRangePoint]: [
      {
        name: "expenses",
        expense: 1967.831646181
      }
    ]
  };

  return (
    <CostExplorer
      total={25034.0305086433}
      previousTotal={28164.199989791334}
      breakdown={breakdown}
      organizationName="Sunflower corporation"
      isLoading={false}
      onApply={() => console.log("apply")}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      isInScopeOfPageMockup
    />
  );
};

export default CostExplorerMocked;
