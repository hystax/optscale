import React from "react";
import { EXPENSES_FILTERBY_TYPES, COST_EXPLORER } from "utils/constants";
import { getLastWeekRange, addDaysToTimestamp } from "utils/datetime";
import ExpensesBreakdown from "../ExpensesBreakdown";

const ExpensesBreakdownForPoolMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  const breakdown = {
    [firstDateRangePoint]: [
      {
        expense: 1019.3258221514999,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 180.2017514556,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      },
      {
        expense: 1613.2313672838,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      },
      {
        expense: 276.1523412237,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 74.4906655197,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 72.7163822619,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 936.8585263726,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 1)]: [
      {
        expense: 1102.6585871711998,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 280.91775902850003,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 1390.8918817483,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 1613.4434233713,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      },
      {
        expense: 76.9318762518,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 76.15093382010001,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 180.2273691024,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 2)]: [
      {
        expense: 67.1536310895,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 974.2399681978,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 72.6631623288,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 1613.1315150162,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      },
      {
        expense: 161.9679362166,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 275.6764456938,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 180.2017514556,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 3)]: [
      {
        expense: 158.44384362690002,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 950.0576681791,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 276.3570788622,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 74.7105337719,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 1613.2712527926,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      },
      {
        expense: 68.3036160696,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 180.2017514556,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 4)]: [
      {
        expense: 274.10609124,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 1613.0356802379,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      },
      {
        expense: 80.08177620599999,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 180.2027137797,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      },
      {
        expense: 1222.745308003,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 84.7720109736,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 323.4172536729001,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 5)]: [
      {
        expense: 180.2017514556,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      },
      {
        expense: 555.2347831983001,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 271.9155268215,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 969.9197964257,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 77.3725232439,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 76.1843484387,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 1612.8339342696,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      }
    ],
    [lastDateRangePoint]: [
      {
        expense: 14.12412918,
        id: "a7dade94-0877-4213-8aed-02be2030886e",
        name: "QA"
      },
      {
        expense: 1534.1528748738,
        id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
        name: "Operations"
      },
      {
        expense: 310.1512353771,
        id: "2a03382a-a036-4881-b6b5-68c08192cc44",
        name: "Sunflower corporation"
      },
      {
        expense: 5.089296,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 326.4942996365,
        id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
        name: "Dev"
      },
      {
        expense: 229.7063507977,
        id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
        name: "Marketing"
      },
      {
        expense: 1612.8339342696,
        id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
        name: "Ops"
      }
    ]
  };

  const filteredBreakdown = [
    {
      total: 11295.2231945,
      previous_total: 12904.245314669699,
      id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
      name: "Ops"
    },
    {
      total: 6731.8333656,
      previous_total: 8318.801227306532,
      id: "00000000-0000-0000-0000-000000000000",
      name: "(not set)"
    },
    {
      total: 5066.33862881,
      previous_total: 3112.1316210275995,
      id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
      name: "Operations"
    },
    {
      total: 2034.16025902,
      previous_total: 2205.0221313149996,
      id: "31622be0-00f9-4138-b033-eee45aefb558",
      name: "Sunflower corp"
    },
    {
      total: 1095.36121788,
      previous_total: 1443.270115071,
      id: "a7dade94-0877-4213-8aed-02be2030886e",
      name: "QA"
    },
    {
      total: 741.972982236,
      previous_total: 521.3964424356,
      id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
      name: "Marketing"
    },
    {
      total: 336.40631981,
      previous_total: 497.3156913609,
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Dev"
    }
  ];

  return (
    <ExpensesBreakdown
      filterBy={EXPENSES_FILTERBY_TYPES.POOL}
      type={COST_EXPLORER}
      breakdown={breakdown}
      total={27301.2959679}
      previousTotal={29048.53603396233}
      filteredBreakdown={filteredBreakdown}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      isLoading={false}
      onApply={() => {}}
      updateFilter={() => {}}
      isInScopeOfPageMockup
    />
  );
};

export default ExpensesBreakdownForPoolMocked;
