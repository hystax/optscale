import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationsCard from "./RecommendationsCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationsCard possibleMonthlySavings={0} costRecommendationsCount={0} securityRecommendationsCount={0} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
