import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CleanExpensesTable from "./CleanExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CleanExpensesTable expenses={[]} appliedFilters={{}} />
    </TestProvider>
  );
  root.unmount();
});
