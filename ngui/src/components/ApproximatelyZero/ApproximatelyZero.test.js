import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ApproximatelyZero from "./ApproximatelyZero";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ApproximatelyZero />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
