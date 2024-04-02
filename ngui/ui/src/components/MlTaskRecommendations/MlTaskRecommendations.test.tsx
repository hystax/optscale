import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlTaskRecommendations from "./MlTaskRecommendations";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlTaskRecommendations recommendations={{}} />
    </TestProvider>
  );
  root.unmount();
});
