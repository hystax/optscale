import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Integrations from "./Integrations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider state={{ organizationId: "organizationId" }}>
      <Integrations />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
