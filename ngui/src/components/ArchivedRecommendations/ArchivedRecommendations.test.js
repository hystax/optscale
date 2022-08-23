import React from "react";
import ReactDOM from "react-dom";
import TestProvider from "tests/TestProvider";
import ArchivedRecommendations from "./ArchivedRecommendations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  ReactDOM.render(
    <TestProvider>
      <ArchivedRecommendations
        dateRange={{
          startDate: 1652659200,
          endDate: 1653004799
        }}
        archivedRecommendationsChartBreakdown={[]}
        archivedRecommendations={{
          breakdown: []
        }}
        onTimeRangeChange={jest.fn}
        isChartLoading={false}
        isLoading={false}
        archivedRecommendationsBreakdown={jest.fn}
        onBarChartSelect={jest.fn}
      />
    </TestProvider>,
    div
  );
  ReactDOM.unmountComponentAtNode(div);
});
