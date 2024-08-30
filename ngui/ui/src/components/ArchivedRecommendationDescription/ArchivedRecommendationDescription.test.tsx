import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ArchivedRecommendationDescription from "./ArchivedRecommendationDescription";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ArchivedRecommendationDescription reason="options_changed" />
    </TestProvider>
  );
  root.unmount();
});
