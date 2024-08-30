import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationAccordionTitle from "./ArchivedRecommendationAccordionTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationAccordionTitle
        titleMessageId="possibleSavingsWithSpotInstancesTitle"
        reason="options_changed"
        count={1}
        archivedAt={1719821794}
      />
    </TestProvider>
  );
  root.unmount();
});
