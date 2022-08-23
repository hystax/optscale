import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationLink from "./RecommendationLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationLink>resourceName</RecommendationLink>
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
