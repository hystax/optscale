import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationSettings from "./RecommendationSettings";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationSettings
        options={{}}
        backendRecommendationType="type"
        availablePools={[]}
        withExclusions
        withThresholds
        withRightsizingStrategy
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
