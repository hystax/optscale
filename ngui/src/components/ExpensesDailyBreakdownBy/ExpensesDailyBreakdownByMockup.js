import React from "react";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";
import { addDaysToTimestamp } from "utils/datetime";
import ExpensesDailyBreakdownBy from "./ExpensesDailyBreakdownBy";

const getBreakdown = (startDateSecondsTimestamp) => ({
  [startDateSecondsTimestamp]: [
    {
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      cost: 9.3,
      name: "Katy Ali"
    },
    {
      id: "11111111-d146-4932-adb0-20c4222c1e6f",
      cost: 2.1,
      name: "Ella Price"
    },
    {
      id: "21111111-d146-4932-adb0-20c4222c1e6f",
      cost: 3.21,
      name: "Sally Wong"
    },
    {
      id: "31111111-d146-4932-adb0-20c4222c1e6f",
      cost: 6,
      name: "Taylor Everett"
    },
    {
      id: "41111111-d146-4932-adb0-20c4222c1e6f",
      cost: 1.6,
      name: "Amy Smith"
    },
    {
      id: "51111111-d146-4932-adb0-20c4222c1e6f",
      cost: 9.9,
      name: "Marie Briggs"
    }
  ],
  [addDaysToTimestamp(startDateSecondsTimestamp, 1)]: [
    {
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      cost: 9.41,
      name: "Katy Ali"
    },
    {
      id: "11111111-d146-4932-adb0-20c4222c1e6f",
      cost: 10.2,
      name: "Ella Price"
    },
    {
      id: "21111111-d146-4932-adb0-20c4222c1e6f",
      cost: 5.02,
      name: "Sally Wong"
    },
    {
      id: "31111111-d146-4932-adb0-20c4222c1e6f",
      cost: 15.2,
      name: "Taylor Everett"
    },
    {
      id: "41111111-d146-4932-adb0-20c4222c1e6f",
      cost: 13.6,
      name: "Amy Smith"
    },
    {
      id: "51111111-d146-4932-adb0-20c4222c1e6f",
      cost: 2.3,
      name: "Marie Briggs"
    }
  ],
  [addDaysToTimestamp(startDateSecondsTimestamp, 2)]: [
    {
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      cost: 7,
      name: "Katy Ali"
    },
    {
      id: "11111111-d146-4932-adb0-20c4222c1e6f",
      cost: 4.02,
      name: "Ella Price"
    },
    {
      id: "21111111-d146-4932-adb0-20c4222c1e6f",
      cost: 12.32,
      name: "Sally Wong"
    },
    {
      id: "31111111-d146-4932-adb0-20c4222c1e6f",
      cost: 2.43,
      name: "Taylor Everett"
    },
    {
      id: "41111111-d146-4932-adb0-20c4222c1e6f",
      cost: 4.16,
      name: "Amy Smith"
    },
    {
      id: "51111111-d146-4932-adb0-20c4222c1e6f",
      cost: 1.98,
      name: "Marie Briggs"
    }
  ],
  [addDaysToTimestamp(startDateSecondsTimestamp, 3)]: [
    {
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      cost: 3,
      name: "Katy Ali"
    },
    {
      id: "11111111-d146-4932-adb0-20c4222c1e6f",
      cost: 8.32,
      name: "Ella Price"
    },
    {
      id: "21111111-d146-4932-adb0-20c4222c1e6f",
      cost: 4.12,
      name: "Sally Wong"
    },
    {
      id: "31111111-d146-4932-adb0-20c4222c1e6f",
      cost: 1,
      name: "Taylor Everett"
    },
    {
      id: "41111111-d146-4932-adb0-20c4222c1e6f",
      cost: 3.21,
      name: "Amy Smith"
    },
    {
      id: "51111111-d146-4932-adb0-20c4222c1e6f",
      cost: 1.98,
      name: "Marie Briggs"
    }
  ]
});

const ExpensesDailyBreakdownByMockup = ({ startDateTimestamp: startDateSecondsTimestamp }) => (
  <ExpensesDailyBreakdownBy
    breakdown={getBreakdown(startDateSecondsTimestamp)}
    breakdownBy={RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID}
    onBreakdownByChange={() => console.log("Click")}
  />
);

export default ExpensesDailyBreakdownByMockup;
