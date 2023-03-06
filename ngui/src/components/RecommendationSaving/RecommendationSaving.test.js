import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationSaving from "./RecommendationSaving";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationSaving saving={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
