import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ArchivedRecommendations from "./ArchivedRecommendations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
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
        onTimeRangeChange={vi.fn}
        isChartLoading={false}
        isLoading={false}
        archivedRecommendationsBreakdown={vi.fn}
        onBarChartSelect={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
