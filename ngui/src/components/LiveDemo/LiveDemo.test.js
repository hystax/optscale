import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import LiveDemo from "./LiveDemo";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <LiveDemo isLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
