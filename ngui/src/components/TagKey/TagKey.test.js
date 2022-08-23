import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import TagKey from "./TagKey";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <TagKey tagKey="key" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
