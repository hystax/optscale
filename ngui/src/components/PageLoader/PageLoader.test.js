import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import PageLoader from "./PageLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <PageLoader />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
