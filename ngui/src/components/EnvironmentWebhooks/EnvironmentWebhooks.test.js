import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentWebhooks from "./EnvironmentWebhooks";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentWebhooks webhooks={[]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
