import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CloudExpensesChart from "./CloudExpensesChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CloudExpensesChart cloudAccounts={[]} pool={123} forecast={234} />
    </TestProvider>
  );
  root.unmount();
});
