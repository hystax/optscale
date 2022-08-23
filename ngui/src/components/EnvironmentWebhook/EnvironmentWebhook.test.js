import React from "react";
import ReactDOM from "react-dom";
import { BOOKING_ACQUIRE } from "services/WebhooksService";
import TestProvider from "tests/TestProvider";
import EnvironmentWebhook from "./EnvironmentWebhook";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentWebhook webhook={{}} resourceId="" action={BOOKING_ACQUIRE} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
