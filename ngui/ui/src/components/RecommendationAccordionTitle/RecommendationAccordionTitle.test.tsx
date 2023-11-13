import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationAccordionTitle from "./RecommendationAccordionTitle";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationAccordionTitle messages={["1", "2", 3]} />
    </TestProvider>
  );
  root.unmount();
});
