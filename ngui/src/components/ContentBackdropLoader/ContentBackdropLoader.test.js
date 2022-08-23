import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ContentBackdropLoader from "./ContentBackdropLoader";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ContentBackdropLoader />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
