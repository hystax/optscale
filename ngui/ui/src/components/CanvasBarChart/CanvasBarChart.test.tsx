import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import CanvasBarChart from "./CanvasBarChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <CanvasBarChart data={[]} keys={[]} />
    </TestProvider>
  );
  root.unmount();
});
