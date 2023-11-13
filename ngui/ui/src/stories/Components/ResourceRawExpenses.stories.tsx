import ResourceRawExpenses from "components/ResourceRawExpenses";
import { KINDS } from "stories";
import { millisecondsToSeconds } from "utils/datetime";

const expensesAllWithBothRateAndUnit = [
  {
    start_date: "2020-10-01T15:00:00",
    end_date: "2020-10-01T16:00:00",
    cost: 0.0002731926,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0897913251",
    "pricing/unit": "GB",
    _id: "6048d5866ed6e23aab17e06f"
  },
  {
    start_date: "2020-10-02T15:00:00",
    end_date: "2020-10-02T16:00:00",
    cost: 1,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0897913251",
    "pricing/unit": "GB",
    _id: "6048d5866ed6e23aab17e06f"
  },
  {
    start_date: "2020-10-02T15:00:00",
    end_date: "2020-10-02T16:00:00",
    cost: 2,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0897913251",
    "pricing/unit": "GB",
    _id: "6048d5866ed6e23aab17e06f"
  }
];

export default {
  title: `${KINDS.COMPONENTS}/ResourceRawExpenses`,
  argTypes: {
    expenses: {
      name: "Expenses",
      control: "object",
      defaultValue: expensesAllWithBothRateAndUnit
    }
  }
};

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

export const allWithBothRateAndUnit = () => (
  <ResourceRawExpenses
    expenses={expensesAllWithBothRateAndUnit}
    shownExpenses={1000}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    onApply={() => console.log("Apply")}
  />
);

export const allUnitsAreAbsent = () => (
  <ResourceRawExpenses
    expenses={expensesAllWithBothRateAndUnit.map(({ "lineItem/BlendedRate": _, "pricing/unit": __, ...rest }) => rest)}
    shownExpenses={1000}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    onApply={() => console.log("Apply")}
  />
);

const expensesSomeUnitIsMissing = [
  {
    start_date: "2020-10-01T15:00:00",
    end_date: "2020-10-01T16:00:00",
    cost: 0.0002731926,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0897913251",
    "pricing/unit": "GB",
    _id: "6048d5866ed6e23aab17e06f"
  },
  {
    start_date: "2020-10-02T15:00:00",
    end_date: "2020-10-02T16:00:00",
    cost: 1,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    "lineItem/BlendedRate": "0.0897913251",
    "pricing/unit": "GB",
    _id: "6048d5866ed6e23aab17e06f"
  },
  {
    start_date: "2020-10-02T15:00:00",
    end_date: "2020-10-02T16:00:00",
    cost: 2,
    "lineItem/LineItemDescription": "$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier",
    _id: "6048d5866ed6e23aab17e06f"
  }
];

export const someUnitIsMissing = () => (
  <>
    <div>
      Missing parts of <strong>$0.090 per GB - first 10 TB / month data transfer out beyond the global free tier:</strong>
      <ul>
        <li>"lineItem/BlendedRate": "0.0897913251"</li>
        <li>"pricing/unit": "GB"</li>
      </ul>
      <p>
        This row will be skipped in the unit expenses calculations, but will be used to calculate the total amount of expenses
      </p>
      <p>
        NOTE: ResourceRawExpenses component doesn't calculate total expenses (it received it via props) - "Expenses:{" "}
        <strong>$1,000</strong>" is a hardcoded label
      </p>
    </div>
    <ResourceRawExpenses
      expenses={expensesSomeUnitIsMissing}
      shownExpenses={1000}
      startDateTimestamp={firstDateRangePoint}
      endDateTimestamp={lastDateRangePoint}
      onApply={() => console.log("Apply")}
    />
  </>
);

export const withDynamicData = (args) => (
  <ResourceRawExpenses
    expenses={args.expenses}
    shownExpenses={1000}
    startDateTimestamp={firstDateRangePoint}
    endDateTimestamp={lastDateRangePoint}
    onApply={() => console.log("Apply")}
  />
);
