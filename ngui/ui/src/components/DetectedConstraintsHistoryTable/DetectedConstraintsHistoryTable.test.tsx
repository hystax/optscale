import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import DetectedConstraintsHistoryTable from "./DetectedConstraintsHistoryTable";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <DetectedConstraintsHistoryTable limitHits={[]} constraint={{}} />
    </TestProvider>
  );
  root.unmount();
});
