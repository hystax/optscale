import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import RightsizingCpuUsageHeaderCell from "./RightsizingCpuUsageHeaderCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <RightsizingCpuUsageHeaderCell options={{ days_threshold: 1 }} />
    </TestProvider>
  );
  root.unmount();
});
