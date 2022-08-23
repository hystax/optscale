import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DashboardGridLayout from "./DashboardGridLayout";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DashboardGridLayout
        topResourcesExpensesCard={null}
        environmentsCard={null}
        organizationExpenses={null}
        recommendationsCard={null}
        myTasksCard={null}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
