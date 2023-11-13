import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import SummaryCardContent from "./SummaryCardContent";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <SummaryCardContent />
    </TestProvider>
  );
  root.unmount();
});
