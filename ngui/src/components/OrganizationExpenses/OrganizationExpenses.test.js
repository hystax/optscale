import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import OrganizationExpenses from "./OrganizationExpenses";

const data = {
  employee_id: "d57dfaaf-7a37-4ad7-9298-de71b40c8748",
  pool_id: "d66bcc27-7d0e-4d45-9f3d-1874cc736284",
  expenses: {
    last_month: {
      total: 60,
      date: 1585688400 // timestamp of last day of last month
    },
    this_month: {
      total: 45,
      date: 1585697200 // today's timestamp
    },
    this_month_forecast: {
      total: 55,
      date: 1585715100 // timestamp of last day of this month
    }
  }
};

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <OrganizationExpenses data={data} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
