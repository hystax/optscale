import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import NavigateAppBarLabel from "./NavigateAppBarLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <NavigateAppBarLabel to="/" label="Give me you battle roar" />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
