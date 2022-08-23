import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PaidNetworkTrafficLabel from "./PaidNetworkTrafficLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PaidNetworkTrafficLabel />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
