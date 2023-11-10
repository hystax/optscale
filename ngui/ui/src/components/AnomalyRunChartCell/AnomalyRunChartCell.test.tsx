import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import AnomalyRunChartCell from "./AnomalyRunChartCell";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <AnomalyRunChartCell breakdown={{}} today={0} average={0} threshold={0} type={"type"} />
    </TestProvider>
  );
  root.unmount();
});
