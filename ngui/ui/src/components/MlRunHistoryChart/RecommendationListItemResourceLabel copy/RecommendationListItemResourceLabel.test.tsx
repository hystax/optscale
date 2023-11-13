import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationListItemResourceLabel from "./RecommendationListItemResourceLabel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationListItemResourceLabel />
    </TestProvider>
  );
  root.unmount();
});
