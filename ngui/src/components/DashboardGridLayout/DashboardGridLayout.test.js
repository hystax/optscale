import React from "react";
import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DashboardGridLayout from "./DashboardGridLayout";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DashboardGridLayout
        topResourcesExpensesCard={null}
        environmentsCard={null}
        organizationExpenses={null}
        recommendationsCard={null}
      />
    </TestProvider>
  );
  root.unmount();
});
