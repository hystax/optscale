import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ExecutorsPanel from "./ExecutorsPanel";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ExecutorsPanel />
    </TestProvider>
  );
  root.unmount();
});
