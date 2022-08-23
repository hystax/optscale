import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import WidgetTitle from "./WidgetTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <WidgetTitle />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
