import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import MlExecutorsBreakdownLineChart from "./MlExecutorsBreakdownLineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <MlExecutorsBreakdownLineChart breakdown={[]} />
    </TestProvider>
  );
  root.unmount();
});
