import { createRoot } from "react-dom/client";
import TestProvider from "tests/TestProvider";
import ResourceMetrics from "./ResourceMetrics";

it("renders without crashing", () => {
  const div = document.createElement("div");
  const root = createRoot(div);
  root.render(
    <TestProvider>
      <ResourceMetrics metrics={{}} />
    </TestProvider>
  );

  root.unmount();
});
