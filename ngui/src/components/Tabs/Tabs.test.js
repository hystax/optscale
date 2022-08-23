import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import Tabs from "./Tabs";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <Tabs>[]</Tabs>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
