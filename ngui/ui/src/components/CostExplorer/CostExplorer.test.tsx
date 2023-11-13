import { createRoot } from "react-dom/client";
import { EXPENSES_BREAKDOWN_PERIOD_TYPE } from "components/ExpensesBreakdown/BreakdownByPeriodWidget/reducer";
import TestProvider from "tests/TestProvider";
import { EXPENSES_SPLIT_PERIODS } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import CostExplorer from "./CostExplorer";

const firstDateRangePoint = millisecondsToSeconds(+new Date());
const lastDateRangePoint = millisecondsToSeconds(+new Date());

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        rangeDates: {},
        [EXPENSES_BREAKDOWN_PERIOD_TYPE]: EXPENSES_SPLIT_PERIODS.DAILY
      }}
    >
      <CostExplorer
        total={1000}
        previousTotal={500}
        breakdown={{}}
        organizationName="org"
        isLoading={false}
        onApply={vi.fn}
        startDateTimestamp={firstDateRangePoint}
        endDateTimestamp={lastDateRangePoint}
      />
    </TestProvider>
  );
  root.unmount();
});
