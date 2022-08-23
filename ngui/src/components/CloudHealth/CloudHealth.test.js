import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import CloudHealth from "./CloudHealth";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <CloudHealth isLoading />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
