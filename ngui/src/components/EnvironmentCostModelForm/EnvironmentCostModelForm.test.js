import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentCostModelForm from "./EnvironmentCostModelForm";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentCostModelForm onSubmit={jest.fn} onCancel={jest.fn} defaultHourlyPrice={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
