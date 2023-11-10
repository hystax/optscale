import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SummaryGrid from "./SummaryGrid";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SummaryGrid summaryData={[]} />
    </TestProvider>
  );
  root.unmount();
});
