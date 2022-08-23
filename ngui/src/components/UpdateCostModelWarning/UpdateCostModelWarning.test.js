import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import { COST_MODEL_TYPES } from "utils/constants";
import UpdateCostModelWarning from "./UpdateCostModelWarning";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <UpdateCostModelWarning costModelType={COST_MODEL_TYPES.K8S} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
