import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CreateEnvironmentProperties from "./CreateEnvironmentProperties";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CreateEnvironmentProperties environmentId="" existingProperties={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
