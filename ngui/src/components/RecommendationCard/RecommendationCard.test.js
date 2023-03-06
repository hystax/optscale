import React from "react";
import ReactDOM from "react-dom";
import {
  getEmptyRecommendationsSet,
  getRecommendationInstanceByModuleName
} from "components/MlModelRecommendations/Recommendations";
import TestProvider from "tests/TestProvider";
import RecommendationCard from "./RecommendationCard";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const recommendationInstance = getRecommendationInstanceByModuleName("cross_region_traffic");
  const buildedRecommendation = recommendationInstance.build(getEmptyRecommendationsSet());
  ReactDOM.render(
    <TestProvider>
      <RecommendationCard buildedRecommendation={buildedRecommendation} recommendationInstance={recommendationInstance} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
