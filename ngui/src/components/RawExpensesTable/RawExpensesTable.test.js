import React from "react";
import { createRoot } from "react-dom/client";
import { COLUMNS, RAW_EXPENSES } from "reducers/columns";
import TestProvider from "tests/TestProvider";
import RawExpensesTable from "./RawExpensesTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider
      state={{
        [COLUMNS]: {
          [RAW_EXPENSES]: []
        }
      }}
    >
      <RawExpensesTable expenses={[]} />
    </TestProvider>
  );
  root.unmount();
});
