import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceGroupedExpensesTable from "./ResourceGroupedExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceGroupedExpensesTable data={[]} />
    </TestProvider>
  );
  root.unmount();
});
