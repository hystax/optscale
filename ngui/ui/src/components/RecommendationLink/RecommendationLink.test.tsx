import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RecommendationLink from "./RecommendationLink";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RecommendationLink>resourceName</RecommendationLink>
    </TestProvider>
  );
  root.unmount();
});
