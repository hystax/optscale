import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LastModelRunGoals from "./LastModelRunGoals";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LastModelRunGoals modelGoals={[]} lastRunGoals={[]} />
    </TestProvider>
  );
  root.unmount();
});
