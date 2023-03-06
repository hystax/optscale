import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { ML_EXECUTORS_DAILY_BREAKDOWN_BY } from "utils/constants";
import MlExecutorsBreakdown from "./MlExecutorsBreakdown";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <MlExecutorsBreakdown breakdown={[]} breakdownBy={ML_EXECUTORS_DAILY_BREAKDOWN_BY.CPU} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
