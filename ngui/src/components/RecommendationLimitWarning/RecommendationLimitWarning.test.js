import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationLimitWarning from "./RecommendationLimitWarning";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationLimitWarning limit={4} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
