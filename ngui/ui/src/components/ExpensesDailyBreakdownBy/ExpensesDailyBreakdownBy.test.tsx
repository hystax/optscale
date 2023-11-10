import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import { RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY } from "utils/constants";
import ExpensesDailyBreakdownBy from "./ExpensesDailyBreakdownBy";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExpensesDailyBreakdownBy
        breakdown={{}}
        breakdownByValue={RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY.EMPLOYEE_ID}
        onBreakdownByChange={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
