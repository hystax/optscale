import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentProperty from "./EnvironmentProperty";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentProperty environmentId="" propertyName="" propertyValue="" existingProperties={{}} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
