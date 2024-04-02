import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LastTaskRunGoals from "./LastTaskRunGoals";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LastTaskRunGoals taskReachedGoals={[]} lastRunMetrics={[]} />
    </TestProvider>
  );
  root.unmount();
});
