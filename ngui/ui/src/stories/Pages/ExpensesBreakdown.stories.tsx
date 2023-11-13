import ExpensesBreakdown from "components/ExpensesBreakdown";
import { KINDS } from "stories";
import { COST_EXPLORER, EXPENSES_FILTERBY_TYPES, CLOUD_DETAILS, OWNER_DETAILS, POOL_DETAILS } from "utils/constants";
import { getLastWeekRange, addDaysToTimestamp } from "utils/datetime";

export default {
  title: `${KINDS.PAGES}/ExpensesBreakdown`,
  argTypes: {
    type: {
      name: "Type",
      control: "select",
      options: [COST_EXPLORER, CLOUD_DETAILS, OWNER_DETAILS, POOL_DETAILS],
      defaultValue: COST_EXPLORER
    }
  }
};

const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

const expenses = {
  total: 3160,
  id: "e1a34742-1531-4b68-b52a-d1d438e52b68",
  name: "FutureOps.com",
  breakdown: {
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        pool_id: "31622be0-00f9-4138-b033-eee45aefb558",
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
        expense: 2.8161423576,
        id: "c4c3a518-ab9c-4aba-912c-708cc51d9b5e",
        name: "Oscar Walsh"
      },
      {
        expense: 31.0973209002,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 15.409309717800001,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 57.1035847473,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 273.35516935140004,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 3.4420872366,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 15.3958764096,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 279.2147783186,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      }
    ]
  },
  pool: [
    {
      total: 9682.389260208,
      previous_total: 12904.245314669699,
      id: "e445ee8b-f062-4b45-9baf-05e11cf5635f",
      name: "Ops"
    },
    {
      total: 6726.7440696027,
      previous_total: 8318.801227306532,
      id: "00000000-0000-0000-0000-000000000000",
      name: "(not set)"
    },
    {
      total: 3532.1857539398998,
      previous_total: 3112.1316210275995,
      id: "a466e029-82cf-439d-b641-e4f65cfaaf71",
      name: "Operations"
    },
    {
      total: 1724.0090236479,
      previous_total: 2205.0221313149996,
      id: "31622be0-00f9-4138-b033-eee45aefb558",
      name: "Sunflower corp"
    },
    {
      total: 1081.2370887045001,
      previous_total: 1443.270115071,
      id: "a7dade94-0877-4213-8aed-02be2030886e",
      name: "QA"
    },
    {
      total: 512.2666314387,
      previous_total: 521.3964424356,
      id: "8ce779dc-cc2a-4210-9770-00a2ce7ccf39",
      name: "Marketing"
    },
    {
      total: 501.60478098240003,
      previous_total: 497.3156913609,
      id: "65846b0e-d146-4932-adb0-20c4222c1e6f",
      name: "Dev"
    }
  ]
};

const onApply = () => console.log("onApply");

const updateFilter = () => console.log("updateFilter");

const Basic = (args) => {
  const { type } = args;
  const { name, entityId } =
    type !== COST_EXPLORER
      ? {
          name: "Entity name",
          entityId: "Entity id"
        }
      : {};
  return (
    <ExpensesBreakdown
      filterBy={EXPENSES_FILTERBY_TYPES.POOL}
      type={type}
      breakdown={expenses.breakdown}
      name={name}
      entityId={entityId}
      total={27301.2959679}
      previousTotal={29048.53603396233}
      filteredBreakdown={expenses.pool}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      isLoading={false}
      onApply={onApply}
      updateFilter={updateFilter}
    />
  );
};

const WithoutPieChar = () => {
  const poolName = "Operations";

  const pool = expenses.pool.find((p) => p.name === poolName);

  return (
    <ExpensesBreakdown
      filterBy={EXPENSES_FILTERBY_TYPES.POOL}
      type={COST_EXPLORER}
      breakdown={expenses.breakdown}
      total={pool.total}
      previousTotal={pool.previous_total}
      filteredBreakdown={[pool]}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      isLoading={false}
      onApply={onApply}
      updateFilter={updateFilter}
    />
  );
};

export const basic = () => <Basic />;

export const withoutPieChart = () => <WithoutPieChar />;

export const empty = () => (
  <ExpensesBreakdown
    filterBy={EXPENSES_FILTERBY_TYPES.POOL}
    type={COST_EXPLORER}
    breakdown={{}}
    total={0}
    previousTotal={0}
    filteredBreakdown={[]}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    isLoading={false}
    onApply={onApply}
    updateFilter={updateFilter}
  />
);

export const loading = () => (
  <ExpensesBreakdown
    filterBy={EXPENSES_FILTERBY_TYPES.POOL}
    type={COST_EXPLORER}
    breakdown={{}}
    total={0}
    previousTotal={0}
    filteredBreakdown={[]}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    isLoading
    onApply={onApply}
    updateFilter={updateFilter}
  />
);
