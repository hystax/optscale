import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import HeaderHelperCell from "./HeaderHelperCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <HeaderHelperCell titleMessageId="name" helperMessageId="name" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
