import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import BarChart from "./BarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <BarChart data={[]} keys={[]} fieldTooltipText={[]} />
    </TestProvider>
  );
  root.unmount();
});
