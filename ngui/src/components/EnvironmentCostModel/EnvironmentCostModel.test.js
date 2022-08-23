import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentCostModel from "./EnvironmentCostModel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentCostModel resourceId={""} hourlyPrice={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
