import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ArchivedRecommendationAccordion from "./ArchivedRecommendationAccordion";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ArchivedRecommendationAccordion
        recommendationType="abandoned_instances"
        count={5}
        reason="options_changed"
        archivedAt={1652830013}
        isExpanded={false}
        onChange={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
