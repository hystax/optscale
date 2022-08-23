import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import RecommendationAccordionTitle from "./RecommendationAccordionTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <RecommendationAccordionTitle messages={["1", "2", 3]} />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
