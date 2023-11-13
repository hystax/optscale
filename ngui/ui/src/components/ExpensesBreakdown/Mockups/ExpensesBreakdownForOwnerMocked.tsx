import { EXPENSES_FILTERBY_TYPES, COST_EXPLORER } from "utils/constants";
import { getLastWeekRange, addDaysToTimestamp } from "utils/datetime";
import ExpensesBreakdown from "../ExpensesBreakdown";

const ExpensesBreakdownForOwnerMocked = () => {
  const { lastWeekStart: firstDateRangePoint, lastWeekEnd: lastDateRangePoint } = getLastWeekRange(true);

  const breakdown = {
    [firstDateRangePoint]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 1613.2313672838,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 24.639862891499998,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 1280.9187834066,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 936.8585263726,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 77.228119044,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 35.26463332349999,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 24.6338124912,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 1)]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 1366.7838405633004,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 222.8572994751,
        id: "c4c3a518-ab9c-4aba-912c-708cc51d9b5e",
        name: "Oscar Walsh"
      },
      {
        expense: 24.6390672303,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 1168.06019992,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 37.100665025100014,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 24.6462867189,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 1613.4434233713,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 83.489296734,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 2)]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 422.4723890391,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 974.2399681978,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      },
      {
        expense: 24.6378574134,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 27.929266884000004,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 24.641445997800002,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 77.78021599440001,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 1613.1315150162,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 3)]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 29.083829960699994,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 420.2256436632,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 24.651374382,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 1613.2712527926,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 24.643465261200003,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 79.2107590635,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 950.0576681791,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 4)]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 24.6567928158,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 1613.0356802379,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 24.639400433700004,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 85.79208305699999,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 44.339432420700014,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 582.9494233653002,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 194.50590291359998,
        id: "c4c3a518-ab9c-4aba-912c-708cc51d9b5e",
        name: "Oscar Walsh"
      },
      {
        expense: 1028.2403674135,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
      }
    ],
    [addDaysToTimestamp(firstDateRangePoint, 5)]: [
      {
        expense: 180.2017514556,
        id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
        name: "Amy Smith"
      },
      {
        expense: 24.641806221,
        id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
        name: "Aaron Simmons"
      },
      {
        expense: 37.541113392599996,
        id: "29019351-df21-4a3b-84c3-42acb086317b",
        name: "Ella Price"
      },
      {
        expense: 24.640616003399998,
        id: "015c36f9-5c05-4da8-b445-932560a00191",
        name: "Haris Price"
      },
      {
        expense: 81.3030821055,
        id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
        name: "Katy Ali"
      },
      {
        expense: 812.5805639798999,
        id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
        name: "Sally Wong"
      },
      {
        expense: 1612.8339342696,
        id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
        name: "Taylor Everett"
      },
      {
        expense: 969.9197964257,
        id: "00000000-0000-0000-0000-000000000000",
        name: "(not set)"
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
  };

  const filteredBreakdown = [
    {
      total: 9682.389260208,
      previous_total: 12904.245314669699,
      id: "ab9f39d4-d486-429a-814e-9717a1e12ac7",
      name: "Taylor Everett"
    },
    {
      total: 6306.5913048273,
      previous_total: 7008.8069736144325,
      id: "00000000-0000-0000-0000-000000000000",
      name: "(not set)"
    },
    {
      total: 5159.2858133688005,
      previous_total: 5199.219195685199,
      id: "9c458a6d-13b4-47d5-b921-b75ee8bf8101",
      name: "Sally Wong"
    },
    {
      total: 1081.2105087336001,
      previous_total: 1489.5603028008002,
      id: "5153cb97-94e4-403b-ac9a-8f1343f1fbc5",
      name: "Amy Smith"
    },
    {
      total: 541.9071407457,
      previous_total: 559.1013787575,
      id: "8886a4df-37f1-4598-aa92-c39eae9567d4",
      name: "Katy Ali"
    },
    {
      total: 420.1793447463,
      previous_total: 1310.0575567382998,
      id: "c4c3a518-ab9c-4aba-912c-708cc51d9b5e",
      name: "Oscar Walsh"
    },
    {
      total: 242.35626190680006,
      previous_total: 183.1998652812,
      id: "29019351-df21-4a3b-84c3-42acb086317b",
      name: "Ella Price"
    },
    {
      total: 163.2856885272,
      previous_total: 197.1577110465,
      id: "015c36f9-5c05-4da8-b445-932560a00191",
      name: "Haris Price"
    },
    {
      total: 163.2312854604,
      previous_total: 197.1877353687,
      id: "87812acf-48f3-47ce-ac7d-0623ae3405ed",
      name: "Aaron Simmons"
    }
  ];

  return (
    <ExpensesBreakdown
      filterBy={EXPENSES_FILTERBY_TYPES.EMPLOYEE}
      type={COST_EXPLORER}
      breakdown={breakdown}
      total={23760.436608524098}
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

export default ExpensesBreakdownForOwnerMocked;
