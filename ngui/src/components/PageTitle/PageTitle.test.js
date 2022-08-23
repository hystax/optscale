import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PageTitle from "./PageTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PageTitle />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
