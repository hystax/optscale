import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentProperties from "./EnvironmentProperties";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentProperties environmentId="id" properties={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
