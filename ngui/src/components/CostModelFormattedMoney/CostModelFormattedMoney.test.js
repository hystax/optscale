import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CostModelFormattedMoney from "./CostModelFormattedMoney";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CostModelFormattedMoney value={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
