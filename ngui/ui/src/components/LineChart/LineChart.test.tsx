import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import LineChart from "./LineChart";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <LineChart data={[]} />
    </TestProvider>
  );
  root.unmount();
});
