import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import EnvironmentBookings from "./EnvironmentBookings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <EnvironmentBookings resourceId="123" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
