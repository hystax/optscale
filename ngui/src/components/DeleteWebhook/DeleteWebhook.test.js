import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import DeleteWebhook from "./DeleteWebhook";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <DeleteWebhook />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
