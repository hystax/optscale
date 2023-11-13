import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RunGoals from "./RunGoals";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RunGoals goals={[]} />
    </TestProvider>
  );
  root.unmount();
});
