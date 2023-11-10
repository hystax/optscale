import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ArchivedRecommendationAccordion from "./ArchivedRecommendationAccordion";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ArchivedRecommendationAccordion
        recommendationType="abandoned_instances"
        count={5}
        reason="options_changed"
        archivedAt={1652830013}
        isExpanded={false}
        onChange={vi.fn}
      />
    </TestProvider>
  );
  root.unmount();
});
